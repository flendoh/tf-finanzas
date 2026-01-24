from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderUrlRetriever(Component):
    _name = "order.url.retriever"
    _usage = "url.retriever"
    _apply_on = ["sale.order"]
    
    def run(self, order):
        """ Retrieve the marketplace order URL using the adapter. """
        adapter = self.component(usage="order.adapter")

        if not order.marketplace_external_id:
            return False
        
        url = adapter.get_order_url(order.marketplace_external_id)

        if not url:
            return False
            
        return url