from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderDocumentImporter(Component):
    _name = "order.document.importer"
    _usage = "document.importer"
    _apply_on = ["sale.order"]
    
    def run(self, order):
        """ Get document from marketplace and attach to order. """
        if not order.marketplace_external_id:
            _logger.warning("Cannot get document: Order %s has no external ID", order.name)
            return

        adapter = self.component(usage="order.adapter")
        
        attachment_vals = adapter.get_document(order.marketplace_external_id)
        
        if attachment_vals:
            attachment_vals.update({
                'res_model': 'sale.order',
                'res_id': order.id,
                'type': 'binary',
            })
            self.collection.env['ir.attachment'].create(attachment_vals)
            _logger.info("Document attached to order %s", order.name)
        else:
            _logger.warning("No document found for order %s", order.name)
