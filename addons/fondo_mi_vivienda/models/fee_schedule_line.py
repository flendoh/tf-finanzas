from odoo import models, fields, api


class FeeScheduleLine(models.Model):
    _name = 'fondo_mi_vivienda.fee_schedule_line'
    _description = 'Linea de Cronograma de Cuotas'
    _rec_name = 'periodo'

    periodo = fields.Integer(string='Periodo', required=True)

    expediente_id = fields.Many2one(
        comodel_name='fondo_mi_vivienda.dossier',
        required=True,
        ondelete='cascade'
    )

    moneda_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        related="expediente_id.moneda_id"
    )

    saldo_inicial = fields.Float(
        string="Saldo Inicial",
    )

    amortizacion = fields.Float(
        string="Amortización",
    )

    intereses = fields.Float(
        string="Intereses",
    )

    seguro_desgravamen = fields.Float(
        string="Seguro Desgravamen",
    )

    seguro_inmueble = fields.Float(
        string="Seguro de Inmueble",
    )

    saldo_final = fields.Float(
        string="Saldo Final",
    )

    cuota_mensual = fields.Float(
        string="Cuota Mensual",
    )