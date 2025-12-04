from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Dossier(models.Model):
    _name = 'fondo_mi_vivienda.dossier'
    _description = 'Expediente'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, index=True, default=lambda self: 'Nuevo Expediente')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo Expediente') == 'Nuevo Expediente':
            vals['name'] = self.env['ir.sequence'].next_by_code('fondo_mi_vivienda.dossier') or 'Nuevo Expediente'
        return super(Dossier, self).create(vals)

    estado = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Califica'),
            ('closed', 'No Califica'),
        ],
        default='draft',
    )

    cliente_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True
    )

    ingreso_financiero = fields.Monetary(
        string="Ingreso financiero mensual",
        currency_field="moneda_id",
        compute="_compute_ingreso_financiero",
        store=True,
        readonly=True
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

    es_vivienda_sostenible = fields.Boolean(string='¿La vivienda es sostenible?', related="proyecto_id.es_vivienda_sostenible")

    ha_recibido_apoyo_habitacional_antes = fields.Boolean(
        string="¿Ha recibido apoyo habitacional antes?",
        related="cliente_id.ha_recibido_apoyo_habitacional_antes"
    )

    total_bbp = fields.Monetary(string='Total BBP', currency_field='moneda_id', compute="_compute_bbp_values", store=True)

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
        compute="_compute_valor_vivienda",
        store=True,
        readonly=True
    )

    @api.depends('cliente_id', 'moneda_id', 'moneda_id.rate_ids', 'cliente_id.moneda_id', 'cliente_id.ingreso_financiero')
    def _compute_ingreso_financiero(self):
        for r in self:
            if r.cliente_id and r.moneda_id:
                r.ingreso_financiero = r.cliente_id.moneda_id._convert(
                    r.cliente_id.ingreso_financiero,
                    r.moneda_id,
                    r.env.company,
                    fields.Date.today()
                )
            else:
                r.ingreso_financiero = 0.0

    @api.depends('proyecto_id', 'moneda_id', 'moneda_id.rate_ids', 'proyecto_id.moneda_id', 'proyecto_id.valor_vivienda')
    def _compute_valor_vivienda(self):
        for r in self:
            if r.proyecto_id and r.moneda_id:
                if r.proyecto_id.moneda_id != r.moneda_id:
                    r.valor_vivienda = r.proyecto_id.moneda_id._convert(
                        r.proyecto_id.valor_vivienda,
                        r.moneda_id,
                        r.env.company,
                        fields.Date.today()
                    )
                else:
                    r.valor_vivienda = r.proyecto_id.valor_vivienda
            else:
                r.valor_vivienda = r.valor_vivienda or 0.0

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

    tipo_periodo_gracia = fields.Selection(
        string="Tipo de Periodo de Gracia",
        selection=[
            ('total', 'Total'),
            ('parcial', 'Parcial'),
        ],
        help="Total: No se pagan intereses ni amortización (se capitalizan). Parcial: Se pagan solo intereses."
    )

    periodo_gracia_meses = fields.Integer(
        string="Meses de Periodo de Gracia",
        default=0,
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

    otros_gastos_iniciales = fields.Monetary(
        string="Otros Gastos Iniciales",
        currency_field="moneda_id",
        related="producto_financiero_id.otros_gastos_iniciales",
        help="Gastos adicionales como administrativos, notariales, registrales o de tasación. Este monto se suma automáticamente al capital del préstamo."
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.depends('cuota_inicial', 'valor_vivienda')
    def _calcular_porcentaje_de_cuota_inicial(self):
        for r in self:
            if r.valor_vivienda == 0:
                continue
            r.porcentaje_de_cuota_inicial = r.cuota_inicial / r.valor_vivienda

    @api.depends('valor_vivienda', 'cuota_inicial', 'total_bbp', 'otros_gastos_iniciales')
    def _calcular_monto_a_financiar(self):
        for r in self:
            r.monto_a_financiar = r.valor_vivienda - r.cuota_inicial - r.total_bbp + r.otros_gastos_iniciales

    @api.constrains('plazo_meses', 'periodo_gracia_meses')
    def _check_plazo_meses(self):
        for record in self:
            MIN_PLAZO_MESES = 60
            MAX_PLAZO_MESES = 300
            if record.plazo_meses < MIN_PLAZO_MESES or record.plazo_meses > MAX_PLAZO_MESES:
                raise ValidationError(f"El plazo debe ser como mínimo {MIN_PLAZO_MESES} meses y como máximo {MAX_PLAZO_MESES} meses.")
            if record.periodo_gracia_meses >= record.plazo_meses:
                raise ValidationError("El periodo de gracia debe ser menor al plazo total del crédito.")
            if record.periodo_gracia_meses < 0:
                raise ValidationError("El periodo de gracia no puede ser negativo.")

    def action_calculate_schedule(self):
        self.ensure_one()
        self.lineas_cronograma_cuota_ids.unlink()

        anterior = None

        cuota_full = self.cuota_mensual # Esta es la cuota a pagar después de la gracia
        tasa = self.tem
        valor_total = self.monto_a_financiar
        seguro_inmueble_mensual = (self.seguro_de_inmueble_anual * self.valor_vivienda) / 12

        for mes in range(1, self.plazo_meses + 1):
            if anterior:
                saldo_inicial = anterior.saldo_final
            else:
                saldo_inicial = valor_total

            intereses = saldo_inicial * tasa
            seguro_desgravamen = saldo_inicial * self.seguro_desgravamen_mensual
            
            # Lógica de Periodo de Gracia
            es_periodo_gracia = mes <= self.periodo_gracia_meses
            
            if es_periodo_gracia:
                amortizacion = 0.0
                if self.tipo_periodo_gracia == 'total':
                    # Gracia Total: Interés se capitaliza. Cuota solo seguros.
                    # El cliente paga solo seguros (Desgravamen + Inmueble)
                    cuota_mes = seguro_desgravamen + seguro_inmueble_mensual
                    saldo_final = saldo_inicial + intereses # Capitalización de intereses
                else:
                    # Gracia Parcial: Se paga interés + seguros. Saldo se mantiene.
                    cuota_mes = intereses + seguro_desgravamen + seguro_inmueble_mensual
                    saldo_final = saldo_inicial
            else:
                # Periodo Normal
                cuota_mes = cuota_full
                amortizacion = cuota_mes - intereses - seguro_desgravamen - seguro_inmueble_mensual
                saldo_final = saldo_inicial - amortizacion
            
            anterior = self.lineas_cronograma_cuota_ids.create({
                'saldo_inicial': saldo_inicial,
                'periodo': mes,
                'expediente_id': self.id,
                'cuota_mensual': cuota_mes,
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
    
    @api.depends('monto_a_financiar', 'tem', 'plazo_meses', 'seguro_desgravamen_mensual', 'seguro_de_inmueble_anual', 'valor_vivienda', 'tipo_periodo_gracia', 'periodo_gracia_meses')
    def _calcular_cuota_mensual(self):
        for r in self:
            tasa_mensual = r.tem + r.seguro_desgravamen_mensual
            
            if r.plazo_meses <= r.periodo_gracia_meses:
                r.cuota_mensual = 0.0
                continue
                
            plazo_restante = r.plazo_meses - r.periodo_gracia_meses
            numerador = tasa_mensual * (1 + tasa_mensual)**plazo_restante
            denominador = (1 + tasa_mensual)**plazo_restante - 1
            
            if denominador == 0:
                continue

            saldo_a_financiar = r.monto_a_financiar

            # Ajustar saldo según tipo de gracia
            if r.tipo_periodo_gracia == 'total' and r.periodo_gracia_meses > 0:
                # En gracia total, los intereses se capitalizan durante el periodo de gracia
                # Saldo futuro = Saldo actual * (1 + tasa)^periodo
                # Nota: Usamos la tasa pura (TEM) para capitalizar intereses, no la tasa con seguros.
                # Sin embargo, si el seguro de desgravamen también se capitaliza, se usaría la combinada.
                # Asumiremos estándar: Solo intereses se capitalizan.
                saldo_a_financiar = r.monto_a_financiar * ((1 + r.tem)**r.periodo_gracia_meses)
            
            # Calcular la cuota constante para el periodo restante
            cuota_financiera = saldo_a_financiar * (numerador / denominador)
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
        
        producto = self.producto_financiero_id
        cliente = self.cliente_id
        errores = []

        # 1. Verificar Plazo
        if producto.plazo_minimo > 0 and self.plazo_meses < producto.plazo_minimo:
            errores.append(f"El plazo ({self.plazo_meses} meses) es menor al mínimo permitido ({producto.plazo_minimo} meses)")
        
        if producto.plazo_maximo > 0 and self.plazo_meses > producto.plazo_maximo:
            errores.append(f"El plazo ({self.plazo_meses} meses) excede el máximo permitido ({producto.plazo_maximo} meses)")

        # 2. Verificar Ingreso Mínimo
        if producto.ingreso_minimo > 0:
            if cliente.ingreso_financiero < producto.ingreso_minimo:
                errores.append(f"El ingreso del cliente ({cliente.ingreso_financiero}) es menor al mínimo requerido ({producto.ingreso_minimo})")

        # 3. Verificar Periodo de Gracia
        if producto.maximo_periodo_gracia > 0 and self.periodo_gracia_meses > producto.maximo_periodo_gracia:
            errores.append(f"El periodo de gracia ({self.periodo_gracia_meses} meses) excede el máximo permitido ({producto.maximo_periodo_gracia} meses)")

        if errores:
            self.write({'estado': 'closed'})
            mensaje = "El cliente NO CALIFICA para este producto financiero por las siguientes razones: " + ", ".join(errores)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Evaluación Completada: No Califica',
                    'message': mensaje,
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        self.write({
            'estado': 'done',
        })

    @api.depends('valor_vivienda', 'es_vivienda_sostenible', 'aplicar_a_bbp_integrador', 'ha_recibido_apoyo_habitacional_antes', 'moneda_id')
    def _compute_bbp_values(self):
        for r in self:
            if r.ha_recibido_apoyo_habitacional_antes:
                r.total_bbp = 0.0
                continue

            company_currency = r.env.company.currency_id
            v = r.proyecto_id.valor_vivienda
            if r.moneda_id and r.proyecto_id.moneda_id != company_currency:
                v = r.moneda_id._convert(v, company_currency, r.env.company, fields.Date.today())

            # Determinar rango
            if 68800 <= v <= 98100:
                rango = "R1"
            elif 98100 < v <= 146900:
                rango = "R2"
            elif 146900 < v <= 244600:
                rango = "R3"
            elif 244600 < v <= 362100:
                rango = "R4"
            elif 362100 < v <= 488800:
                rango = "R5"
            else:
                r.total_bbp = 0
                continue

            # tabla de fmvivienda
            tabla_bbp = {
                "R1": {
                    "trad": 27400,
                    "sost": 33700,
                    "int_trad": 31000,
                    "int_sost": 37300,
                },
                "R2": {
                    "trad": 22800,
                    "sost": 29100,
                    "int_trad": 26400,
                    "int_sost": 32700,
                },
                "R3": {
                    "trad": 20900,
                    "sost": 27200,
                    "int_trad": 24500,
                    "int_sost": 30800,
                },
                "R4": {
                    "trad": 7800,
                    "sost": 14100,
                    "int_trad": 11400,
                    "int_sost": 17700,
                },
                "R5": {
                    "trad": 0,
                    "sost": 0,
                    "int_trad": 0,
                    "int_sost": 0,
                }
            }

            # tipo
            if r.aplicar_a_bbp_integrador:
                tipo = "int_sost" if r.es_vivienda_sostenible else "int_trad"
            else:
                tipo = "sost" if r.es_vivienda_sostenible else "trad"

            bbp_base = tabla_bbp[rango][tipo]

            # Bono integrador adicional
            bbp_adicional = 0
            if r.aplicar_a_bbp_integrador:
                bbp_adicional = 3600

            # Total - Convertir de vuelta a la moneda del expediente
            total_bbp = bbp_base + bbp_adicional
            if r.moneda_id and r.moneda_id != company_currency:
                r.total_bbp = company_currency._convert(total_bbp, r.moneda_id, r.env.company, fields.Date.today())
            else:
                r.total_bbp = total_bbp