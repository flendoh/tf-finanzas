from odoo import _
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderPartnerService(Component):
    _name = "market.order.partner.service"
    _collection = "market.account"
    _usage = "order.partner.service"
    _apply_on = ["sale.order"]
    
    def process_partner(self, partner_vals: dict):
        """ Process partner based on vals. """
        partner = None
        vat = partner_vals.get("vat")
        if vat:
            partner = self.collection.env['res.partner'].search([('vat', '=', vat)], limit=1)
        
        if not partner:
            create_vals = partner_vals.copy()

            partner = self.collection.env['res.partner'].create(create_vals)
                    
        return partner