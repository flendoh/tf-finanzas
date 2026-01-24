from typing import Any
from odoo.addons.component.core import Component
import logging
import json

_logger = logging.getLogger(__name__)

class FalabellaAdapter(Component):
    """ Falabella Adapter for Orders """
    _name = "falabella.market.adapter"
    _inherit = "order.market.adapter"
    _usage = "order.adapter"
    _backend_type = "falabella"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type
    
    def _validate_account_credentials(self):
        """
        Validates the account credentials by making a test request to the API.
        """
        if not self.collection.falabella_base_url:
            raise ValueError("URL Base Falabella no configurada")
        if not self.collection.falabella_user_id:
            raise ValueError("ID de Usuario Falabella no configurado")
        if not self.collection.falabella_api_key:
            raise ValueError("Clave API Falabella no configurada")

        return True

    def create_package_order_from_webhook(self, webhook):
        """ Enrich the data with additional information from the external system """

        external_id = webhook["payload"]["OrderId"]

        _logger.info(f"Creating package order: {external_id}")

        webservice = self.component(usage="order.webservice")
        mapper = self.component(usage="order.import.mapper")

        order_data = webservice.get("GetOrder", params={"OrderId": external_id}, version="2.0")
        order_items_data = webservice.get("GetOrderItems", params={"OrderId": external_id})
        
        return dict[str, Any](
            order=mapper.map_create_order(order_data),
            lines=mapper.map_create_order_lines(order_items_data),
            partner=mapper.map_create_partner(order_data)
        )
    
    def get_document(self, external_id):
        """
        Retrieves the documents for the order.
        """

        webservice = self.component(usage="order.webservice")
        mapper = self.component(usage="order.import.mapper")
        
        order_items_data = webservice.get("GetOrderItems", params={"OrderId": external_id})
        lines = mapper.map_create_order_lines(order_items_data, include_external_id=True)
        
        params = {
            "DocumentType": "shippingParcel",
            "OrderItemIds": json.dumps([int(line["marketplace_external_id"]) for line in lines]),
        }

        _logger.info(f"GetDocument params: {params}")
        
        return mapper.map_document(webservice.get("GetDocument", params=params), external_id)
