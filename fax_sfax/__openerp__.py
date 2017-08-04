# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Extension of base_fax providing SFax bindings',
    'version': '9.0.1.0.0',
    'category': 'Fax',
    'author': "LasLabs",
    'license': 'LGPL-3',
    'website': 'https://laslabs.com',
    'depends': [
        'base_fax',
    ],
    'data': [
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
    ],
    "external_dependencies": {
        "python": [
            'Crypto',
        ],
        "bin": [],
    },
    'installable': False,
    'application': False,
}
