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
            raise ValueError("El pedido %s no tiene ID externo" % order.name)
        adapter = self.component(usage="order.adapter")
        
        attachment_vals = adapter.get_document(order.marketplace_external_id)
        
        if not attachment_vals:
            raise ValueError("No se encontró documento para el pedido %s", order.name)

        attachment_vals.update({
            'res_model': 'sale.order',
            'res_id': order.id,
            'type': 'binary',
        })
        return self.collection.env['ir.attachment'].create(attachment_vals)