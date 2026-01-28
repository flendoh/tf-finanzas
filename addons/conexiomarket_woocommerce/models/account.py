from odoo import models, fields

class MarketAccount(models.Model):
    _inherit = 'market.account'

    backend_type = fields.Selection(selection_add=[('woocommerce', 'WooCommerce')], ondelete={'woocommerce': 'cascade'})

    woocommerce_url = fields.Char(
        string="URL WooCommerce",
        help="URL de la tienda WooCommerce",
        groups="conexiomarket_core.group_market_connector_admin"
    )