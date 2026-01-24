import json
import traceback
from odoo import models, fields, api, tools
import logging

_logger = logging.getLogger(__name__)

class MarketWebhookEntry(models.Model):
    _name = "market.webhook.entry"
    _description = "Webhook Entry"
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Referencia",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: 'New'
    )
    account_id = fields.Many2one(
        "market.account",
        string="Cuenta",
        required=True,
        index=True,
        ondelete="cascade",
        help="Cuenta de marketplace asociada a este webhook"
    )
    company_id = fields.Many2one(
        related='account_id.company_id',
        string='Empresa',
        store=True,
        readonly=True,
        index=True
    )
    backend_type = fields.Selection(
        related="account_id.backend_type",
        store=True,
        string="Backend Type"
    )
    state = fields.Selection(
        [
            ("draft", "Pendiente"),
            ("processing", "Procesando"),
            ("done", "Procesado"),
            ("failed", "Fallido"),
        ],
        string="Estado",
        default="draft",
        required=True,
        index=True,
        tracking=True
    )
    payload = fields.Text(
        string="Payload (JSON)",
        required=True,
        help="Contenido crudo del webhook"
    )
    headers = fields.Text(
        string="Headers",
        help="Cabeceras HTTP de la petición"
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Modelo Destino",
        help="Modelo de Odoo asociado (ej. sale.order)",
        index=True,
        ondelete="set null"
    )
    res_id = fields.Integer(
        string="ID Registro",
        help="ID del registro Odoo creado/actualizado",
        index=True,
        readonly=True
    )
    retry_count = fields.Integer(
        string="Reintentos",
        default=0
    )

    def action_view_record(self):
        self.ensure_one()
        if not self.model_id or not self.res_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registro Relacionado',
            'res_model': self.model_id.sudo().model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('market.webhook.entry') or 'New'
        
        records = super().create(vals_list)
        
        for record in records:
            if record.account_id and record.account_id.message_partner_ids:
                record.message_subscribe(partner_ids=record.account_id.message_partner_ids.ids)
                
        return records

    def action_retry(self):
        for entry in self:
            entry.write({
                'state': 'draft',
                'retry_count': entry.retry_count + 1
            })

    def action_process(self):
        """ Método stub para ser extendido por los módulos de dominio """
        for entry in self:
            entry.write({'state': 'processing'})

            payload = json.loads(entry.payload)
            account = entry.account_id

            try:
                _logger.info(f"Iniciando procesamiento de webhook {entry.name} para el modelo {entry.model_id.model}")
                with self.env.cr.savepoint():
                    with account.work_on(entry.model_id.model) as work:
                        importer = work.component(usage="importer")
                        record = importer.run(payload)

                        if record:
                            entry.write({'res_id': record.id})

                            if 'marketplace_webhook_id' in record._fields:
                                record.write({
                                    'marketplace_webhook_id': entry.id
                                })
                        
            except Exception as e:
                _logger.exception(f"Falló procesamiento de webhook {entry.name} para el modelo {entry.model_id.model}")
                escaped_tb = tools.html_escape(traceback.format_exc()[:5000])
                
                post_body = f"<p>Falló procesamiento de webhook {entry.name} para el modelo {entry.model_id.model}.</p><pre>{escaped_tb}</pre>"
                entry.message_post(
                    body=post_body,
                    body_is_html=True,
                    subtype_id=self.env.ref("conexiomarket_core.mail_message_subtype_webhook_failed").id
                )
                entry.write({
                    'state': 'failed',
                })

            else:
                _logger.info(f"Completada procesamiento de webhook {entry.name} para el modelo {entry.model_id.model}")
                post_body = f"<p>Procesamiento de webhook {entry.name} para el modelo {entry.model_id.model} completado con éxito.</p>"
                entry.message_post(body=post_body, body_is_html=True)
                entry.write({
                    'state': 'done',
                })

    @api.model
    def process_batch(self, limit=50):
        """ Procesa un lote de webhooks pendientes """
        entries = self.search([('state', '=', 'draft')], limit=limit, order='id asc')
        if entries:
            entries.action_process()
