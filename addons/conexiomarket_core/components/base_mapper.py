from odoo.addons.component.core import AbstractComponent
import pytz
from dateutil.parser import parse
# pylint: disable=W8106
class BaseMapper(AbstractComponent):
    """ Base Mapper for transforming data between Odoo and External Systems.
    
    - ImportMapper: External Data -> Odoo Data (Dict)
    - ExportMapper: Odoo Record -> External Data (Dict)
    """
    _name = "base.market.mapper"
    _collection = "market.account"

    def to_utc(self, dt):
        return dt.astimezone(pytz.utc)

    def parse_to_utc(self, date_str):
        if not date_str:
            return False
        dt = parse(date_str)
        if not dt.tzinfo:
            timezone = self.collection.tz or 'UTC'
            dt = pytz.timezone(timezone).localize(dt)
        return self.to_utc(dt).replace(tzinfo=None)

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
