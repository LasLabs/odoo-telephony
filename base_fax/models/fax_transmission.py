# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class FaxTransmission(models.Model):

    _name = 'fax.transmission'
    _description = 'Fax Transmission Record'

    remote_fax = fields.Char(
        index=True,
    )
    local_fax = fields.Char(
        index=True
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
        index=True,
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
        index=True,
        default=lambda s: s.env['ir.sequence'].next_by_code(
            'fax.transmission',
        ),
        help='Automatically generated sequence.',
    )

    @api.multi
    def action_transmit(self):
        self.write({
            'status': 'transmit',
        })
