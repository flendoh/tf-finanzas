from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    marketplace_account_id = fields.Many2one("market.account", string="Cuenta Marketplace", readonly=True, index=True, help="Cuenta del marketplace desde donde se originó esta orden de venta", related="marketplace_webhook_id.account_id")
    marketplace_external_id = fields.Char(string="ID Externo", index=True, readonly=True, help="ID único de la orden en el marketplace externo")
    marketplace_date_order = fields.Datetime(string="Fecha de Orden", readonly=True, help="Fecha y hora cuando se creó la orden en el marketplace")
    marketplace_shipping_deadline = fields.Datetime(string="Fecha Límite Envío", readonly=True, help="Fecha límite de envío establecida por el marketplace")
    marketplace_order_number = fields.Char(string="Número de Orden (N°)", readonly=True, help="Número de orden del marketplace", index=True)
    marketplace_invoice_required = fields.Boolean(string="Requiere Factura", default=False, readonly=True, help="Indica si la orden del marketplace requiere factura")
    marketplace_webhook_id = fields.Many2one(
        "market.webhook.entry",
        string="Entrada Webhook",
        readonly=True,
        help="Webhook que originó esta orden",
        groups="conexiomarket_core.group_market_connector_user",
        ondelete="set null"
    )
    marketplace_raw_data = fields.Text(string="Raw Data", readonly=True, help="Data recibido del marketplace para esta orden", groups="conexiomarket_core.group_market_connector_manager")

    # Features
    feature_order_document = fields.Boolean(related="marketplace_account_id.feature_order_document", string="Soporte Documento", default=False, readonly=True, help="Indica si la cuenta de marketplace soporta la obtención de documentos de la orden")

    _sql_constraints = [
        ('marketplace_external_id_account_unique', 'UNIQUE(marketplace_account_id, marketplace_external_id)', 'El ID externo debe ser único por cuenta de marketplace')
    ]

    def action_get_marketplace_document(self):
        """ Action to retrieve document from marketplace """
        self.ensure_one()
        if not self.marketplace_account_id.feature_order_document:
            raise ValidationError(_("Esta cuenta no soporta la obtención de documentos."))
        
        with self.marketplace_account_id.work_on(self._name) as work:
            importer = work.component(usage="document.importer")
            importer.run(self)
        
        return True