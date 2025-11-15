from odoo import models, fields, api


class FeeScheduleLine(models.Model):
    _name = 'fondo_mi_vivienda.fee_schedule_line'
    _description = 'Linea de Cronograma de Cuotas'

    name = fields.Integer(string='Periodo', required=True)

    scenario_simulation_id = fields.Many2one(
        comodel_name='fondo_mi_vivienda.scenario_simulation',
        required=True
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        related="scenario_simulation_id.currency_id"
    )

    initial_balance = fields.Monetary(
        string="Saldo Inicial",
        currency_field="currency_id",
        required=True
    )

    amortization = fields.Monetary(
        string="Amortización",
        currency_field="currency_id",
        required=True
    )

    debt_relief_insurance = fields.Monetary(
        string="Seguro Desgravamen",
        currency_field="currency_id",
        required=True
    )

    property_insurance = fields.Monetary(
        string="Seguro de Inmueble",
        currency_field="currency_id",
        required=True
    )

    final_balance = fields.Monetary(
        string="Saldo Final",
        currency_field="currency_id",
        required=True
    )

    monthly_payment = fields.Monetary(
        string="Pago Mensual",
        currency_field="currency_id",
        required=True
    )