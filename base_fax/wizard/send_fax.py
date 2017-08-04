# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class SendFax(models.TransientModel):
    _name = 'fax.send.fax'
    _description = 'Wizard to send faxes'
    # _inherit = ['phone.common']
    _phone_name_sequence = 10
    _country_field = 'country_id'
    _partner_field = None
    _phone_fields = ['fax_to_number']

    fax_to_number = fields.Char(
        string='Fax To',
        help='Phone number of remote fax machine',
    )
    adapter_id = fields.Many2one(
        'fax.adapter',
        default=lambda s: s._default_session(),
    )
    name = fields.Char(
        string="Fax Name",
    )
    image = fields.Binary(
        attachment=True,
    )
    country_id = fields.Many2one(
        'res.country',
        default=lambda s: s.env.user.company_id.country_id
    )

    @api.model
    def _default_session(self, ):
        return self.env['fax.adapter'].browse(self._context.get('active_id'))

    @api.multi
    def action_send(self, ):
        for rec_id in self:
            payload_id = self.env['fax.payload'].create({
                'name': rec_id.name,
                'image': rec_id.image,
                'image_type': 'PNG',
            })
            # number = self._generic_reformat_phonenumbers({
            #     'fax_to_number': rec_id.fax_to_number,
            # })
            # number = number['fax_to_number']
            # _logger.debug('Got number %s reformatted to %s',
            #               self.fax_to_number, number)
            # dialable = self.convert_to_dial_number(number)
            # send_name = self.get_name_from_phone_number(number)
            dialable = None
            send_name = None
            rec_id.adapter_id.action_send(dialable, payload_id, send_name)
