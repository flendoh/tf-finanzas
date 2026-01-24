from odoo.addons.component.core import AbstractComponent

# pylint: disable=W8106
class BaseMapper(AbstractComponent):
    """ Base Mapper for transforming data between Odoo and External Systems.
    
    - ImportMapper: External Data -> Odoo Data (Dict)
    - ExportMapper: Odoo Record -> External Data (Dict)
    """
    _name = "base.market.mapper"
    _collection = "market.account"

    def map_record(self, record):
        """ Main method to map a record.
        
        If importing: record is a dict (external data).
        If exporting: record is an Odoo recordset.
        
        :return: dict with mapped values
        """
        raise NotImplementedError

    def map(self, *args, **kwargs):
        """ Deprecated: Use map_record instead """
        return self.map_record(*args, **kwargs)

    def map_to_external(self, *args, **kwargs):
        """ Deprecated: Use ExportMapper strategy """
        raise NotImplementedError
