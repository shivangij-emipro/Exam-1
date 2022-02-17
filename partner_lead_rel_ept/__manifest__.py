{
    'name': 'Partner Lead Management',
    'version': '1.1',
    'category': 'utility',
    'description': """
    This module contains all the data about relations between Partners""",
    'depends': ['sale_crm', 'sales_team'],
    'data': ['security/ir.model.access.csv',
             'data/sequence.xml',
             'views/partner_lead_rel_ept.xml',
             'views/sales_person_count.xml',
             'views/sale_order_extend.xml'],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False
}
