from odoo import _
from odoo.addons.component.core import Component
import logging

_logger = logging.getLogger(__name__)

class OrderProductService(Component):
    _name = "market.order.product.service"
    _collection = "market.account"
    _usage = "order.product.service"
    _apply_on = ["sale.order"]

    def process_lines(self, lines: list[dict]):
        """ Process lines, handling product resolution. """
        valid_lines = []
        missing_lines = []
        
        if not lines:
            return [], []

        account = self.collection
        create_products = bool(account and account.create_product_if_not_found)

        for line in lines:
            product_data = line.get("product_id")
            
            if isinstance(product_data, dict):
                external_id = product_data.get("external_id")
                product = None
                
                if external_id:
                    mapping = self.collection.env["market.product.mapping"].search([
                        ("account_id", "=", account.id),
                        ("external_id", "=", str(external_id))
                    ], limit=1)
                    if mapping:
                        product = mapping.product_id.product_variant_id

                if product:
                    line["product_id"] = product.id
                    valid_lines.append(line)
                elif create_products:
                    product = self._create_product(product_data)
                    line["product_id"] = product.id
                    valid_lines.append(line)
                    
                    self._create_product_mapping(product, product_data.get("external_id"))
                else:
                    missing_lines.append(line)
            else:
                missing_lines.append(line)

        return valid_lines, missing_lines

    def _create_product(self, product_info):
        return self.collection.env["product.product"].create({
            "name": product_info.get("name", "Unknown Product"),
            "default_code": product_info.get("default_code"),
            "type": "consu"
        })

    def _create_product_mapping(self, product, external_id):
        if not external_id:
            return

        self.collection.env["market.product.mapping"].create({
            "account_id": self.collection.id,
            "external_id": external_id,
            "product_id": product.product_tmpl_id.id,
        })

    def handle_missing_products(self, order, missing_lines):
        """ Schedule activity for missing products. """
        account = self.collection
        assignee = (account.user_id.id if account and account.user_id else order.user_id.id) or self.collection.env.user.id
        details = []
        for l in missing_lines:
            info = l.get("product_id", {}) or {}
                
            details.append(
                f"- [{info.get('default_code')}] {info.get('name')} x {l.get('product_uom_qty') or 0} @ {l.get('price_unit') or 0} - {info.get('external_id')}"
            )
        summary = _("Productos no encontrados al crear el pedido %s desde el marketplace.") % (order.name or order.client_order_ref)
        
        act_type_xmlid = 'mail.mail_activity_data_warning'
        if not self.collection.env.ref(act_type_xmlid, raise_if_not_found=False):
            act_type_xmlid = 'mail.mail_activity_data_todo'
            
        if self.collection.env.ref(act_type_xmlid, raise_if_not_found=False):
            order.activity_schedule(
                act_type_xmlid, 
                user_id=assignee, 
                summary=summary, 
                note="<br>".join(details)
            )
