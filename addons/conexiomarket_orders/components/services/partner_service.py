from odoo import _
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderPartnerService(Component):
    _name = "market.order.partner.service"
    _collection = "market.account"
    _usage = "order.partner.service"
    _apply_on = ["sale.order"]

    def _apply_company_specific_values(self, partner_vals: dict):
        """
        Hook method to apply company/country specific values to partner creation.
        Override this method in other modules to add custom logic.
        """
        pass
    
    def process_partner(self, partner_vals: dict, shipping_vals: dict = None):
        """ Process partner based on vals. """
        partner = None
        vat = partner_vals.get("vat")
        email = partner_vals.get("email")
        if vat:
            partner = self.collection.env['res.partner'].search([('vat', '=', vat)], limit=1)
        elif email:
            partner = self.collection.env['res.partner'].search([('email', '=', email)], limit=1)
        
        if not partner:
            create_vals = partner_vals.copy()

            self._apply_company_specific_values(create_vals)

            partner = self.collection.env['res.partner'].create(create_vals)
        
        shipping_partner = partner
        
        if shipping_vals and any(shipping_vals.values()):
            domain = [
                ('parent_id', '=', partner.id),
                ('type', '=', 'delivery'),
                ('street', '=', shipping_vals.get('street')),
                ('city', '=', shipping_vals.get('city'))
            ]
            if shipping_vals.get('zip'):
                domain.append(('zip', '=', shipping_vals.get('zip')))
                
            existing_delivery = self.collection.env['res.partner'].search(domain, limit=1)
            
            if existing_delivery:
                shipping_partner = existing_delivery
            else:
                delivery_create_vals = shipping_vals.copy()
                delivery_create_vals['parent_id'] = partner.id
                delivery_create_vals['type'] = 'delivery'

                self._apply_company_specific_values(delivery_create_vals)

                shipping_partner = self.collection.env['res.partner'].create(delivery_create_vals)
                    
        return partner, shipping_partner