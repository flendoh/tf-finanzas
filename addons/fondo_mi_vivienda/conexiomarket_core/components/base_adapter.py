from odoo.addons.component.core import AbstractComponent

# pylint: disable=W8106
class BaseAdapter(AbstractComponent):
    """ Base External Adapter specialized in the handling
    of records on external systems.
    
    The Adapter is responsible ONLY for the communication with the external API.
    It should return raw data (dicts) and not Odoo records.
    """
    _name = "base.market.adapter"
    _collection = "market.account"

    def search(self, filters=None):
        """ Search records in the external system.
        :param filters: dict of filters to apply
        :return: list of raw data (dicts) or list of IDs
        """
        raise NotImplementedError

    def read(self, external_id):
        """ Read a record from the external system.
        :param external_id: ID of the record in the external system
        :return: raw data (dict)
        """
        raise NotImplementedError

    def create(self, data):
        """ Create a record in the external system.
        :param data: dict of data to create
        :return: ID of the created record or full data
        """
        raise NotImplementedError

    def write(self, external_id, data):
        """ Update a record in the external system.
        :param external_id: ID of the record to update
        :param data: dict of data to update
        :return: boolean or updated data
        """
        raise NotImplementedError

    def delete(self, external_id):
        """ Delete a record in the external system.
        :param external_id: ID of the record to delete
        :return: boolean
        """
        raise NotImplementedError
