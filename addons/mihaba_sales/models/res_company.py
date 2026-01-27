from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    warehouse_manager_id = fields.Many2one(
        'res.users',
        string="Almacenero/Encargado de Despacho",
        help="Usuario responsable del almacén que recibirá actividades cuando las órdenes estén listas para envío"
    )
