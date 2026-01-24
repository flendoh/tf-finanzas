from odoo import models, api, fields


class MarketProductMapping(models.Model):
    _name = "market.product.mapping"
    _description = "Mapeo entre IDs de marketplace y productos de Odoo"
    _rec_name = "external_id"

    account_id = fields.Many2one("market.account", string="Cuenta", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        related='account_id.company_id',
        string='Empresa',
        store=True,
        readonly=True,
        index=True
    )
    external_id = fields.Char(string="ID Externo", required=True, index=True)
    product_id = fields.Many2one("product.template", string="Producto", required=True, index=True, ondelete="restrict")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ("uniq_account_product", "unique(account_id, product_id)", "Cada producto solo puede estar mapeado una vez por cuenta."),
        ("uniq_account_external", "unique(account_id, external_id)", "El ID externo debe ser único por cuenta.")
    ]