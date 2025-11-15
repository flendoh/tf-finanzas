# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    apply_to_bbp_integrator = fields.Boolean(
        string="¿Aplicar a BBP Integrador?",
        help="(5) Personas vulnerables en los grupos: Personas de menores ingresos, adultos mayores, personas con discapacidad, personas desplazadas, migrantes retornados."
    )

    has_received_housing_support_before = fields.Boolean(
        string="¿Ha recibido apoyo habitacional antes?"
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.user.company_id.currency_id
    )

    financial_income = fields.Monetary(
        string="Ingreso financiero mensual",
        help="Ingreso financiero mensual en pesos chilenos.",
        currency_field="currency_id"
    )

    financial_expenses = fields.Monetary(
        string="Gastos financieros mensuales",
        help="Gastos financieros mensuales en pesos chilenos.",
        currency_field="currency_id"
    )

    financial_debts = fields.Monetary(
        string="Deudas financieras mensuales",
        help="Deudas financieras mensuales en pesos chilenos.",
        currency_field="currency_id"
    )