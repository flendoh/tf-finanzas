from odoo import _
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderImporter(Component):
    _name = "market.order.importer"
    _collection = "market.account"
    _usage = "importer"
    _apply_on = ["sale.order"]
    
    def run(self, payload):
        """ Import order from a webhook payload. """
        adapter = self.component(usage="order.adapter")
        package = adapter.create_package_order_from_webhook(payload)
        
        return self._import_order(package)

    def _import_order(self, package):
        """ Internal method to process the normalized package. """

        external_id = package.get("external_id")

        if not external_id:
            raise ValueError(_("El payload de la orden no contiene un ID externo válido."))

        account = self.collection

        if package.get('order'):
            package['order'].update({
                'company_id': account.company_id.id,
                'user_id': account.user_id.id,
                'warehouse_id': account.warehouse_id.id,
                'marketplace_account_id': account.id,
            })
        
        binder = self.component(usage="order.binder")
        
        # 1. Check if order already exists
        existing_order = binder.to_internal(external_id)
        if existing_order:
            raise ValueError(_("La orden %s ya existe como %s.") % (external_id, existing_order.name))
            
        # 2. Get Order Values
        order_vals = package.get("order") or {}
        
        # 3. Handle Partner via Service
        partner_service = self.component(usage="order.partner.service")
        partner_vals = package.get("partner") or {}

        if account.partner_category_id:
            partner_vals.update({
                'category_id': [(4, account.partner_category_id.id)],
            })

        partner = partner_service.process_partner(partner_vals)
        order_vals["partner_id"] = partner.id
        
        # 4. Handle Lines via Service
        product_service = self.component(usage="order.product.service")
        processed_lines, missing_lines = product_service.process_lines(package.get("lines"))
        order_vals["order_line"] = [(0, 0, line) for line in processed_lines]

        order = self.collection.env["sale.order"].create(order_vals)
        
        # 5. Post process
        if missing_lines and account and not account.create_product_if_not_found:
            product_service.handle_missing_products(order, missing_lines)
        
        # 7. Bind the order
        if external_id:
            binder.bind(external_id, order.id)
            
        _logger.info("Created new market order %s (ID: %s)", order.name, order.id)
        return order