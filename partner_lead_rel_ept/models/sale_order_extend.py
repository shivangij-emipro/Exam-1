from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_paid_invoice_amount = fields.Float(string='Total Paid ', help='Total Paid invoice Amount',
                                             compute='compute_total_paid_invoice_amount')
    remaining_payment = fields.Float(string='Remaining amount ', compute='compute_remaining_payment',
                                     help='Remaining amount = Total amount - total paid invoice amount')

    def compute_total_paid_invoice_amount(self):
        """
        This method is written for calculate total paid amount of invoices
        """
        self.total_paid_invoice_amount = 0
        for order in self:
            for invoices in order.invoice_ids:
                order.total_paid_invoice_amount = invoices.amount_total - invoices.amount_residual

    def compute_remaining_payment(self):
        """
        This method is written for calculate order's remaining amount of invoice
        """
        self.remaining_payment = 0
        for order in self:
            order.remaining_payment = order.amount_total - order.total_paid_invoice_amount