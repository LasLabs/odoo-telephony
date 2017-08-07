# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    fax_adapter_ids = fields.One2many(
        string='Fax Adapters',
        comodel_name='fax.adapter',
        inverse_name='company_id',
        help='Company that adapter is associated with',
    )
