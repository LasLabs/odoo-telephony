# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import models, fields, api
from copy import copy
from PIL import Image, ImageSequence
from io import BytesIO


_logger = logging.getLogger(__name__)


class FaxPayload(models.Model):

    _name = 'fax.payload'
    _description = 'Fax Data Payload'

    name = fields.Char(
        index=True,
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
        index=True,
        required=True,
        default=lambda s: s.env['ir.sequence'].next_by_code(
            'fax.payload',
        ),
        help='Automatically generated sequence.',
    )
    _sql_constraints = [
        ('ref_uniq', 'UNIQUE(ref)', 'Each ref must be unique.'),
    ]

    @api.model
    def create(self, vals):
        """ Override Create method, inject a pages using `image`.

        Args:
            vals['image'] (str): Raw image data, will convert to page_ids.
        Returns:
            FaxPayload: New payload record.
        """
        try:
            images = self.convert_image(
                vals['image'], vals['image_type'],
            )
            vals['page_ids'] = []
            for idx, img in enumerate(images):
                vals['page_ids'].append((0, 0, {
                    'name': '%02d.png' % (idx + 1),
                    'image': img,
                }))
            del vals['image']
        except KeyError:
            _logger.debug('No images were included in the payload.')
        return super(FaxPayload, self).create(vals)

    @api.multi
    def write(self, vals):
        """Override write to allow for image type conversions and pages.

        Args:
            vals['image_type'] (str): Will convert existing pages if needed.
            vals['image'] (str): Raw image data, will add as page_ids.
        """
        for record in self:
            _vals = copy(vals)
            if _vals.get('image'):
                _vals['page_ids'] = []
                image_type = _vals.get('image_type') or record.image_type
                images = record.convert_image(
                    _vals['image'], image_type,
                )
                for idx, img in enumerate(images):
                    _vals['page_ids'].append((0, 0, {
                        'name': '%02d.png' % (idx + 1),
                        'image': img,
                    }))
                del _vals['image']
            elif _vals.get('image_type'):
                if record.image_type != _vals['image_type']:
                    for img in record.page_ids:
                        img.image = record.convert_image(
                            img.image, _vals['image_type'],
                        )
            super(FaxPayload, record).write(_vals)

    @api.multi
    def action_send(self, adapter_id, fax_number):
        """Sends fax using specified adapter.

        Args:
            adapter_id (FaxAdapter): to use
            fax_number (str): Number to fax to

        Returns:
            FaxTransmission: Transmission records that were generated.
        """
        transmissions = self.env['fax.transmission'].browse()
        for record in self:
            transmissions += adapter_id.action_send(fax_number, record)
        return transmissions

    @api.model
    def convert_image(self, image, image_type, b64_out=True, b64_in=True):
        """Generator for converting image for storage and use by the fax adapter.

        Each iteration of the generator represents a page of the input image.

        Args:
            image (str): Raw image data
            image_type (str): Name of the image format (valid formats avail in
            **FaxPayload.image_type**)
            b64_out (bool): False if the output data should be binary, True if
            base64 encoded binary.
            b64_in (bool): False if the input data is binary. True if base64
            encoded binary.

        Yields:
            str: Raw image data.
        """
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
