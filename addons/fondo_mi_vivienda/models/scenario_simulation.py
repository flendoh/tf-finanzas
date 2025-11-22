from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


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
        string="Proyecto Inmobiliario",
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
        string="Entidad Financiera",
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

    tem = fields.Float(
        string="TEM",
        related="producto_financiero_id.tem",
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

    cuota_mensual = fields.Float(
        string="Cuota Mensual",
        compute="_calcular_cuota_mensual",
        store=True,
    )

    monto_a_financiar = fields.Monetary(
        string="Monto a Financiar",
        currency_field="moneda_id",
        compute="_calcular_monto_a_financiar",
        store=True,
    )

    porcentaje_de_cuota_inicial = fields.Float(
        string="Porcentaje de Cuota Inicial",
        compute="_calcular_porcentaje_de_cuota_inicial",
        store=True,
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.depends('cuota_inicial', 'valor_vivienda')
    def _calcular_porcentaje_de_cuota_inicial(self):
        for r in self:
            r.porcentaje_de_cuota_inicial = r.cuota_inicial / r.valor_vivienda

    @api.depends('valor_vivienda', 'cuota_inicial')
    def _calcular_monto_a_financiar(self):
        for r in self:
            r.monto_a_financiar = r.valor_vivienda - r.cuota_inicial

    @api.constrains('plazo_meses')
    def _check_plazo_meses(self):
        for record in self:
            MIN_PLAZO_MESES = 60
            MAX_PLAZO_MESES = 300
            if record.plazo_meses < MIN_PLAZO_MESES or record.plazo_meses > MAX_PLAZO_MESES:
                raise ValidationError(f"El plazo debe ser como mínimo {MIN_PLAZO_MESES} meses y como máximo {MAX_PLAZO_MESES} meses.")

    def action_calculate_schedule(self):
        self.ensure_one()
        self.lineas_cronograma_cuota_ids.unlink()

        anterior = None

        cuota_mensual = self.cuota_mensual
        tem = self.tem
        valor_total = self.monto_a_financiar

        for mes in range(1, self.plazo_meses + 1):
            if anterior:
                saldo_inicial = anterior.saldo_final
                intereses = saldo_inicial * tem
                amortizacion = cuota_mensual - intereses
                saldo_final = saldo_inicial - amortizacion
            else:
                saldo_inicial = valor_total
                intereses = saldo_inicial * tem
                amortizacion = cuota_mensual - intereses
                saldo_final = saldo_inicial - amortizacion
            
            anterior = self.lineas_cronograma_cuota_ids.create({
                'saldo_inicial': saldo_inicial,
                'periodo': mes,
                'simulacion_escenario_id': self.id,
                'cuota_mensual': cuota_mensual,
                'saldo_final': saldo_final,
                'amortizacion': amortizacion,
                'intereses': intereses,
            })
    
    def action_export_pdf(self):
        return True
    
    @api.depends('monto_a_financiar', 'tem', 'plazo_meses')
    def _calcular_cuota_mensual(self):
        for r in self:
            numerador = r.tem * (1 + r.tem)**r.plazo_meses
            denominador = (1 + r.tem)**r.plazo_meses - 1
            
            if denominador == 0:
                continue
            
            cuota_mensual = r.monto_a_financiar * (numerador / denominador)
            
            r.write({
                'cuota_mensual': cuota_mensual
            })