from odoo import models, fields, api
import base64
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def attach_documents(self):
        """
        Busca y adjunta documentos relevantes para el despacho (Facturas, Etiquetas Marketplace, Guías).
        Devuelve una lista de strings describiendo los documentos adjuntados.
        """
        invalid_orders = self.filtered(lambda o: o.state != 'sale')
        if invalid_orders:
            raise UserError("Solo se pueden adjuntar documentos a pedidos en estado 'Confirmado'")

        for order in self:
            attached_docs_log = []
            
            # 1. Adjuntar Facturas
            attached_docs_log.extend(order._attach_invoices())

            # 2. Adjuntar Documentos del Marketplace
            attached_docs_log.extend(order._attach_marketplace_documents())

            # 3. Adjuntar Guías de Remisión
            #attached_docs_log.extend(order._attach_picking_documents())

            if attached_docs_log:
                order.message_post(
                    body="Documentos adjuntados:<ul>" + "".join([f"<li>{doc}</li>" for doc in attached_docs_log]) + "</ul>",
                    subtype_xmlid="mail.mt_note", 
                    body_is_html=True
                )

    def _create_pdf_attachment(self, name, pdf_content):
        """Helper para crear adjuntos PDF"""
        return self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    def _attach_invoices(self):
        """Procesa y adjunta facturas publicadas"""
        logs = []
        report = self.env.ref('account.account_invoices', raise_if_not_found=False)
        if not report:
            _logger.warning("Reporte 'account.account_invoices' no encontrado.")
            return logs

        for invoice in self.invoice_ids.filtered(lambda i: i.state == 'posted'):
            try:
                attachment_name = f"Factura_{invoice.name.replace('/', '_')}.pdf"

                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report, invoice.ids)
                self._create_pdf_attachment(attachment_name, pdf_content)
                logs.append(f"Factura: {invoice.name}")
            except Exception as e:
                _logger.error(f"Error adjuntando factura {invoice.name}: {e}")
                self.message_post(body=f"Error al adjuntar factura {invoice.name}: {str(e)}", subtype_xmlid="mail.mt_note")
        return logs

    def _attach_marketplace_documents(self):
        """Procesa y adjunta documentos del conector de marketplace"""
        logs = []
        if not self.marketplace_account_id or not self.marketplace_account_id.feature_order_document:
            return logs

        account = self.marketplace_account_id
        try:
            self.action_get_marketplace_document()
            logs.append("Documento Marketplace")
        except Exception as e:
            error_msg = f"Error obteniendo documentos del Marketplace ({account.name}): {str(e)}"
            _logger.error(error_msg)
            self.message_post(body=error_msg, subtype_xmlid="mail.mt_note")
        return logs

    def _attach_picking_documents(self):
        """Procesa y adjunta guías de remisión electrónicas"""
        logs = []
        if not self.picking_ids:
            return logs

        report_eguide = self.env.ref('solse_pe_cpe_guias.action_guia_electronica', raise_if_not_found=False)
        if not report_eguide:
            _logger.warning("Reporte de guía electrónica no encontrado.")
            return logs

        for picking in self.picking_ids.filtered(lambda i: i.state == 'done' and i.pe_is_eguide):
            try:
                attachment_name = f"Guía_{picking.name.replace('/', '_')}.pdf"

                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_eguide, picking.ids)
                self._create_pdf_attachment(attachment_name, pdf_content)
                logs.append(f"Guía Remision: {picking.name}")
            except Exception as e:
                _logger.error(f"Error adjuntando guía {picking.name}: {e}")
                self.message_post(body=f"Error al adjuntar guía {picking.name}: {str(e)}", subtype_xmlid="mail.mt_note")
        return logs
    
    def create_activity_for_warehouse_manager(self):
        for order in self:
            invalid_orders = self.filtered(lambda o: o.state != 'sale')
            if invalid_orders:
                raise UserError("Solo se pueden alistar pedidos en estado 'Confirmado'")

            assignee = order.company_id.warehouse_manager_id or order.user_id
            order_name = order.marketplace_order_number or order.name
            deadline = order.marketplace_shipping_deadline or order.commitment_date
            deadline_str = deadline.strftime('%Y-%m-%d %H:%M') if deadline else '-'
            sale_channel = order.sale_channel_id.name if order.sale_channel_id else '-'
            summary = f"Nueva orden por alistar: {order_name}"
            
            details = [
                f"Orden: {order_name}",
                f"Cliente: {order.partner_id.name}",
                f"Fecha Límite Envío: {deadline_str}",
                f"Camal de venta: {sale_channel}",
            ]
                
            order.activity_schedule('mail.mail_activity_data_todo', user_id=assignee.id, summary=summary, note="<br>".join(details))