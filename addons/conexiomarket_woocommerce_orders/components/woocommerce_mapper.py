import json
from typing import Any
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class WooCommerceMapper(Component):
    _name = "woocommerce.market.mapper"
    _inherit = "order.import.mapper"
    _usage = "order.import.mapper"
    _backend_type = "woocommerce"

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        return work.collection.backend_type == cls._backend_type

    def map_create_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the order data to the Odoo format """
        
        vals = dict(
            marketplace_external_id=str(order_data.get('id')),
            marketplace_order_number=order_data.get('number'),
            marketplace_date_order=order_data.get('date_created'),
            marketplace_invoice_required=False,
            partner_id=None,
            client_order_ref=order_data.get('number'),
            origin=f"WooCommerce-{order_data.get('id')}",
            state='draft',
            marketplace_order_note=order_data.get('customer_note', ''),
            marketplace_payment_method=order_data.get('payment_method_title', order_data.get('payment_method')),
            marketplace_last_raw_data=json.dumps(order_data, indent=4),
        )
        
        return vals
    
    def map_create_order_lines(self, order_data: dict[str, Any]) -> list[dict[str, Any]]:
        """ Map the order lines data to the Odoo format """
        items = order_data.get('line_items', [])
        
        lines = []
        for item in items:
            product_info = {
                'name': item.get('name', 'Producto sin nombre'),
                'default_code': item.get('sku') or item.get('name'), # Fallback to name if SKU is missing
                'external_id': str(item.get('id'))
            }

            line_vals = dict(
                product_id=product_info,
                product_uom_qty=float(item.get('quantity') or 1),
                price_unit=float(item.get('price') or 0.0),
            )
            
            lines.append(line_vals)
        return lines
    
    def map_create_partner(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """ Map the partner data to the Odoo format """
        billing = order_data.get('billing', {})
        shipping = order_data.get('shipping', {})
        
        first_name = billing.get('first_name', '')
        last_name = billing.get('last_name', '')
        name = f"{first_name} {last_name}".strip()
        
        if not name:
            name = f"Customer {order_data.get('customer_id')}"

        partner_vals = dict(
            name = name,
            street = billing.get('address_1'),
            street2 = billing.get('address_2'),
            city = billing.get('city'),
            zip = billing.get('postcode'),
            email = billing.get('email'),
            phone = billing.get('phone'),
        )

        # --- Shipping Partner (Delivery Address) ---
        shipping_vals = {}
        s_first = shipping.get('first_name', '')
        s_last = shipping.get('last_name', '')
        s_name = f"{s_first} {s_last}".strip()

        if s_name or shipping.get('address_1'):
            shipping_vals = dict(
                name = s_name or name,
                street = shipping.get('address_1'),
                street2 = shipping.get('address_2'),
                city = shipping.get('city'),
                zip = shipping.get('postcode'),
            )
        
        return dict(
            partner = partner_vals,
            shipping = shipping_vals
        )
