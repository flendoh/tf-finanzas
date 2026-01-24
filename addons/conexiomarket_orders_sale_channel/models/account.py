from odoo import fields, models


class MarketAccount(models.Model):
    _inherit = "market.account"

    sale_channel_id = fields.Many2one(
        "sale.channel",
        string="Canal de venta",
        ondelete="restrict",
        check_company=True,
    )

