from odoo import models, fields

class MarketAccount(models.Model):
    _inherit = 'market.account'

    backend_type = fields.Selection(selection_add=[('woocommerce', 'WooCommerce')], ondelete={'woocommerce': 'cascade'})
