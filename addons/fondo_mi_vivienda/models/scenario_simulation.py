from odoo import models, fields, api


class ScenarioSimulation(models.Model):
    _name = 'fondo_mi_vivienda.scenario_simulation'
    _description = 'Simulación de Escenario'

    name = fields.Char(string='Nombre', required=True)

    state = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Hecho'),
        ],
        default='draft',
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True
    )

    project_id = fields.Many2one(
        comodel_name="fondo_mi_vivienda.project",
        string="Proyecto Vivienda",
        required=True
    )

    apply_to_bbp_integrator = fields.Boolean(
        string="¿Aplicar a BBP Integrador?",
        help="(5) Personas vulnerables en los grupos: Personas de menores ingresos, adultos mayores, personas con discapacidad, personas desplazadas, migrantes retornados.",
        related="partner_id.apply_to_bbp_integrator"
    )

    has_received_housing_support_before = fields.Boolean(
        string="¿Ha recibido apoyo habitacional antes?",
        related="partner_id.has_received_housing_support_before"
    )

    financial_product_id = fields.Many2one(
        comodel_name="fondo_mi_vivienda.financial_product",
        string="Producto Financiero",
        required=True
    )

    currency_id = fields.Many2one(
        related="financial_product_id.currency_id",
        string="Moneda",
    )

    tea = fields.Float(
        string="TEA",
        related="financial_product_id.tea",
    )

    property_value = fields.Monetary(
        string="Valor de la Vivienda",
        currency_field="currency_id",
        required=True,
        related="project_id.property_value"
    )

    down_payment = fields.Monetary(
        string="Cuota Inicial",
        currency_field="currency_id",
        required=True
    )

    fee_schedule_line_ids = fields.One2many(
        comodel_name="fondo_mi_vivienda.fee_schedule_line",
        inverse_name="scenario_simulation_id",
        string="Cronograma de Cuotas",
    )

    active = fields.Boolean(string='Activo', default=True)

    def action_calculate_schedule(self):
        return True
    
    def action_export_pdf(self):
        return True