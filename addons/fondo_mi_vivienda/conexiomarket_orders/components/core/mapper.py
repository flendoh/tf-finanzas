from odoo.addons.component.core import AbstractComponent

class OrderImportMapper(AbstractComponent):
    _name = "order.import.mapper"
    _inherit = "base.market.mapper"
    _apply_on = ["sale.order"]

    def map_record(self, record):
        """ Map the normalized package to Odoo values. 
        
        :param record: dict containing the order data (package['order'])
        :return: dict for sale.order.create
        """
        # In the current design, the package['order'] is already close to Odoo vals.
        # We can add default mappings here.
        return record.copy()

    def map_document(self, document_data, external_id):
        """ Map document data to attachment values.
        
        :param document_data: raw data from adapter
        :param external_id: external ID of the order/document
        :return: dict for ir.attachment
        """
        raise NotImplementedError
