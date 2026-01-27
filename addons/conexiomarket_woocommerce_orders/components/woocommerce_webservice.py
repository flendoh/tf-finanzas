from odoo.addons.component.core import Component
import logging
import requests
from urllib.parse import urljoin

_logger = logging.getLogger(__name__)

class WooCommerceWebservice(Component):
    """
    """
    _name = "woocommerce.market.webservice"
    _inherit = "base.market.webservice"
    _usage = "order.webservice"
    _backend_type = "woocommerce"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type

    def get(self, endpoint, params=None):
        """
        Generic GET request to WooCommerce API.
        Currently only supports public endpoints or basic requests as no auth is configured.
        """
        base_url = self.collection.woocommerce_url
        if not base_url:
            raise ValueError("WooCommerce URL is not configured")
            
        url = urljoin(base_url, endpoint)
        
        # Placeholder for future authentication
        headers = {
            'User-Agent': 'Odoo-ConexioMarket/1.0'
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"WooCommerce API Error: {str(e)}")
            raise
