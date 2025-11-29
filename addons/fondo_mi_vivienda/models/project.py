from odoo import models, fields


class Project(models.Model):
    _name = 'fondo_mi_vivienda.project'
    _description = 'Proyecto Vivienda'

    name = fields.Char(string='Nombre', required=True)
    tipo_propiedad = fields.Selection(
        string='Tipo de Propiedad',
        selection=[('house', 'Casa'), ('apartment', 'Departamento')],
        required=True
    )

    moneda_id = fields.Many2one('res.currency', string='Moneda', required=True)
    valor_vivienda = fields.Monetary(string='Valor de la vivienda', required=True, currency_field='moneda_id')
    es_vivienda_sostenible = fields.Boolean(string='¿La vivienda es sostenible?', required=True)

    calle = fields.Char(string='Calle')
    departamento = fields.Many2one('res.country.state', string='Departamento', domain="[('country_id', '=', 173)]")
    ciudad = fields.Char(string='Ciudad')

    estado = fields.Selection(
        string='Estado',
        selection=[('open', 'Abierto'), ('close', 'Cerrado')],
        default='open',
        required=True
    )

    active = fields.Boolean(string='Activo', default=True)