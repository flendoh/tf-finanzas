from odoo import models, fields

class MarketAccount(models.Model):
    _inherit = 'market.account'

    backend_type = fields.Selection(selection_add=[('falabella', 'Falabella')], ondelete={'falabella': 'cascade'})

    falabella_base_url = fields.Char(
        string="URL Base Falabella",
        help="URL base de la API de Falabella",
        readonly=True,
        default="https://sellercenter-api.falabella.com/",
        groups="conexiomarket_core.group_market_connector_manager"
    )

    falabella_api_key = fields.Char(
        string="Clave API Falabella",
        help="Clave API para autenticación en la API de Falabella",
        groups="conexiomarket_core.group_market_connector_manager"
    )

    falabella_user_id = fields.Char(
        string="ID de Usuario Falabella",
        help="ID de usuario para autenticación en la API de Falabella",
        groups="conexiomarket_core.group_market_connector_manager"
    )

    falabella_seller_id = fields.Char(
        string="ID de Vendedor Falabella",
        help="ID de vendedor para autenticación en la API de Falabella",
        groups="conexiomarket_core.group_market_connector_manager"
    )

    def _compute_features(self):
        super()._compute_features()
        for account in self:
            if account.backend_type == 'falabella':
                account.feature_order_document = True