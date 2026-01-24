from odoo.addons.component.core import AbstractComponent

# pylint: disable=W8106
class BaseWebservice(AbstractComponent):
    """ 

    """
    _name = "base.market.webservice"
    _collection = "market.account"

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def post(self, *args, **kwargs):
        raise NotImplementedError