from odoo import models, fields, api
import uuid
import logging
import json

_logger = logging.getLogger(__name__)

class MarketAccount(models.Model):
    _inherit = 'market.account'

    team_id = fields.Many2one(
        'crm.team',
        string="Equipo de Ventas",
        help="Equipo de Ventas asginado para los reportes.",
        check_company=True,
    )

    order_ids = fields.One2many(
        "sale.order",
        "marketplace_account_id",
        string="Órdenes",
        help="Lista de todas las órdenes de venta asociadas a esta cuenta de marketplace",
        check_company=True,
        readonly=True
    )

    orders_count = fields.Integer(
        string='Órdenes de Marketplace',
        compute='_compute_orders_count',
    )
    
    order_created_weebhook_url = fields.Char(
        string="URL del Webhook de Órdenes Creadas",
        help="URL completa donde el marketplace enviará las notificaciones de nuevas órdenes",
        compute='_compute_order_webhook_url',
        readonly=True,
        store=False,
        groups="conexiomarket_core.group_market_connector_manager"
    )
    
    order_webhook_token = fields.Char(
        string="Token de Seguridad para Webhooks de Órdenes",
        help="Token único para validar las solicitudes del webhook de órdenes del marketplace",
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        required=True,
        groups="conexiomarket_core.group_market_connector_manager"
    )
    
    order_webhook_enabled = fields.Boolean(
        string="Habilitar Webhook de Órdenes",
        help="Activa o desactiva la recepción automática de notificaciones de órdenes del marketplace",
        default=False,
        
    )
    
    partner_category_id = fields.Many2one(
        'res.partner.category',
        string="Categoría de Partners",
        help="Categoría opcional que se asignará automáticamente a los partners creados desde órdenes de este marketplace",
    )

    create_product_if_not_found = fields.Boolean(
        string="Crear Producto si No Existe",
        help="Si está activado, se creará un producto automáticamente si no se encuentra en Odoo al procesar una orden.",
        default=False
    )

    # Features
    feature_order_document = fields.Boolean(
        string="Soporta Documentos de Orden",
        compute="_compute_features",
        help="Indica si este backend soporta la descarga de documentos de orden (etiquetas, facturas, etc.)"
    )

    feature_open_marketplace_url = fields.Boolean(
        string="Soporta URL de Orden",
        compute="_compute_features",
        help="Indica si este backend soporta redirigir a la URL de la orden en el marketplace"
    )
    
    @api.depends('order_webhook_token')
    def _compute_order_webhook_url(self):
        """Generar dinámicamente la URL del webhook de órdenes"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.order_webhook_token and base_url:
                record.order_created_weebhook_url = f"{base_url}/webhook/order/created/{record.id}/{record.order_webhook_token}"
            else:
                record.order_created_weebhook_url = False
    
    @api.depends('order_ids')
    def _compute_orders_count(self):
        for order in self:
            order.orders_count = len(order.order_ids)

    def regenerate_order_webhook_token(self):
        """Regenerar el token del webhook de órdenes"""
        self.ensure_one()
        self.order_webhook_token = str(uuid.uuid4())
        return True
    
    def _compute_features(self):
        """ Compute supported features based on backend type. """
        for account in self:
            account.feature_order_document = False
            account.feature_open_marketplace_url = False
    
    def action_view_orders(self):
        """Abrir vista de órdenes para esta cuenta"""
        self.ensure_one()
        return {
            'name': f'Órdenes Obtenidas',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'context': {
                'create': False
            },
            'domain': [('marketplace_account_id', '=', self.id)],
            'target': 'current',
            'help': 'Órdenes de venta obtenidas automáticamente del marketplace. No se pueden crear manualmente.'
        }
    
    def handle_create_webhook(self, payload):
        """ Recibe el payload y lo encola en market.webhook.entry """
        self.ensure_one()
        
        self.env['market.webhook.entry'].sudo().create({
            'account_id': self.id,
            'state': 'draft',
            'payload': json.dumps(payload, indent=4),
            'model_id': self.env.ref('sale.model_sale_order').id,
        })

        _logger.info(f"Webhook encolado para cuenta {self.name}")