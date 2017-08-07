# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
import mock


model_file = 'openerp.addons.base_fax.models.fax_adapter'
model = '%s.FaxAdapter' % model_file


class TestFaxAdapter(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestFaxAdapter, self).setUp(*args, **kwargs)
        self.model_obj = self.env['fax.adapter']
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1
        )
        self.test_adapter = self.env['res.partner'].search([], limit=1)
        self.vals = {
            'name': 'Test Adapter',
            'adapter_model_id': self.test_model.id,
            'adapter_pk': self.test_adapter.id,
        }

    def _new_record(self):
        return self.model_obj.create(self.vals)

    def test_compute_adapter_name(self):
        rec_id = self._new_record()
        self.assertEqual(
            self.test_adapter.name, rec_id.adapter_name,
            'Adapter name computed incorrectly. Expect "%s", Got "%s"' % (
                self.test_adapter.name, rec_id.adapter_name
            )
        )

    def testget_adapter(self):
        rec_id = self._new_record()
        res = rec_id.get_adapter()
        self.assertEqual(
            self.test_adapter, res,
            'Did not return correct adapter. Expect %s, Got %s' % (
                self.test_adapter, res,
            )
        )

    @mock.patch('%s.get_adapter' % model)
    def test_action_fetch_payloads(self, mk):
        rec_id = self._new_record()
        expect = ['Payloads']
        rec_id.action_fetch_payloads(expect)
        mk().action_fetch_payloads.assert_called_once_with(expect)

    @mock.patch('%s.get_adapter' % model)
    def test_action_send_passthru(self, mk):
        rec_id = self._new_record()
        expect = ['dialable', ['payload_ids'], 'send_name']
        mk().action_send.side_effect = Exception  # Stops the write
        try:
            rec_id.action_send(*expect)
        except Exception:
            pass
        mk().action_send.assert_called_once_with(*expect)

    @mock.patch('%s.get_adapter' % model)
    @mock.patch('%s.write' % model)
    def test_action_send_write(self, write_mk, mk):
        rec_id = self._new_record()
        expect = 'Expect'
        mk().action_send.return_value = expect
        rec_id.action_send(0, 0, 0)
        write_mk.assert_called_once_with(
            {'transmission_ids': [(0, 0, expect)]}
        )
