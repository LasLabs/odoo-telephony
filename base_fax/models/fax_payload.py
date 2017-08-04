# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from copy import copy
from PIL import Image, ImageSequence
from io import BytesIO


class FaxPayload(models.Model):
    _name = 'fax.payload'
    _description = 'Fax Data Payload'

    name = fields.Char(
        select=True,
        help='Name of payload',
    )
    image_type = fields.Selection(
        [
            ('PNG', 'PNG'),
            ('JPG', 'JPG'),
            ('BMP', 'BMP'),
            ('GIF', 'GIF'),
            ('TIF', 'TIFF'),
        ],
        default='PNG',
        required=True,
        string='Image Format',
        help='Store image as this format',
    )
    transmission_ids = fields.Many2many(
        string='Transmissions',
        comodel_name='fax.transmission',
        inverse_name='payload_ids',
    )
    page_ids = fields.One2many(
        string='Pages',
        comodel_name='fax.payload.page',
        inverse_name='payload_id',
        ondelete='cascade',
    )
    ref = fields.Char(
        readonly=True,
        select=True,
        required=True,
        help='Automatically generated sequence.',
    )
    _sql_constraints = [
        ('ref_uniq', 'UNIQUE(ref)', 'Each ref must be unique.')
    ]

    @api.model
    def create(self, vals, ):
        '''
        Override Create method, inject a sequence ref and pages using `image`

        Params:
            vals['image']: str Raw image data, will convert to page_ids
        '''
        if vals.get('image'):
            images = self.action_convert_image(
                vals['image'], vals['image_type']
            )
            vals['page_ids'] = []
            for idx, img in enumerate(images):
                vals['page_ids'].append((0, 0, {
                    'name': '%02d.png' % (idx + 1),
                    'image': img,
                }))
            del vals['image']  # Suppress invalid col warning
        vals['ref'] = self.env['ir.sequence'].next_by_code(
            'fax.payload'
        )
        return super(FaxPayload, self).create(vals)

    @api.multi
    def write(self, vals, ):
        '''
        Override write to allow for image type conversions and page appends

        Params:
            vals['image_type']: str Will convert existing pages if needed
            vals['image']: str Raw image data, will add as page_ids
        '''
        for rec_id in self:
            _vals = copy(vals)
            if _vals.get('image'):
                _vals['page_ids'] = []
                image_type = _vals.get('image_type') or rec_id.image_type
                images = rec_id.action_convert_image(
                    _vals['image'], image_type
                )
                for idx, img in enumerate(images):
                    _vals['page_ids'].append((0, 0, {
                        'name': '%02d.png' % (idx + 1),
                        'image': img,
                    }))
                del _vals['image']  # < The warning was killing my OCD
            elif _vals.get('image_type'):
                if rec_id.image_type != _vals['image_type']:
                    for img in rec_id.page_ids:
                        img.image = rec_id.action_convert_image(
                            img.image, _vals['image_type']
                        )
            super(FaxPayload, rec_id).write(vals)

    @api.multi
    def action_send(self, adapter_id, fax_number, ):
        '''
        Sends fax using specified adapter

        Params:
            adapter_id: fax.adapter to use
            fax_number: str Number to fax to

        Returns:
            :class:``fax.transmission`` Representing fax transmission
        '''
        for rec_id in self:
            return adapter_id.action_send(fax_number, rec_id)

    @api.model
    def action_convert_image(self, image, image_type,
                             b64_out=True, b64_in=True):
        '''
        Convert image for storage and use by the fax adapter

        Params:
            image:  str Raw image data (binary or base64)
            image_type: str
            b64_out: bool
            b64_in: bool

        Yields:
            list Of base64 encoded raw image data
        '''
        binary = image.decode('base64') if b64_in else image
        with BytesIO(binary) as raw_image:
            image = Image.open(raw_image)
            # prevent IOError: PIL doesn't support alpha for some formats
            if image_type in ['BMP', 'PDF']:
                if len(image.split()) == 4:
                    r, g, b, a = image.split()
                    image = Image.merge("RGB", (r, g, b))
            for frame in ImageSequence.Iterator(image):
                with BytesIO() as raw:
                    frame.save(raw, image_type)
                    val = raw.getvalue()
                    if b64_out:
                        val = val.encode('base64')
                    yield val
