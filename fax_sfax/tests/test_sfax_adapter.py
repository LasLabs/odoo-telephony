# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
import time
import logging

from odoo.tools.misc import mute_logger
from odoo.tests.common import TransactionCase


_logger = logging.getLogger(__name__)


model_file = 'openerp.addons.fax_sfax.models.fax_adapter_sfax'
model = '%s.FaxAdapterSfax' % model_file


class TestFaxAdapterSfax(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestFaxAdapterSfax, self).setUp(*args, **kwargs)
        self.model_obj = self.env['fax.adapter.sfax']
        self.return_encoded = 'TestEncoded'.encode('base64')
        self.vals = {
            'name': 'Test Adapter',
            'username': 'Username',
            'encrypt_key': b'4p7*Zw5Fc5ijUtWEFuMVh(Hfh^as*HsU',
            'vector': 't72e*wJVXr8BrRTE',
            'api_key': 'B273E072A8R8489A9A3F08692212E1CF',
            'uri': 'http://example.com/api',
            'company_id': self.env.user.company_id.id,
        }

    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def _new_record(self, pkcs_mk, aes_mk):
        aes_mk.new().encrypt().encode.return_value = self.return_encoded
        return self.model_obj.create(self.vals), aes_mk, pkcs_mk

    def _new_token(self, expired=False, add_str=''):
        if expired:
            timestr = '2015-12-01T12:00:00Z'
        else:
            timestr = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        token = 'Username=%(uname)s&ApiKey=%(key)s&GenDT=%(time)s&' % {
            'uname': self.vals['username'],
            'key': self.vals['api_key'],
            'time': timestr,
        }
        token = '%s%s' % (token, add_str)
        return token.encode('base64')

    @mock.patch('%s.requests' % model_file)
    def _new_call(self, mk, *args, **kwargs):
        rec_id, _, _ = self._new_record()
        return rec_id._call_api(*args, **kwargs), mk
    #
    # def test_compute_token_inits_aes(self):
    #     rec_id, mk, _ = self._new_record()
    #     self.assertTrue(rec_id.token)
    #     mk.new.assert_called_with(
    #         self.vals['encrypt_key'],
    #         mk.MODE_CBC,
    #         self.vals['vector'],
    #     )
    #
    # def test_compute_token_encrypts_encoded(self):
    #     rec_id, aes_mk, mk = self._new_record()
    #     self.assertTrue(rec_id.token)
    #     aes_mk.new().encrypt.assert_called_with(mk().encode())
    #
    # def test_compute_token_base64_encodes_cipher(self):
    #     rec_id, _, mk = self._new_record()
    #     self.assertTrue(rec_id.token)
    #     mk().encrypt().encode.assert_called_with('base64')
    #
    # def test_compute_token_sets_token(self):
    #     rec_id, _, _ = self._new_record()
    #     self.assertEqual(
    #         self.return_encoded, rec_id.token
    #     )
    #
    # def test_compute_token_unknown_exception(self):
    #     rec_id, mk, _ = self._new_record()
    #     mk.new.side_effect = Exception
    #     rec_id.token = False
    #     rec_id._compute_token()
    #     self.assertFalse(
    #         rec_id.token,
    #         'Did not correctly handle token generation exception. Got %s' % (
    #             rec_id.token,
    #         ),
    #     )

    # _validate_token()

    @mute_logger(
        'odoo.addons.fax_sfax.models.fax_adapter_sfax',
    )
    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def test_validate_token_expired(self, pkcs_mk, aes_mk):
        rec_id, _, _ = self._new_record()
        token = self._new_token(True)
        pkcs_mk().decode.return_value = token.decode('base64')
        res = rec_id.validate_token(token)
        self.assertFalse(
            res,
            'Did not fail for expired token. Got %s' % res,
        )

    @mute_logger(
        'odoo.addons.fax_sfax.models.fax_adapter_sfax',
    )
    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def test_validate_token_bad_user(self, pkcs_mk, aes_mk):
        rec_id, _, _ = self._new_record()
        self.vals['username'] = 'NoExist'
        token = self._new_token()
        pkcs_mk().decode.return_value = token.decode('base64')
        res = rec_id.validate_token(token)
        self.assertFalse(
            res,
            'Did not fail for bad Username in token. Got %s' % res,
        )

    @mute_logger(
        'odoo.addons.fax_sfax.models.fax_adapter_sfax',
    )
    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def test_validate_token_bad_api_key(self, pkcs_mk, aes_mk):
        rec_id, _, _ = self._new_record()
        self.vals['api_key'] = 'NoExist'
        token = self._new_token()
        pkcs_mk().decode.return_value = token.decode('base64')
        res = rec_id.validate_token(token)
        self.assertFalse(
            res,
            'Did not fail for bad Api Key in token. Got %s' % res,
        )

    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def test_validate_token_good(self, pkcs_mk, aes_mk):
        rec_id, _, _ = self._new_record()
        token = self._new_token()
        pkcs_mk().decode.return_value = token.decode('base64')
        res = rec_id.validate_token(token)
        self.assertTrue(
            res,
            'Did not return True for valid token. Got %s' % res,
        )

    @mock.patch('%s.AES' % model_file)
    @mock.patch('%s.PKCS7Encoder' % model_file)
    def test_validate_token_handles_empty_vals(self, pkcs_mk, aes_mk):
        """ No error should be raised here """
        rec_id, _, _ = self._new_record()
        token = self._new_token(add_str='EmptyVal=&')
        pkcs_mk().decode.return_value = token.decode('base64')
        rec_id.validate_token(token)
        self.assertTrue(True)

    # _call_api

    def test_call_api_post(self):
        action = 'action'
        uri_params = {
            'test': '123',
        }
        post_data = {
            'test_post': 'this is a post',
        }
        files = ['Files']
        json = True
        self._new_call(
            action=action,
            uri_params=uri_params,
            post=post_data,
            files=files,
            json=json,
        )
