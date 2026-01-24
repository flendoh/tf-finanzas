from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def action_view_product_mappings(self):
        """Abrir vista de mapeos para este template"""
        self.ensure_one()
        return {
            'name': 'Mapeos de Marketplace',
            'type': 'ir.actions.act_window',
            'res_model': 'market.product.mapping',
            'view_mode': 'list,form',
            'context': {
                'default_product_id': self.product_tmpl_id.id,
                'default_external_id': self.default_code,
            },
            'domain': [('product_id', '=', self.product_tmpl_id.id)],
            'target': 'current',
            'help': 'Configure en qué marketplaces está disponible este producto'
        }