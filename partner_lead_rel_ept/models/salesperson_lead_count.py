from odoo import fields, models, api


class SalespersonLeadCount(models.Model):
    _name = 'salesperson.lead.count'
    _description = 'Sales Person Lead Count'

    user_id = fields.Many2one(comodel_name='res.users', string='SalesPerson Name',
                              help='Name of SalesPerson', default=lambda self: self.env.user)
    saleperson_lead_id = fields.Many2one(comodel_name='partner.lead.rel.ept', string='Salespersons lead')
    number_of_pipeline = fields.Integer(string='Number of Pipelines',
                                        help='Number of pipeline of that salesperson')
    Total_revenue = fields.Float(string='Total Revenue', help='total revenue of leads of salesperson',
                                 )
    number_of_quotations = fields.Float(string='Number of Quotations',
                                        help='Total number of quotations created from this lead',
                                        )
    number_of_sale_order = fields.Float(string='Number of SaleOrder',
                                        help='Total number of sales orders created from this lead',
                                        )
    total_amount = fields.Float(string='Sum of Total Amount',
                                help='sum of total order amounts of all those sales orders')
    percentage = fields.Float(string='Percentage of Conversation Amount',
                              help='percentage of conversation amount from expected revenue to sales order total amount')
