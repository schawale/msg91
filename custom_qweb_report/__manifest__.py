# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Q-Web Custom Report',
    'description': """

""",
    "version": "1.1",
    "license": "AGPL-3",
    'author': "",
    'category': 'Accounting',
    'author': 'Bhargavi Kompelli',
    'complexity': 'easy',
    'depends': ['account'],
    'data': [   
                'report/extended_layout.xml',
                'report/report.xml',
                'report/invoice_report.xml',
                'views/res_company_view.xml',
             ],
    # tests order matter
    'test': [
             ],
    'active': False,
    'installable': True,
    'application': True,
}
