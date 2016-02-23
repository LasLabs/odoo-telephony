# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools


class FaxPayloadPage(models.Model):
    _name = 'fax.payload.page'
    _description = 'Fax Payload Page'

    name = fields.Char(
        help='Name of image',
        store=True,
        select=True,
    )
    image = fields.Binary(
        string='Fax Image',
        attachment=True,
        readonly=True,
        required=True,
    )
    image_xlarge = fields.Binary(
        string='XLarge Image (1024x1024)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    image_large = fields.Binary(
        string='Large Image (384x384)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    image_medium = fields.Binary(
        string='Medium Image (128x128)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    payload_id = fields.Many2one(
        string='Payload',
        comodel_name='fax.payload',
        inverse_name='page_ids',
    )

    @api.multi
    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_xlarge = tools.image_resize_image_big(rec.image)
            rec.image_large = tools.image_resize_image(
                rec.image, (384, 384), 'base64', None, True
            )
            rec.image_medium = tools.image_resize_image_medium(rec.image)
