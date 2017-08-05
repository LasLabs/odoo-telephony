# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, tools


class FaxPayloadPage(models.Model):

    _name = 'fax.payload.page'
    _description = 'Fax Payload Page'

    name = fields.Char(
        help='Name of image',
        store=True,
        index=True,
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
        required=True,
    )

    @api.multi
    @api.depends('image')
    def _compute_images(self):
        for record in self:
            record.image_xlarge = tools.image_resize_image_big(
                record.image,
            )
            record.image_large = tools.image_resize_image(
                record.image, (384, 384), 'base64', None, True,
            )
            record.image_medium = tools.image_resize_image_medium(
                record.image,
            )
