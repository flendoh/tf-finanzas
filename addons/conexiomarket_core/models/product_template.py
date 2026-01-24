from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    mapping_ids = fields.One2many(
        'market.product.mapping', 
        'product_id',
        string='Mapeos de Marketplace',
        groups='conexiomarket_core.group_market_connector_user'
    )
    
    mapping_count = fields.Integer(
        string='Mapeos de Marketplace',
        compute='_compute_mapping_count',
        groups='conexiomarket_core.group_market_connector_user'
    )
    
    @api.depends('mapping_ids')
    def _compute_mapping_count(self):
        for template in self:
            template.mapping_count = len(template.mapping_ids)
    
    def action_view_product_mappings(self):
        """Abrir vista de mapeos para este template"""
        self.ensure_one()
        return {
            'name': 'Mapeos de Marketplace',
            'type': 'ir.actions.act_window',
            'res_model': 'market.product.mapping',
            'view_mode': 'list,form',
            'context': {
                'default_product_id': self.id,
                'default_external_id': self.default_code,
            },
            'domain': [('product_id', '=', self.id)],
            'target': 'current',
            'help': 'Configure en qué marketplaces está disponible este producto'
        }