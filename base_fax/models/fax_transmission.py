# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class FaxTransmission(models.Model):
    _name = 'fax.transmission'
    _description = 'Fax Transmission Record'
    # _inherit = ['phone.common']
    _phone_fields = ['remote_fax', 'local_fax']
    _phone_name_sequence = 10
    _country_field = None
    _partner_field = None

    remote_fax = fields.Char(
        select=True,
    )
    local_fax = fields.Char(
        select=True
    )
    direction = fields.Selection(
        [
            ('in', 'Inbound'),
            ('out', 'Outbound'),
        ],
        readonly=True,
        default='in',
        string='Fax Direction',
        help='Whether transmission was incoming or outgoing',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('transmit', 'Transmitted'),
            ('transmit_except', 'Exception'),
            ('done', 'Success'),
        ],
        readonly=True,
        required=True,
        default='draft',
        help='Transmission Status',
    )
    attempt_num = fields.Integer(
        string='Attempts',
        help='Outbound Fax Attempts',
    )
    page_num = fields.Integer(
        string='Pages',
        help='Number Of Pages',
    )
    status_msg = fields.Text(
        readonly=True,
        store=True,
        help='Final status message/error received from remote',
    )
    timestamp = fields.Datetime(
        readonly=True,
        string='Transmission Timestamp',
    )
    response_num = fields.Char(
        readonly=True,
        select=True,
        help='API Response (Transmission) ID',
    )
    payload_ids = fields.Many2many(
        comodel_name='fax.payload',
        required=True,
    )
    adapter_id = fields.Many2one(
        comodel_name='fax.adapter',
        required=True,
    )
    ref = fields.Char(
        readonly=True,
        required=True,
        select=True,
        help='Automatically generated sequence.',
    )

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code(
            'fax.transmission'
        )
        # @TODO: Re-Add phone lib
        # vals_reformatted = self._generic_reformat_phonenumbers(vals)
        # _logger.debug('Reformatted for new: %s', vals_reformatted)
        return super(FaxTransmission, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     vals_reformatted = self._generic_reformat_phonenumbers(vals)
    #     super(FaxTransmission, self).write(vals_reformatted)

    @api.multi
    def action_transmit(self, ):
        self.write({
            'status': 'transmit',
        })
