# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Landed Cost Custom',
    'version': '2.0',
    'category': 'Inventory',
    'author': 'Bhargavi Kompelli',
    'complexity': 'easy',
    'website': '',
    'description': """""",
    'depends': ['base','purchase','stock_landed_costs','stock','product','account'],
    'data': [
        'views/account.xml',
        
    ],
#    'qweb': [
#        'static/src/xml/doctor.xml'
#    ],    
    
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

