from odoo import models
import traceback
import logging

_logger = logging.getLogger(__name__)

class MarketEventQueue(models.Model):
    _inherit = "market.event.queue"

    def action_process(self):
        # Filtrar eventos de productos
        product_events = self.filtered(lambda r: r.model_id.model == 'product.template' and r.state == 'pending')
        
        for event in product_events:
            event.write({'state': 'processing'})
            try:
                # TODO: Implementar llamada real al ProductManager
                # account = event.account_id
                # with account.work_on("product.template") as work:
                #     manager = work.component(usage="product.manager")
                #     manager.export(event.res_id, event.event_type)
                
                # Stub temporal
                _logger.info(f"Procesando evento de producto: {event.name}")
                
                event.write({
                    'state': 'done',
                    'log_notes': f"{event.log_notes or ''}\n[OK] Evento procesado (Stub)."
                })
                
            except Exception as e:
                tb = traceback.format_exc()
                _logger.error(f"Error procesando evento {event.id}: {str(e)}")
                event.write({
                    'state': 'failed',
                    'log_notes': f"{event.log_notes or ''}\n[ERROR] {str(e)}\n{tb}",
                    'retry_count': event.retry_count + 1
                })
        
        # Continuar con el resto de eventos
        super(MarketEventQueue, self - product_events).action_process()
