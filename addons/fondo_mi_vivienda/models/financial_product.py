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
    _description = 'Producto Financiero'

    name = fields.Char(string='Nombre', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    rate_type = fields.Selection([
        ('nominal', 'Nominal'),
        ('effective', 'Efectiva')
    ], string='Tipo de Tasa', required=True)

    #Opciones TN
    nominal_rate_period = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Periodo de Tasa')

    nominal_rate_capitalization = fields.Selection([
        ('daily', 'Diaria'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Capitalización de Tasa', default='daily')

    #Opciones TE
    effective_rate_period = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi-annual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Periodo de Tasa')

    rate_value = fields.Float(string='Valor de la Tasa (%)')

    tea = fields.Float(string='Tasa Efectiva Anual (%)', compute='_compute_tea', store=True, readonly=True)
    tem = fields.Float(string='Tasa Efectiva Mensual (%)', compute='_compute_tem', store=True, readonly=True)

    active = fields.Boolean(string='Active', default=True)

    @api.depends('rate_value', 'rate_type', 'nominal_rate_period', 'nominal_rate_capitalization', 'effective_rate_period')
    def _compute_tea(self):
        for record in self:
            tea = None

            if record.rate_type == 'nominal':
                nominal_period = PERIOD_DAYS.get(record.nominal_rate_period, 0)
                nominal_cap_period = PERIOD_DAYS.get(record.nominal_rate_capitalization, 0)

                tea = self._n_rate_to_effective_rate(record.rate_value, nominal_period, nominal_cap_period, 360)

            elif record.rate_type == 'effective':
                e_period = PERIOD_DAYS.get(record.effective_rate_period, 0)
                
                tea = self._e_rate_to_effective_rate(record.rate_value, e_period, 360)

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