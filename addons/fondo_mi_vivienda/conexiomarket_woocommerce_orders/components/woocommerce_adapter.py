from typing import Any
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class WooCommerceAdapter(Component):
    """ WooCommerce Adapter for Orders """
    _name = "woocommerce.market.adapter"
    _inherit = "order.market.adapter"
    _usage = "order.adapter"
    _backend_type = "woocommerce"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type
    
    def create_package_order_from_webhook(self, webhook):
        order_data = webhook
        
        external_id = order_data.get("id")
        _logger.info(f"Creating package order: {external_id}")

        mapper = self.component(usage="order.import.mapper")
        
        return dict[str, Any](
            order=mapper.map_create_order(order_data),
            lines=mapper.map_create_order_lines(order_data),
            partner=mapper.map_create_partner(order_data)
        )
