from odoo import models, fields, api
from odoo.exceptions import ValidationError

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

    active = fields.Boolean(string='Activo', default=True)

    expediente_ids = fields.One2many('fondo_mi_vivienda.dossier', 'proyecto_id', string='Expedientes')
    expediente_count = fields.Integer(string='Expedientes', compute='_compute_dossier_count')

    @api.depends('expediente_ids')
    def _compute_dossier_count(self):
        for record in self:
            record.expediente_count = len(record.expediente_ids)

    def action_view_expedientes(self):
        self.ensure_one()
        return {
            'name': 'Expedientes',
            'type': 'ir.actions.act_window',
            'res_model': 'fondo_mi_vivienda.dossier',
            'view_mode': 'list,form',
            'domain': [('proyecto_id', '=', self.id)],
            'context': {'default_proyecto_id': self.id},
        }
    
    @api.constrains('valor_vivienda')
    def _check_valor_vivienda(self):
        for r in self:
            if not 67400 <= r.valor_vivienda <= 355100:
                raise ValidationError("El valor de la vivienda debe estar entre 67,400 y 355,100.")