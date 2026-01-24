from contextlib import contextmanager
from odoo import models, fields, api, tools
import logging
import traceback

_logger = logging.getLogger(__name__)

class MarketAccount(models.Model):
    _name = "market.account"
    _description = "Marketplace Account"
    _check_company_auto = True
    _inherit = ['collection.base', 'mail.thread']

    name = fields.Char(
        string="Nombre de cuenta",
        help="Nombre identificativo de la cuenta del marketplace",
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Empresa",
        help="Empresa específica para esta configuración.",
        required=True,
        default=lambda self: self.env.company
    )
    backend_type = fields.Selection(
        selection=[],
        string="Backend",
        help="Tipo de backend del marketplace (Amazon, MercadoLibre, etc.)",
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string="Vendedor",
        help="Vendedor responsable de la cuenta.",
        required=True,
        tracking=True,
        default=lambda self: self.env.user
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string='Almacén',
        help='Almacén asociado a esta cuenta de marketplace',
        check_company=True,
        required=True
    )
    is_active = fields.Boolean(
        string="Activo",
        help="Indica si la cuenta del marketplace está activa y operativa",
        default=True
    )
    product_mapping_ids = fields.One2many(
        "market.product.mapping",
        "account_id",
        string="Mapeos de Productos",
        help="Mapeos entre productos de Odoo y IDs externos del marketplace"
    )
    mapping_count = fields.Integer(
        string='Mapeos de Productos',
        compute='_compute_mapping_count'
    )
    webhook_ids = fields.One2many(
        "market.webhook.entry",
        "account_id",
        string="Webhooks"
    )
    event_queue_ids = fields.One2many(
        "market.event.queue",
        "account_id",
        string="Eventos Salientes"
    )
    webhook_count = fields.Integer(
        string='Webhooks',
        compute='_compute_webhook_count'
    )
    event_queue_count = fields.Integer(
        string='Eventos Salientes',
        compute='_compute_event_queue_count'
    )

    def _compute_features(self):
        """ Compute supported features based on backend type. """
        for account in self:
            account.feature_order_document = False

    @api.depends('product_mapping_ids')
    def _compute_mapping_count(self):
        for account in self:
            account.mapping_count = len(account.product_mapping_ids)

    @api.depends('webhook_ids')
    def _compute_webhook_count(self):
        for account in self:
            account.webhook_count = len(account.webhook_ids)

    @api.depends('event_queue_ids')
    def _compute_event_queue_count(self):
        for account in self:
            account.event_queue_count = len(account.event_queue_ids)

    def action_view_webhooks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Webhooks',
            'res_model': 'market.webhook.entry',
            'view_mode': 'list,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id}
        }

    def action_view_events(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Eventos Salientes',
            'res_model': 'market.event.queue',
            'view_mode': 'list,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id}
        }

    @contextmanager
    def log_operation(self, operation_name="sin nombre"):
        """Log a operation result."""
        external_id = self.env.context.get("external_id")
        with_raise = self.env.context.get("with_raise", False)

        log_msg_base = f"Operación '{operation_name}' en la cuenta '{self.name}'"
        if external_id:
            log_msg_base += f" para el ID externo '{external_id}'"

        try:
            _logger.info(f"Iniciando {log_msg_base}")
            with self.env.cr.savepoint():
                yield
        except Exception as e:
            _logger.exception(f"Falló {log_msg_base}")
            escaped_tb = tools.html_escape(traceback.format_exc()[:5000])

            post_body = f"<p>Falló {log_msg_base}.</p><pre>{escaped_tb}</pre>"
            self.message_post(body=post_body, body_is_html=True)

            if with_raise:
                raise e
        else:
            _logger.info(f"Completada {log_msg_base}")
            post_body = f"<p>{log_msg_base} completada con éxito.</p>"
            self.message_post(body=post_body, body_is_html=True)
