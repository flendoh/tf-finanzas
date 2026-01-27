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
    
    def _validate_account_credentials(self):
        """
        Validates the account credentials.
        """
        if not self.collection.woocommerce_url:
            raise ValueError("URL WooCommerce no configurada")
        
        return True

    def create_package_order_from_webhook(self, webhook):
        """ Enrich the data with additional information from the external system """
        order_data = webhook
        
        external_id = order_data.get("id")
        _logger.info(f"Creating package order: {external_id}")

        mapper = self.component(usage="order.import.mapper")
        
        partners_data = mapper.map_create_partner(order_data)
        
        return dict[str, Any](
            external_id=str(external_id),
            order=mapper.map_create_order(order_data),
            lines=mapper.map_create_order_lines(order_data),
            partner=partners_data.get('partner'),
            shipping=partners_data.get('shipping')
        )
    
    def get_order_url(self, external_id):
        """
        Returns the URL of the order in the marketplace.
        """
        base_url = self.collection.woocommerce_url
        if base_url:
            return f"{base_url}/wp-admin/post.php?post={external_id}&action=edit"
        return False
