# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from datetime import datetime
from json import dumps
import logging


_logger = logging.getLogger(__name__)


class DataException(Exception):
    error = None
    description = None
    status = 500
    headers = {}

    def __init__(self):
        super(DataException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }

    def __str__(self, ):
        return dumps(self.to_dict())


class AuthenticationException(Exception):
    error = None
    description = None
    status = 400
    headers = {}

    def __init__(self):
        super(AuthenticationException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }


class InvalidTokenException(AuthenticationException):
    status = 403
    error = 'invalid_token'
    description = 'Invalid token provided in request'


class MultipleTransmissionException(DataException):
    error = 'multiple_transmission'
    description = 'Multiple transmissions found matching provided FaxID'


class NoTransmissionException(DataException):
    status = 404
    error = 'no_transmission'
    description = 'No transmission found matching provided FaxID'


class NoOperationException(DataException):
    error = 'noop_error'
    description = 'Server error, no operation was triggered'


class FaxSfaxCallback(http.Controller):

    def __throw_error(self, exception):
        return http.Response(
            str(exception),
            exception.status,
            exception.headers,
        )

    def __ok(self, ):
        return http.Response(
            'OK',
            200,
        )

    @http.route('/fax/sfax/callback', type='http', auth='none')
    def do_callback(self, token, **kwargs):

        transmission_mdl = http.request.env['fax.transmission'].sudo()
        transmission_id = transmission_mdl.search([
            ('response_num', '=', kwargs.get('faxid', None))
        ])

        if len(transmission_id) > 1:
            return self.__throw_error(MultipleTransmissionException())

        if len(transmission_id) == 0:
            sfax_ids = http.request.env['fax.adapter'].sudo().search([
                ('adapter_model_name', '=', 'fax.adapter.sfax')
            ])
        else:
            sfax_ids = transmission_id.adapter_id

        sfax_id = None
        for sfax in sfax_ids:
            if sfax._get_adapter().validate_token(token):
                sfax_id = sfax
                break

        if sfax_id is None:
            return self.__throw_error(AuthenticationException())

        kwargs['faxdateiso'] = datetime.strptime(
            kwargs['faxdateiso'], '%Y-%m-%dT%H:%M:%SZ'
        )

        if kwargs.get('outfromfaxnumber'):
            self.process_out_fax(sfax_id, transmission_id, kwargs)
            return self.__ok()
        else:
            self.process_in_fax(sfax_id, transmission_id, kwargs)
            return self.__ok()

        return self.__throw_error(NoOperationException())

    def process_in_fax(self, sfax_id, transmission_id, vals):
        transmission_vals = {
            'local_fax': vals.get('intofaxnumber'),
            'remote_fax': vals.get('infromfaxnumber'),
            'state': 'done' if vals['faxsuccess'] else 'transmit_except',
            'timestamp': vals['faxdateiso'],
            'direction': 'in',
            'attempt_num': 1,
            'page_num': vals['faxpages'],
            'status_msg': 'OK',
            'response_num': vals['faxid'],
        }
        self.save_transmission(sfax_id, transmission_id, transmission_vals)

    def process_out_fax(self, sfax_id, transmission_id, vals):
        transmission_vals = {
            'local_fax': vals.get('outfromfaxnumber'),
            'remote_fax': vals.get('outtofaxnumber'),
            'state': 'done' if vals['faxsuccess'] else 'transmit_except',
            'timestamp': vals['faxdateiso'],
            'direction': 'out',
            'attempt_num': vals['outfaxattempts'],
            'page_num': vals['faxpages'],
            'status_msg': vals['outresultdescr'],
            'response_num': vals['faxid'],
        }
        self.save_transmission(sfax_id, transmission_id, transmission_vals)

    def save_transmission(self, sfax_id, transmission_id, transmission_vals):
        if len(transmission_id) == 0:
            _logger.debug('Creating new transmission - %s', transmission_vals)
            sfax_id.write({
                'transmission_ids': [(0, 0, transmission_vals)],
            })
            for i in reversed(sfax_id.transmission_ids):
                _logger.debug(
                    '%s == %s?',
                    i.response_num, transmission_vals['response_num']
                )
                if i.response_num == transmission_vals['response_num']:
                    transmission_id = i
                    break
        else:
            _logger.debug('Updating %s', transmission_id)
            transmission_id.write(transmission_vals)
        if transmission_id and not len(transmission_id.payload_ids):
            transmission_id.adapter_id.action_fetch_payloads(transmission_id)
