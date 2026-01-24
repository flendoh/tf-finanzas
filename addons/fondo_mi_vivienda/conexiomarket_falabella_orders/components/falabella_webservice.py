from odoo.addons.component.core import Component
import logging
import sys
import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from datetime import datetime


_logger = logging.getLogger(__name__)

class FalabellaWebservice(Component):
    """
    """
    _name = "falabella.market.webservice"
    _inherit = "base.market.webservice"
    _usage = "order.webservice"
    _backend_type = "falabella"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type

    @staticmethod
    def _generate_signature(api_key, parameters):
        """
        Generates an HMAC-SHA256 signature for API requests.

        Args:
            api_key (str): Your API key provided by the service.
            parameters (dict): A dictionary containing request parameters.

        Returns:
            str: The generated signature in hexadecimal format.
        """
        # Sort the parameters alphabetically
        sorted_params = sorted(parameters.items())

        # Concatenate the parameters into URL format
        concatenated = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)

        # Generate the HMAC-SHA256 signature
        signature = HMAC(api_key.encode('utf-8'), concatenated.encode('utf-8'), sha256).hexdigest()
        return signature
    
    def get(self, action, params=None, version="1.0"):
        user_id = self.collection.falabella_user_id
        api_key = self.collection.falabella_api_key

        base_params = {
            'Action': action,
            'Format': 'JSON',
            'Timestamp': datetime.now().isoformat(),
            'UserID': user_id,
            'Version': version,
        }
        if params:
            base_params.update(params)

        base_params['Signature'] = self._generate_signature(api_key, base_params)

        headers = self._get_user_agent_header()

        response = requests.get(self.collection.falabella_base_url, params=base_params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def _get_user_agent_header(self):
        """Build the User-Agent header based on Falabella requirements."""
        seller_id = self.collection.falabella_seller_id or 'UNKNOWN_SELLER'
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        integrator_name = "PROPIA"

        country_map = {'cl': 'FACL', 'co': 'FACO', 'pe': 'FAPE'}
        country_code = 'pe'
        business_unit_code = country_map.get(country_code, 'UNKNOWN')

        user_agent = (
            f"{seller_id}/Python/{python_version}/{integrator_name}/{business_unit_code}"
        )
        return {'User-Agent': user_agent}