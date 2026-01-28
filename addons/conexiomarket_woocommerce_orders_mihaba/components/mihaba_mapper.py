from typing import Any
from odoo.addons.component.core import Component

class MihabaWooCommerceMapper(Component):
    _inherit = "woocommerce.market.mapper"
    
    def map_create_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the order data to the Odoo format (Mihaba Customization) """
        vals: dict[str, Any] = super().map_create_order(order_data)
        
        meta_data = order_data.get('meta_data', [])
        
        utm_source_val = self._get_meta_value(meta_data, '_wc_order_attribution_utm_source')
        utm_medium_val = self._get_meta_value(meta_data, '_wc_order_attribution_utm_medium')
        invoice_required = self._get_meta_value(meta_data, '_billing_tipo_de_comprobante_') == 'Si'

        if utm_source_val:
            if isinstance(utm_source_val, str):
                utm_source_val = utm_source_val.strip()
            
            if utm_source_val:
                source = self.env['utm.source'].search([('name', 'ilike', utm_source_val)], limit=1)
                if not source:
                    source = self.env['utm.source'].create({'name': utm_source_val})

                vals.update({'source_id': source.id})
            
        if utm_medium_val:
            if isinstance(utm_medium_val, str):
                utm_medium_val = utm_medium_val.strip()
            
            if utm_medium_val:
                medium = self.env['utm.medium'].search([('name', 'ilike', utm_medium_val)], limit=1)
                if not medium:
                    medium = self.env['utm.medium'].create({'name': utm_medium_val})
                
                vals.update({'medium_id': medium.id})
        
        if invoice_required:
            vals.update({'marketplace_invoice_required': True})
        
        return vals
    
    def map_create_partner(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the partner data to the Odoo format (Mihaba Customization) """
        vals: dict[str, Any] = super().map_create_partner(order_data)
        
        meta_data = order_data.get('meta_data', [])
        vat = self._get_meta_value(meta_data, '_billing_dni_ruc')
        
        if vat and vals.get('partner'):
            if isinstance(vat, str):
                vat = vat.strip()
            
            if vat:
                vals.update({'partner':{'vat': vat}})
                
        return vals

    def _get_meta_value(self, meta_data, key):
        for item in meta_data:
            if item.get('key') == key:
                return item.get('value')
        return False