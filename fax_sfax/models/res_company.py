# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    sfax_adapter_ids = fields.One2many(
        string='SFax Adapters',
        comodel_name='fax.adapter.sfax',
        inverse_name='company_id',
        help='Company that adapter is associated with',
    )
