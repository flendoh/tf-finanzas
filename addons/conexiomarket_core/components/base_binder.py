from odoo.addons.component.core import AbstractComponent


class BaseBinder(AbstractComponent):
    """ Base Binder for linking External IDs with Odoo IDs.

    The Binder is responsible for:
    1. Finding the Odoo record corresponding to an external ID (Import).
    2. Finding the External ID corresponding to an Odoo record (Export).
    3. Creating the link (Binding) between them.

    This usually relies on a concrete model (e.g. `market.order`, `market.product`)
    that stores the `external_id` and the `odoo_id`.
    """
    _name = "base.market.binder"
    _collection = "market.account"

    def to_internal(self, external_id, unwrap=False):
        """ Get the Odoo record (or ID) for an external ID.

        :param external_id: The ID in the external system.
        :param unwrap: If True, return the Odoo ID (int). 
                       If False, return the Odoo recordset.
        :return: Odoo recordset or ID, or None if not found.
        """
        raise NotImplementedError

    def to_external(self, binding_id):
        """ Get the External ID for an Odoo binding record.

        :param binding_id: The ID of the binding record (not the Odoo record itself, 
                           unless they are the same model).
        :return: External ID (str/int) or None.
        """
        raise NotImplementedError

    def bind(self, external_id, binding_id):
        """ Create or update the link between external_id and binding_id.
        
        :param external_id: ID in external system
        :param binding_id: ID of the binding record in Odoo
        """
        raise NotImplementedError
