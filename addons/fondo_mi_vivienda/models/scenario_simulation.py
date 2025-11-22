from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ScenarioSimulation(models.Model):
    _name = 'fondo_mi_vivienda.scenario_simulation'
    _description = 'Simulación de Escenario'

    name = fields.Char(string='Nombre', required=True)

    estado = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Hecho'),
        ],
        default='draft',
    )

    cliente_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True
    )

    proyecto_id = fields.Many2one(
        comodel_name="fondo_mi_vivienda.project",
        string="Proyecto Vivienda",
        required=True
    )

    aplicar_a_bbp_integrador = fields.Boolean(
        string="¿Aplicar a BBP Integrador?",
        help="(5) Personas vulnerables en los grupos: Personas de menores ingresos, adultos mayores, personas con discapacidad, personas desplazadas, migrantes retornados.",
        related="cliente_id.aplicar_a_bbp_integrador"
    )

    ha_recibido_apoyo_habitacional_antes = fields.Boolean(
        string="¿Ha recibido apoyo habitacional antes?",
        related="cliente_id.ha_recibido_apoyo_habitacional_antes"
    )

    producto_financiero_id = fields.Many2one(
        comodel_name="fondo_mi_vivienda.financial_product",
        string="Producto Financiero",
        required=True
    )

    moneda_id = fields.Many2one(
        related="producto_financiero_id.moneda_id",
        string="Moneda",
    )

    tea = fields.Float(
        string="TEA",
        related="producto_financiero_id.tea",
    )

    valor_vivienda = fields.Monetary(
        string="Valor de la Vivienda",
        currency_field="moneda_id",
        required=True,
        related="proyecto_id.valor_vivienda"
    )

    cuota_inicial = fields.Monetary(
        string="Cuota Inicial",
        currency_field="moneda_id",
        required=True
    )

    lineas_cronograma_cuota_ids = fields.One2many(
        comodel_name="fondo_mi_vivienda.fee_schedule_line",
        inverse_name="simulacion_escenario_id",
        string="Cronograma de Cuotas",
    )

    plazo_meses = fields.Integer(
        string="Plazo (meses)",
        required=True,
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.constrains('plazo_meses')
    def _check_plazo_meses(self):
        for record in self:
            MIN_PLAZO_MESES = 60
            MAX_PLAZO_MESES = 300
            if record.plazo_meses < MIN_PLAZO_MESES or record.plazo_meses > MAX_PLAZO_MESES:
                raise ValidationError(f"El plazo debe ser como mínimo {MIN_PLAZO_MESES} meses y como máximo {MAX_PLAZO_MESES} meses.")

    def action_calculate_schedule(self):
        return True
    
    def action_export_pdf(self):
        return True