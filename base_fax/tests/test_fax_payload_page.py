# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import mock
import os
import base64


model_file = 'openerp.addons.base_fax.models.fax_payload_page'
model = '%s.FaxPayloadPage' % model_file


class TestFaxPayloadPage(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestFaxPayloadPage, self).setUp(*args, **kwargs)
        self.model_obj = self.env['fax.payload.page']
        with open(os.path.join(
            os.path.dirname(__file__), '..', 'static', 'description',
            'icon.png',
        ), 'rb') as fh:
            image = base64.b64encode(fh.read())
        self.vals = {
            'image_type': 'PNG',
            'image': image,
        }
        self.image_vals = {
            'name': 'Test Image',
            'image': image,
        }

    @mock.patch('%s.tools' % model_file)
    def _new_record(self, mk):
        for i in ['image_resize_image_big', 'image_resize_image',
                  'image_resize_image_medium']:
            getattr(mk, i).return_value = self.image_vals['image']
        rec_id = self.env['fax.payload'].create(self.vals)
        self.image_vals['payload_id'] = rec_id.id
        self.page_id = self.model_obj.create(self.image_vals)
        return rec_id, mk

    def test_compute_images_xl(self):
        rec_id, mk = self._new_record()
        mk.image_resize_image_big.assert_called_with(
            self.page_id.image
        )

    def test_compute_images_lg(self):
        rec_id, mk = self._new_record()
        mk.image_resize_image.assert_called_with(
            self.page_id.image, (384, 384), 'base64', None, True
        )

    def test_compute_images_med(self):
        rec_id, mk = self._new_record()
        mk.image_resize_image_medium.assert_called_with(
            self.page_id.image
        )
