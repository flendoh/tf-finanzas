from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_manager_id = fields.Many2one(
        related='company_id.warehouse_manager_id',
        string="Almacenero/Encargado de Despacho",
        readonly=False,
        help="Usuario responsable del almacén que recibirá actividades cuando las órdenes estén listas para envío"
    )
