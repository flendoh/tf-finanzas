import json
from typing import Any
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class FalabellaMapper(Component):
    _name = "falabella.market.mapper"
    _inherit = "order.import.mapper"
    _usage = "order.import.mapper"
    _backend_type = "falabella"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type

    def map_record(self, record):
        return record

    def map_create_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the order data to the Odoo format """
        order_info = order_data['SuccessResponse']['Body']['Orders']['Order']
        
        vals = dict(
            marketplace_shipping_deadline=order_info.get('PromisedShippingTime'),
            marketplace_external_id=order_info.get('OrderId'),
            marketplace_date_order=order_info.get('CreatedAt'),
            marketplace_order_number=order_info.get('OrderNumber'),
            marketplace_invoice_required= str(order_info.get('InvoiceRequired', False)).lower() == 'true',
            partner_id=None,
            client_order_ref=order_info.get('OrderNumber'),
            origin=f"Falabella-{order_info.get('OrderId')}",
            date_order=order_info.get('CreatedAt'),
            state='draft',
            note=order_info.get('Remarks', ''),
            company_id=self.collection.company_id.id,
            user_id=self.collection.user_id.id,
            warehouse_id=self.collection.warehouse_id.id,
            commitment_date=order_info.get('PromisedShippingTime'),
            marketplace_raw_data=json.dumps(order_data, indent=4),
        )
        
        return vals
    
    def map_create_order_lines(self, order_items_data: dict[str, Any], include_external_id: bool = False) -> list[dict[str, Any]]:
        """ Map the order lines data to the Odoo format """
        order_items_data = order_items_data['SuccessResponse']['Body'].get('OrderItems', {})
        items = order_items_data.get('OrderItem', [])
        
        if isinstance(items, dict):
            items = [items]
        
        lines = []
        for item in items:
            product_info = {
                'name': item.get('Name', 'Producto sin nombre'),
                'default_code': item.get('Sku', 'Desconocido'),
                'external_id': item.get('OrderItemId')
            }

            line_vals = dict(
                product_id=product_info,
                product_uom_qty=float(item.get('PurchaseOrderNumber') or 1),
                price_unit=float(item.get('ItemPrice') or 0.0),
            )

            if include_external_id:
                line_vals.update(
                    marketplace_external_id = item.get('OrderItemId')
                )
            
            lines.append(line_vals)
        return lines
    
    def map_create_partner(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the partner data to the Odoo format """
        order = order_data['SuccessResponse']['Body']['Orders']['Order']
        address_billing = order['AddressBilling']
        vals = dict(
            vat = order.get('NationalRegistrationNumber'),
            name = f"{order.get('CustomerFirstName')} {order.get('CustomerLastName')}",
            street = address_billing.get('Address1'),
            street2 = address_billing.get('Address2'),
            is_company = False
        )

        if address_billing.get('CustomerEmail'):
            vals.update(
                email = address_billing.get('CustomerEmail')
            )

        return vals
    
    def map_document(self, document_data, external_id):
        """ Map document data to attachment values. """
        body = document_data.get('SuccessResponse', {}).get('Body', {})
        documents = body.get('Documents', {}).get('Document', [])

        if isinstance(documents, dict):
            documents = [documents]
            
        if not documents:
            return None
            
        doc = documents[0]
        
        file_content = doc.get('File')
        if not file_content:
            return None
        
        mimetype = doc.get('MimeType', 'application/pdf')
        return {
            'name': f"{doc.get('DocumentType', 'document')}_{external_id}.{self._get_extension(mimetype)}",
            'datas': file_content,
            'mimetype': mimetype,
        }

    def _get_extension(self, mimetype):
        if mimetype == 'application/pdf':
            return 'pdf'
        if mimetype == 'text/html':
            return 'html'
        return 'bin'