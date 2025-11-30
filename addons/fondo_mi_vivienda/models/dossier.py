from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Dossier(models.Model):
    _name = 'fondo_mi_vivienda.dossier'
    _description = 'Expediente'

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

    tcea = fields.Float(
        string="TCEA",
        compute="_calcular_tcea",
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
        inverse_name="expediente_id",
        string="Cronograma de Cuotas",
        readonly=True
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

    #Seguros
    seguro_desgravamen_mensual = fields.Float(
        string="Seguro Desgravamen Mensual",
        related="producto_financiero_id.seguro_desgravamen_mensual",
    )

    seguro_de_inmueble_anual = fields.Float(
        string="Seguro de Inmueble Anual",
        related="producto_financiero_id.seguro_de_inmueble_anual",
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.depends('cuota_inicial', 'valor_vivienda')
    def _calcular_porcentaje_de_cuota_inicial(self):
        for r in self:
            if r.valor_vivienda == 0:
                continue
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
        tasa = self.tem
        valor_total = self.monto_a_financiar
        seguro_inmueble_mensual = (self.seguro_de_inmueble_anual * self.valor_vivienda) / 12

        for mes in range(1, self.plazo_meses + 1):
            if anterior:
                saldo_inicial = anterior.saldo_final
                intereses = saldo_inicial * tasa
                seguro_desgravamen = saldo_inicial * self.seguro_desgravamen_mensual
                amortizacion = cuota_mensual - intereses - seguro_desgravamen - seguro_inmueble_mensual
                saldo_final = saldo_inicial - amortizacion
            else:
                saldo_inicial = valor_total
                intereses = saldo_inicial * tasa
                seguro_desgravamen = saldo_inicial * self.seguro_desgravamen_mensual
                amortizacion = cuota_mensual - intereses - seguro_desgravamen - seguro_inmueble_mensual
                saldo_final = saldo_inicial - amortizacion
            
            anterior = self.lineas_cronograma_cuota_ids.create({
                'saldo_inicial': saldo_inicial,
                'periodo': mes,
                'expediente_id': self.id,
                'cuota_mensual': cuota_mensual,
                'saldo_final': saldo_final,
                'amortizacion': amortizacion,
                'intereses': intereses,
                'seguro_desgravamen': seguro_desgravamen,
                'seguro_inmueble': seguro_inmueble_mensual,
            })
    
    def action_export_pdf(self):
        self.ensure_one()
        if not self.lineas_cronograma_cuota_ids:
            raise ValidationError("No hay datos de cronograma para exportar.")
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'fondo_mi_vivienda.report_dossier',
            'report_type': 'qweb-pdf',
            'report_file': 'fondo_mi_vivienda.report_dossier',
            'name': f'Cronograma_{self.name}_{fields.Date.today()}',
            'datas': {
                'ids': [self.id],
                'model': 'fondo_mi_vivienda.dossier',
            },
        }
    
    def action_view_schedule_graph(self):
        self.ensure_one()
        return {
            'name': 'Gráfico de Cronograma',
            'type': 'ir.actions.act_window',
            'res_model': 'fondo_mi_vivienda.fee_schedule_line',
            'view_mode': 'graph',
            'view_id': self.env.ref('fondo_mi_vivienda.view_fee_schedule_line_graph').id,
            'domain': [('expediente_id', '=', self.id)],
            'target': 'current',
        }
    
    @api.depends('monto_a_financiar', 'tem', 'plazo_meses', 'seguro_desgravamen_mensual', 'seguro_de_inmueble_anual', 'valor_vivienda')
    def _calcular_cuota_mensual(self):
        for r in self:
            tasa = r.tem + r.seguro_desgravamen_mensual
            numerador = tasa * (1 + tasa)**r.plazo_meses
            denominador = (1 + tasa)**r.plazo_meses - 1
            
            if denominador == 0:
                continue

            c = r.monto_a_financiar
            
            cuota_financiera = c * (numerador / denominador)
            seguro_inmueble_mensual = (r.seguro_de_inmueble_anual * r.valor_vivienda) / 12
            
            r.write({
                'cuota_mensual': cuota_financiera + seguro_inmueble_mensual
            })
    
    @api.depends('cuota_mensual', 'monto_a_financiar', 'plazo_meses')
    def _calcular_tcea(self):
        for r in self:
            if r.monto_a_financiar <= 0 or r.cuota_mensual <= 0 or r.plazo_meses <= 0:
                r.tcea = 0.0
                continue

            # Búsqueda binaria para encontrar la TIR mensual
            # P = C * ((1 - (1+i)^-n) / i)
            P = r.monto_a_financiar
            C = r.cuota_mensual
            n = r.plazo_meses
            
            low = 0.0
            high = 1.0
            i = 0.0
            
            for _ in range(100):
                i = (low + high) / 2
                if i == 0:
                    vp = C * n
                else:
                    vp = C * ((1 - (1 + i)**-n) / i)
                
                if abs(vp - P) < 0.001:
                    break
                
                if vp > P:
                    # Si VP calculado es mayor, necesitamos descontar más (tasa más alta)
                    low = i
                else:
                    high = i
            
            # Anualizar la TIR mensual para obtener la TCEA
            r.tcea = (1 + i)**12 - 1

    def action_confirmar(self):
        self.ensure_one()
        if not self.lineas_cronograma_cuota_ids:
            raise ValidationError("No hay datos de cronograma para confirmar.")
        self.write({
            'estado': 'done',
        })
