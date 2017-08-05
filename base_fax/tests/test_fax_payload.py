# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import mock
import os
import __builtin__
import base64


model_file = 'openerp.addons.base_fax.models.fax_payload'
model = '%s.FaxPayload' % model_file
builtin = __builtin__  # Get rid of flake error for non-usage


class TestFaxPayload(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestFaxPayload, self).setUp(*args, **kwargs)
        self.model_obj = self.env['fax.payload']
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

    def _new_record(self):
        rec_id = self.model_obj.create(self.vals)
        self.image_vals['payload_id'] = rec_id.id
        self.page = self.env['fax.payload.page'].create(self.image_vals)
        return rec_id

    # Create

    @mock.patch('%s.convert_image' % model)
    @mock.patch('__builtin__.super')
    def _create_helper(self, super_mk, mk):
        mk.return_value = [self.vals['image']]
        with mock.patch.object(self.model_obj, 'env'):
            self.model_obj.create(self.vals)
            res = super_mk().create.call_args[0][0]
        return res, super_mk, mk

    @mock.patch('%s.convert_image' % model)
    def test_create_converts_image(self, mk):
        vals = {'image': 'Image', 'image_type': 'Type'}
        mk.side_effect = Exception
        try:
            self.model_obj.create(vals)
        except Exception:
            pass
        mk.assert_called_once_with(vals['image'], vals['image_type'])

    @mock.patch('%s.convert_image' % model)
    def test_create_enumerates_images(self, mk):
        vals = {'image': 'Image', 'image_type': 'Type'}
        mk().__iter__.side_effect = Exception
        try:
            self.model_obj.create(vals)
        except Exception:
            pass
        mk().__iter__.assert_called_once_with()

    def test_create_injects_page_ids(self):
        res, super_mk, mk = self._create_helper()
        expect = [
            (0, 0, {'name': '01.png', 'image': self.image_vals['image']})
        ]
        self.assertEqual(
            expect, res.get('page_ids'),
            'Page Ids was not inserted into vals. Expect "%s", Got "%s"' % (
                expect, res.get('page_ids'),
            )
        )

    def test_create_deletes_image_key(self):
        res, super_mk, mk = self._create_helper()
        self.assertNotIn(
            'image', res,
            'Image key was not deleted from vals. Got %s' % res
        )

    # Write

    @mock.patch('%s.copy' % model_file)
    def test_write_copies_vals(self, mk):
        mk.side_effect = Exception
        rec_id = self._new_record()
        expect = {'test': True}
        try:
            rec_id.write(expect)
        except Exception:
            pass
        mk.assert_called_once_with(expect)

    @mock.patch('%s.convert_image' % model)
    def test_write_converts_image_when_changed_type(self, mk):
        del self.vals['image']
        rec_id = self._new_record()
        vals = {'image_type': 'JPG'}
        mk.return_value = self.image_vals['image']
        rec_id.write(vals)
        mk.assert_called_once()

    @mock.patch('%s.convert_image' % model)
    def test_write_no_convert_image_when_same_type(self, mk):
        del self.vals['image']
        rec_id = self._new_record()
        vals = {'image_type': 'PNG'}
        rec_id.write(vals)
        mk.assert_not_called()

    @mock.patch('%s.convert_image' % model)
    def test_write_converts_new_image(self, mk):
        del self.vals['image']
        rec_id = self._new_record()
        vals = {'image': self.image_vals['image']}
        rec_id.write(vals)
        mk.assert_called_once_with(
            self.image_vals['image'], 'PNG',
        )

    @mock.patch('%s.convert_image' % model)
    def test_write_enumerates_converted_images(self, mk):
        del self.vals['image']
        rec_id = self.model_obj.create(self.vals)
        mk().__iter__.side_effect = Exception
        vals = {'image': self.image_vals['image']}
        try:
            rec_id.write(vals)
        except Exception:
            pass
        mk().__iter__.assert_called_once_with()
