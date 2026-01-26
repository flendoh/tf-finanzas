from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    marketplace_account_id = fields.Many2one("market.account", string="Cuenta Marketplace", readonly=True, index=True, help="Cuenta del marketplace desde donde se originó esta orden de venta")
    marketplace_external_id = fields.Char(string="ID Externo", index=True, readonly=True, help="ID único de la orden en el marketplace externo")
    marketplace_date_order = fields.Datetime(string="Fecha de Orden", readonly=True, help="Fecha y hora cuando se creó la orden en el marketplace")
    marketplace_shipping_deadline = fields.Datetime(string="Fecha Límite Envío", readonly=True, help="Fecha límite de envío establecida por el marketplace")
    marketplace_order_number = fields.Char(string="Número de Orden (N°)", readonly=True, help="Número de orden del marketplace", index=True)
    marketplace_invoice_required = fields.Boolean(string="Requiere Factura", default=False, readonly=True, help="Indica si la orden del marketplace requiere factura")
    marketplace_webhook_ids = fields.One2many(
        "market.webhook.entry",
        "res_id",
        string="Entradas Webhook",
        readonly=True,
        help="Webhooks que originaron esta orden",
        groups="conexiomarket_core.group_market_connector_user",
    )
    marketplace_last_raw_data = fields.Text(string="Raw Data", readonly=True, help="Data recibido del marketplace para esta orden", groups="conexiomarket_core.group_market_connector_manager")
    
    marketplace_last_webhook_id = fields.Many2one(
        "market.webhook.entry",
        string="Último Webhook",
        readonly=True,
        help="Webhook que originó esta orden",
        groups="conexiomarket_core.group_market_connector_user",
        ondelete="set null"
    )

    marketplace_webhook_count = fields.Integer(string="Cantidad Webhooks", compute="_compute_marketplace_webhook_count")

    # Features
    feature_order_document = fields.Boolean(related="marketplace_account_id.feature_order_document", string="Soporta Documento", default=False, readonly=True, help="Indica si la cuenta de marketplace soporta la obtención de documentos de la orden")
    feature_open_marketplace_url = fields.Boolean(related="marketplace_account_id.feature_open_marketplace_url", string="Soporta URL de Orden", default=False, readonly=True, help="Indica si la cuenta de marketplace soporta redirigir a la URL de la orden")

    _sql_constraints = [
        ('marketplace_external_id_account_unique', 'UNIQUE(marketplace_account_id, marketplace_external_id)', 'El ID externo debe ser único por cuenta de marketplace')
    ]

    @api.depends('marketplace_webhook_ids')
    def _compute_marketplace_webhook_count(self):
        for order in self:
            order.marketplace_webhook_count = len(order.marketplace_webhook_ids)

    def action_view_webhooks(self):
        self.ensure_one()
        return {
            'name': _('Webhooks'),
            'type': 'ir.actions.act_window',
            'res_model': 'market.webhook.entry',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.marketplace_webhook_ids.ids)],
        }

    def action_get_marketplace_document(self):
        """ Action to retrieve document from marketplace """
        self.ensure_one()
        if not self.marketplace_account_id.feature_order_document:
            raise ValidationError(_("Esta cuenta no soporta la obtención de documentos."))
        
        with self.marketplace_account_id.work_on(self._name) as work:
            importer = work.component(usage="document.importer")
            importer.run(self)
        
        return True

    def action_open_marketplace_url(self):
        """ Open marketplace order URL in a new tab """
        self.ensure_one()
        if not self.feature_open_marketplace_url:
            raise ValidationError(_("Esta cuenta no soporta la redirección a la orden."))
        
        url = False
        with self.marketplace_account_id.work_on(self._name) as work:
            retriever = work.component(usage="url.retriever")
            url = retriever.run(self)
        
        if not url:
            raise UserError(_("No se pudo obtener la URL de la orden."))

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }