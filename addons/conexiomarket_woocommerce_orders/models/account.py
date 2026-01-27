from odoo import models

class MarketAccount(models.Model):
    _inherit = 'market.account'

    def _compute_features(self):
        super()._compute_features()
        for account in self:
            if account.backend_type == 'woocommerce':
                account.feature_order_document = False
                account.feature_open_marketplace_url = True
