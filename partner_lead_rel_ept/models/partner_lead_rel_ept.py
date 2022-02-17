from datetime import date

from odoo import fields, models, api


class PartnerLeadRelEpt(models.Model):
    _name = 'partner.lead.rel.ept'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Partner Lead Relation Ept'

    name = fields.Char(string='Name Of Partner', help="Partner's Name", readonly=True, default='New')
    from_date = fields.Date(string='From Date', help="From Date of lead timing")
    to_date = fields.Date(string='To Date', help='To Date of lead timing')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', help='Res partner')
    partner_contact_ids = fields.Many2many(comodel_name='res.partner', string="Partner's Contacts",
                                           help="Contacts of partners")
    salesperson_lead_count_ids = fields.One2many(comodel_name='salesperson.lead.count',
                                                 inverse_name='saleperson_lead_id',
                                                 string='Lead count of Salesperson',
                                                 help='Number of leads done by particular Salesperson')
    lead_ids = fields.Many2many(comodel_name='crm.lead', string='Leads', help="Leads of Partner")
    total_revenue = fields.Float(string='Total Revenue', help='Total Revenue of partner', digits=(6, 2),
                                 compute='compute_total_revenue')
    pipelines_count = fields.Float(compute='_compute_pipelines_count', string='Pipelines',
                                   help='Counter of pipelines')

    def compute_total_revenue(self):
        """
        This method is written for calculate total revenue.
        """
        self.total_revenue = 0
        for partner in self:
            for lead in partner.lead_ids:
                partner.total_revenue += lead.expected_revenue

    @api.depends('lead_ids')
    def _compute_pipelines_count(self):
        """
        This method is written for count how many pipelines are there and display the counter of the that.
        """
        self.pipelines_count = 0
        self.pipelines_count = len(self.lead_ids) if self.lead_ids else 0

    @api.model
    def create(self, vals):
        """
        Here I override create method for maintaining sequence of the records.
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('partner.lead.rel.ept') or 'New'
        return super(PartnerLeadRelEpt, self).create(vals)

    def create_lead(self):
        """
        This method is created for creating lead at time of click button - Get pipeline details
        and this method is call from that button's click event
        """
        leads = []
        partners = [self.partner_id.id]
        for contact in self.partner_contact_ids.ids:
            partners.append(contact)
        crm_lead = self.env['crm.lead'].search(
            [('partner_id', 'in', partners)])
        for lead in crm_lead:
            leads.append((0, 0, {
                'name': lead.name,
                'contact_name': lead.contact_name,
                'email_from': lead.email_from,
                'phone': lead.phone,
                'expected_revenue': lead.expected_revenue,
                'stage_id': lead.stage_id.id
            }))
        self.lead_ids = leads

    def get_pipeline_details(self):
        """
        This method is created for get pipeline details
        for that purpose first I called create_lead method which create for creating leads
        then create lines for sales_person_lead_count_ids
        """
        self.create_lead()
        salesperson_list = []
        quotation = 0
        order = 0
        total_revenue = 0
        total_amount = 0
        for lead in self.lead_ids:
            total_amount += lead.expected_revenue
            if lead.filtered(lambda line: line.stage_id.is_won == False):
                quotation += 1
            if lead.filtered(lambda line: line.stage_id.is_won == True):
                order += 1
            total_revenue += lead.filtered(lambda line: line.stage_id.is_won == True).expected_revenue
            if lead.user_id.id not in salesperson_list:
                salesperson_list.append(lead.user_id.id)
                self.env['salesperson.lead.count'].create({
                    'saleperson_lead_id': self.id,
                    'number_of_pipeline': 1,
                    'number_of_quotations': quotation,
                    'number_of_sale_order': order,
                    'Total_revenue': total_revenue,
                    'total_amount': total_amount
                })
            elif lead.user_id.id in salesperson_list:
                for id in self.salesperson_lead_count_ids:
                    if id.user_id.id == lead.user_id.id:
                        id.number_of_pipeline = id.number_of_pipeline + 1
                        id.number_of_quotations = quotation
                        id.number_of_sale_order = order
                        id.Total_revenue = total_revenue
                        id.total_amount = total_amount

    def view_leads(self):
        """
        This method is created for fetching kanban view and form view of crm lead model
        """
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_all_leads")
        domain = [('partner_id', '=', self.partner_id.id)]
        if self.from_date and self.to_date:
            domain = [('partner_id', '=', self.partner_id.id),
                      ('date_deadline', '>=', self.from_date),
                      ('date_deadline', '<=', self.to_date)]
        elif not self.to_date:
            domain = [('partner_id', '=', self.partner_id.id),
                      ('date_deadline', '>=', self.from_date),
                      ('date_deadline', '<=', fields.Date.today())]
        action['domain'] = domain
        action['views'] = [(self.env.ref('crm.crm_lead_view_form').id, 'form')]
        action['views'] = [(self.env.ref('crm.view_crm_lead_kanban').id, 'kanban')]
        action['res_id'] = self.partner_id.id
        return action

    def view_paid_orders(self):
        """
        This method is created for fetching form view and tree view of sale order model
        """
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['domain'] = [('partner_id', '=', self.partner_id.id),
                            ('invoice_status', '=', 'invoiced')]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['views'] = [(self.env.ref('sale.view_order_tree').id, 'list')]
        action['res_id'] = self.partner_id.id
        return action
