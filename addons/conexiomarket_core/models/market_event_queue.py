import traceback
from odoo import models, fields, api, tools
from contextlib import contextmanager
import logging

_logger = logging.getLogger(__name__)

class MarketEventQueue(models.Model):
    _name = "market.event.queue"
    _description = "Cola de Eventos de Salida"
    _order = "priority desc, id asc"
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
        ondelete="cascade"
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
            ("pending", "Pendiente"),
            ("processing", "En Proceso"),
            ("done", "Enviado"),
            ("failed", "Fallido"),
        ],
        string="Estado",
        default="pending",
        required=True,
        index=True,
        tracking=True
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Modelo Odoo",
        required=True,
        ondelete="cascade"
    )
    res_id = fields.Integer(
        string="ID Registro",
        required=True,
        index=True
    )
    record_ref = fields.Char(
        string="Referencia Registro",
        compute="_compute_record_ref"
    )
    event_type = fields.Selection(
        [
            ("create", "Creación"),
            ("write", "Actualización"),
            ("unlink", "Eliminación"),
            ("action", "Acción Personalizada"),
        ],
        string="Tipo Evento",
        required=True,
        default="write"
    )
    priority = fields.Integer(
        string="Prioridad",
        default=10,
        help="Mayor número = Mayor prioridad"
    )
    payload = fields.Text(
        string="Datos a Enviar",
        help="JSON pre-calculado (opcional)"
    )
    log_notes = fields.Text(
        string="Logs de Salida"
    )
    retry_count = fields.Integer(
        string="Reintentos",
        default=0
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('market.event.queue') or 'New'
        
        records = super().create(vals_list)

        subtype_ids = [self.env.ref('mail.mt_comment').id, self.env.ref('mail.mt_note').id]

        for record in records:
            user_id = record.account_id.user_id
            if user_id and user_id.partner_id:
                record.message_subscribe(partner_ids=[user_id.partner_id.id], subtype_ids=subtype_ids)

        return records

    def _compute_record_ref(self):
        for rec in self:
            if rec.model_id and rec.res_id:
                record = self.env[rec.model_id.model].browse(rec.res_id)
                rec.record_ref = record.display_name if record.exists() else f"Eliminado ({rec.res_id})"
            else:
                rec.record_ref = False

    def action_retry(self):
        self.write({'state': 'pending', 'log_notes': False})

    def action_process(self):
        """ Método stub para ser extendido """
        # Implementación base vacía
        pass

    @api.model
    def process_batch(self, limit=50):
        """ Procesa un lote de eventos pendientes """
        entries = self.search([('state', '=', 'pending')], limit=limit, order='priority desc, id asc')
        if entries:
            entries.action_process()
    
    @contextmanager
    def log_operation(self, operation_name="sin nombre"):
        """Log a operation result."""

        log_msg_base = f"Operación '{operation_name}' en la cuenta '{self.name}'"

        try:
            _logger.info(f"Iniciando {log_msg_base}")
            with self.env.cr.savepoint():
                yield
        except Exception as e:
            _logger.exception(f"Falló {log_msg_base}")
            escaped_tb = tools.html_escape(traceback.format_exc()[:5000])

            post_body = f"<p>Falló {log_msg_base}.</p><pre>{escaped_tb}</pre>"
            self.message_post(body=post_body, body_is_html=True)

        else:
            _logger.info(f"Completada {log_msg_base}")
            post_body = f"<p>{log_msg_base} completada con éxito.</p>"
            self.message_post(body=post_body, body_is_html=True)