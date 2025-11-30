from odoo import models, fields, api

PERIOD_DAYS = {
    'daily': 1,
    'monthly': 30,
    'quarterly': 90,
    'semi-annual': 180,
    'annual': 360
}

class FinancialProduct(models.Model):
    _name = 'fondo_mi_vivienda.financial_product'
    _description = 'Entidad Financiera'

    name = fields.Char(string='Nombre', required=True)
    moneda_id = fields.Many2one('res.currency', string='Moneda', required=True)
    tipo_tasa = fields.Selection([
        ('nominal', 'Nominal'),
        ('effective', 'Efectiva')
    ], string='Tipo de Tasa', required=True)

    #Opciones TN
    periodo_tasa_nominal = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Periodo de Tasa')

    capitalizacion_tasa_nominal = fields.Selection([
        ('daily', 'Diaria'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Capitalización de Tasa', default='daily')

    #Opciones TE
    periodo_tasa_efectiva = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Periodo de Tasa', default='monthly')

    valor_tasa = fields.Float(string='Valor de la Tasa (%)')

    tea = fields.Float(string='Tasa Efectiva Anual (%)', compute='_compute_tea', store=True, readonly=True)
    tem = fields.Float(string='Tasa Efectiva Mensual (%)', compute='_compute_tem', store=True, readonly=True)

    #Seguros y Gastos
    seguro_desgravamen_mensual = fields.Float(string='Seguro Desgravamen Mensual', required=True)
    seguro_de_inmueble_anual = fields.Float(string='Seguro de Inmueble Anual', required=True)
    otros_gastos_iniciales = fields.Monetary(
        string='Otros Gastos Iniciales',
        required=True,
        currency_field='moneda_id',
        help="Gastos adicionales como administrativos, notariales, registrales o de tasación. Este monto se suma automáticamente al capital del préstamo."
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.depends('valor_tasa', 'tipo_tasa', 'periodo_tasa_nominal', 'capitalizacion_tasa_nominal', 'periodo_tasa_efectiva')
    def _compute_tea(self):
        for record in self:
            tea = None
            if record.tipo_tasa == 'nominal':
                if not record.periodo_tasa_nominal or not record.capitalizacion_tasa_nominal:
                    continue

                nominal_period = PERIOD_DAYS.get(record.periodo_tasa_nominal, 0)
                nominal_cap_period = PERIOD_DAYS.get(record.capitalizacion_tasa_nominal, 0)

                tea = self._n_rate_to_effective_rate(record.valor_tasa, nominal_period, nominal_cap_period, 360)

            elif record.tipo_tasa == 'effective':
                if not record.periodo_tasa_efectiva:
                    continue
                e_period = PERIOD_DAYS.get(record.periodo_tasa_efectiva, 0)
                
                tea = self._e_rate_to_effective_rate(record.valor_tasa, e_period, 360)

            record.tea = tea
    
    @api.depends('tea')
    def _compute_tem(self):
        for record in self:
            record.tem = self._e_rate_to_effective_rate(record.tea, 360, 30)
    
    def _e_rate_to_effective_rate(self, e_rate, e_period, effective_period):
        """
        Convierte una tasa efectiva a una tasa efectiva.

        :param e_rate: Tasa efectiva.
        :param e_period: Período de la tasa efectiva.
        :param effective_period: Período de la tasa efectiva para el cálculo.
        :return: TEP.
        """
        return (1+e_rate)**(effective_period/e_period) - 1
    
    def _n_rate_to_effective_rate(self, n_rate, n_period, n_cap_period, effective_period):
        """
        Convierte una tasa nominal a una tasa efectiva.

        :param n_rate: Tasa nominal.
        :param n_period: Período de la tasa nominal.
        :param n_cap_period: Período de capitalización de la tasa nominal.
        :param effective_period: Período de la tasa efectiva para el cálculo.
        :return: TEP.
        """
        m = n_period/n_cap_period
        n = effective_period/n_cap_period
        return (1+n_rate/m)**(n) - 1