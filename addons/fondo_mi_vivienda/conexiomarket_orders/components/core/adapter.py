from odoo.addons.component.core import AbstractComponent

class OrderAdapter(AbstractComponent):
    _name = "order.market.adapter"
    _inherit = "base.market.adapter"
    _apply_on = ["sale.order"]

    def create_package_order_from_webhook(self, payload):
        """ Convert webhook payload to normalized package.
        
        :param payload: dict, raw data from webhook
        :return: dict, normalized package
        """
        raise NotImplementedError

    def get_document(self, external_id, **kwargs):
        """ Get document data from marketplace. 
        
        :param external_id: str, External Order ID
        :param kwargs: dict, Extra arguments for specific implementations
        :return: raw data (usually list of dicts or dict)
        """
        raise NotImplementedError
