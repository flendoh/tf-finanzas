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
        external_id = package['order'].get("marketplace_external_id")
        
        binder = self.component(usage="order.binder")
        
        # 1. Check if order already exists
        existing_order = binder.to_internal(external_id)
        if existing_order:
            raise ValueError(_("Order %s already exists as %s.") % (external_id, existing_order.name))
        # 2. Get Order Values
        order_vals = package.get("order") or {}
        # 3. Handle Partner
        partner = self._upsert_partner(package.get("partner") or {})
        order_vals["partner_id"] = partner.id
        # 4. Handle Lines
        processed_lines, missing_lines = self._process_order_lines(package.get("lines"))
        order_vals["order_line"] = [(0, 0, line) for line in processed_lines]
        
        # 5. Create Order
        order = self.collection.env["sale.order"].create(order_vals)
        
        # 6. Post-processing (Missing Products)
        account = self.collection
        if missing_lines and account and not account.create_product_if_not_found:
            self._schedule_missing_product_activity(order, missing_lines, account)
        _logger.info("Created new market order %s (ID: %s)", order.name, order.id)
        return order
        
    def _upsert_partner(self, partner_vals: dict):
        """ Find or create partner. """
        partner = None
        vat = partner_vals.get("vat")
        if vat:
            partner = self.collection.env['res.partner'].search([('vat', '=', vat)], limit=1)
        
        if not partner:
            create_vals = partner_vals.copy()
            
            # Specific logic for Peru localization (safe check) TODO: Mover esto a mihaba_sale
            dni_type = self.collection.env.ref('l10n_pe.it_DNI', raise_if_not_found=False)
            if dni_type:
                create_vals['l10n_latam_identification_type_id'] = dni_type.id
            
            if self.collection.partner_category_id:
                create_vals['category_id'] = [(4, self.collection.partner_category_id.id)]
                
            partner = self.collection.env['res.partner'].create(create_vals)

            if hasattr(partner, 'update_document'):
                partner.update_document()
                    
        return partner

    def _process_order_lines(self, lines: list[dict]):
        """ Process lines, handling product resolution. """
        valid_lines = []
        missing_lines = []
        
        if not lines:
            return [], []

        account = self.collection
        create_products = bool(account and account.create_product_if_not_found)

        for line in lines:
            product_data = line.get("product_id")
            
            if isinstance(product_data, int):
                valid_lines.append(line)
                continue
            
            if isinstance(product_data, dict):
                # Product needs resolution/creation
                # Try to find by SKU/Default Code first
                default_code = product_data.get("default_code")
                product = None
                if default_code:
                    product = self.collection.env["product.product"].search([('default_code', '=', default_code)], limit=1)
                
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

    def _schedule_missing_product_activity(self, order, missing_lines, account):
        assignee = (account.user_id.id if account and account.user_id else order.user_id.id) or self.collection.env.user.id
        details = []
        for l in missing_lines:
            info = l.get("product_id", {}) or {}
            # Handle if info is not a dict (should rely on previous checks, but be safe)
            if not isinstance(info, dict):
                info = {"name": "Unknown", "default_code": "Unknown", "external_id": "Unknown"}
                
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
