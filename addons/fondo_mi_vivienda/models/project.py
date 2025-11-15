from odoo import models, fields


class Project(models.Model):
    _name = 'fondo_mi_vivienda.project'
    _description = 'Proyecto Vivienda'

    name = fields.Char(string='Nombre', required=True)
    property_type = fields.Selection(
        string='Tipo de Propiedad',
        selection=[('house', 'Casa'), ('apartment', 'Departamento')],
        required=True
    )

    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    property_value = fields.Monetary(string='Valor de la vivienda', required=True, currency_field='currency_id')
    is_property_sustainable = fields.Boolean(string='¿La vivienda es sostenible?', required=True)

    street = fields.Char(string='Calle')
    department = fields.Many2one('res.country.state', string='Departamento', domain="[('country_id', '=', 173)]")
    city = fields.Char(string='Ciudad')

    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Borrador'), ('open', 'Abierto'), ('close', 'Cerrado')],
        default='draft',
        required=True
    )

    active = fields.Boolean(string='Activo', default=True)
