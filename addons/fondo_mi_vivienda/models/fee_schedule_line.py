from odoo import models, fields, api


class FeeScheduleLine(models.Model):
    _name = 'fondo_mi_vivienda.fee_schedule_line'
    _description = 'Linea de Cronograma de Cuotas'

    name = fields.Integer(string='Periodo', required=True)

    simulacion_escenario_id = fields.Many2one(
        comodel_name='fondo_mi_vivienda.scenario_simulation',
        required=True
    )

    moneda_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        related="simulacion_escenario_id.moneda_id"
    )

    saldo_inicial = fields.Monetary(
        string="Saldo Inicial",
        currency_field="moneda_id",
        required=True
    )

    amortizacion = fields.Monetary(
        string="Amortización",
        currency_field="moneda_id",
        required=True
    )

    seguro_desgravamen = fields.Monetary(
        string="Seguro Desgravamen",
        currency_field="moneda_id",
        required=True
    )

    seguro_inmueble = fields.Monetary(
        string="Seguro de Inmueble",
        currency_field="moneda_id",
        required=True
    )

    saldo_final = fields.Monetary(
        string="Saldo Final",
        currency_field="moneda_id",
        required=True
    )

    pago_mensual = fields.Monetary(
        string="Pago Mensual",
        currency_field="moneda_id",
        required=True
    )