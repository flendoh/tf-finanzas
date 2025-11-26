# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    aplicar_a_bbp_integrador = fields.Boolean(
        string="¿Aplicar a BBP Integrador?",
        help="(5) Personas vulnerables en los grupos: Personas de menores ingresos, adultos mayores, personas con discapacidad, personas desplazadas, migrantes retornados."
    )

    ha_recibido_apoyo_habitacional_antes = fields.Boolean(
        string="¿Ha recibido apoyo habitacional antes?"
    )

    moneda_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.user.company_id.currency_id
    )

    ingreso_financiero = fields.Monetary(
        string="Ingreso financiero mensual",
        currency_field="moneda_id"
    )

    gastos_financieros = fields.Monetary(
        string="Gastos financieros mensuales",
        currency_field="moneda_id"
    )

    deudas_financieras = fields.Monetary(
        string="Deudas financieras mensuales",
        currency_field="moneda_id"
    )

    simulaciones_ids = fields.One2many(
        comodel_name='fondo_mi_vivienda.scenario_simulation',
        inverse_name='cliente_id',
        string='Simulaciones de Escenario'
    )

    simulaciones_count = fields.Integer(
        string='Número de Simulaciones',
        compute='_compute_simulaciones_count'
    )

    def _compute_simulaciones_count(self):
        for partner in self:
            partner.simulaciones_count = len(partner.simulaciones_ids)

    def action_view_simulaciones(self):
        self.ensure_one()
        return {
            'name': f'Simulaciones de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'fondo_mi_vivienda.scenario_simulation',
            'view_mode': 'list,form',
            'domain': [('cliente_id', '=', self.id)],
            'context': {
                'default_cliente_id': self.id
            },
        }