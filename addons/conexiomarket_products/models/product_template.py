from odoo import models, api, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)
        self._notify_marketplaces('write')
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._notify_marketplaces('create')
        return records

    def unlink(self):
        for record in self:
             record._notify_marketplaces('unlink')
        return super().unlink()

    def _notify_marketplaces(self, event_type):
        """ Busca cuentas donde este producto esté mapeado y encola eventos """
        if not self:
            return

        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1).id
        EventQueue = self.env['market.event.queue'].sudo()
        Mapping = self.env['market.product.mapping'].sudo()
        
        for record in self:
            mappings = Mapping.search([
                ('product_tmpl_id', '=', record.id),
                ('account_id.is_active', '=', True)
            ])
             
            for mapping in mappings:
                # Debounce: Si ya hay un evento pendiente para este registro y cuenta, no creamos otro.
                domain = [
                   ('model_id', '=', model_id),
                   ('res_id', '=', record.id),
                   ('account_id', '=', mapping.account_id.id),
                   ('state', '=', 'pending') 
                ]
                existing = EventQueue.search(domain, limit=1)
                
                if not existing:
                    EventQueue.create({
                       'account_id': mapping.account_id.id,
                       'model_id': model_id,
                       'res_id': record.id,
                       'event_type': event_type,
                       'state': 'pending',
                       'priority': 10 if event_type == 'write' else 20 # Create/Unlink prioridad mayor
                    })