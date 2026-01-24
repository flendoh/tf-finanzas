import logging
from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)

class OrderWebhookController(http.Controller):
    @route('/webhook/order/created/<int:account_id>/<string:token>', 
                type='http', auth='none', methods=['POST'], csrf=False)
    def handle_create_webhook(self, account_id, token):
        try:
            current_user = request.env.ref('base.user_root')
            account = request.env(user=current_user.id)['market.account'].sudo().browse(account_id)

            if not account.exists():
                _logger.warning('Webhook authentication failed: Account %s not found', account_id)
                return request.make_json_response({'error': 'Unauthorized'}, status=401)
            
            if not account.order_webhook_enabled:
                _logger.warning('Webhook authentication failed: Webhook disabled for account %s', account_id)
                return request.make_json_response({'error': 'Unauthorized'}, status=401)
            
            if account.order_webhook_token != token:
                _logger.warning('Webhook authentication failed: Invalid token for account %s', account_id)
                return request.make_json_response({'error': 'Unauthorized'}, status=401)
            

            data = request.httprequest.get_json(silent=True) or {}
            
            account.handle_create_webhook(data)
            
            return request.make_json_response({'status': 'ok'}, status=201)
            
        except Exception as e:
            _logger.error('Error processing webhook for account %s: %s', account_id, str(e))
            return request.make_json_response({'error': 'Internal Server Error'}, status=500)