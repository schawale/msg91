# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Q-Web Custom Report Sales',
    'description': """

""",
    "version": "1.1",
    "license": "AGPL-3",
    'author': "",
    'category': 'Sales',
    'author': 'Bhargavi Kompelli',
    'complexity': 'easy',
    'depends': ['account','sale','laxicon_payment_extend'],
    'data': [   
                'report/extended_layout.xml',
                'report/sale_report.xml',
                'report/report.xml',
                'views/res_company_view.xml',
             ],
    # tests order matter
    'test': [
             ],
    'active': True,
    'installable': True,
    'application': True,
}
