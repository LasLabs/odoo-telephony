# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Odoo Faxing Core',
    'version': '10.0.1.0.0',
    'category': 'Fax',
    'author': "LasLabs",
    'license': 'LGPL-3',
    'website': 'https://laslabs.com',
    'data': [
        'security/fax_security.xml',
        'security/ir.model.access.csv',
        'views/fax_payload_view.xml',
        'views/fax_transmission_view.xml',
        'views/res_company_view.xml',
        'views/fax_menus.xml',
        'wizard/send_fax_view.xml',
        'data/ir_sequence.xml',
    ],
    'depends': [
        'base',
    ],
    'installable': True,
    'application': False,
}
