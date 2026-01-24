from odoo.addons.component.core import Component

class OrderBinder(Component):
    _name = "order.market.binder"
    _inherit = "base.market.binder"
    _usage = "order.binder"
    _apply_on = ["sale.order"]

    def to_internal(self, external_id, unwrap=False):
        domain = [
            ("marketplace_external_id", "=", external_id),
            ("marketplace_account_id", "=", self.collection.id)
        ]
        record = self.collection.env["sale.order"].search(domain, limit=1)
        if unwrap:
            return record.id
        return record

    def to_external(self, binding_id):
        record = self.collection.env["sale.order"].browse(binding_id)
        return record.marketplace_external_id

    def bind(self, external_id, binding_id):
        record = self.collection.env["sale.order"].browse(binding_id)
        record.write({
            "marketplace_external_id": external_id,
            "marketplace_account_id": self.collection.id
        })
