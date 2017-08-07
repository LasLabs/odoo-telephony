# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class FaxAdapter(models.Model):

    _name = 'fax.adapter'
    _description = 'Base Fax Adapter'

    transmission_ids = fields.One2many(
        string='Transmissions',
        comodel_name='fax.transmission',
        inverse_name='adapter_id',
        ondelete='cascade',
        help='Transmissions that have taken place over this adapter',
    )
    name = fields.Char(
        required=True,
    )
    adapter_model_id = fields.Many2one(
        string='Adapter Model',
        comodel_name='ir.model',
        domain=[
            ('model', '=like', 'fax.%',),
            ('model', '!=', 'fax.adapter'),
        ],
        help='Proprietary fax adapter model',
    )
    adapter_model_name = fields.Char(
        related='adapter_model_id.model',
    )
    adapter_pk = fields.Integer(
        help='ID of the proprierary fax adapter',
    )
    adapter_name = fields.Char(
        compute='_compute_adapter_name',
    )
    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        default=lambda s: s.env.user.company_id.country_id,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
    )

    @api.multi
    def _compute_adapter_name(self):
        """Compute the adapter name."""
        for record in self:
            if record.adapter_pk:
                record.adapter_name = record.get_adapter().name

    @api.multi
    def get_adapter(self):
        """Return Recordset obj of the proprietary fax adapter.

        Returns:
             FaxAdapter: An instanace of a FaxAdapter class representing the
             actual adapter.
        """
        self.ensure_one()
        adapter_obj = self.env[self.adapter_model_id.model]
        adapter_id = adapter_obj.browse(self.adapter_pk)
        _logger.debug('Got adapter model %s and obj %s',
                      adapter_obj, adapter_id)
        return adapter_id

    @api.multi
    def action_fetch_payloads(self, transmission_ids):
        """Gets payloads using action_fetch_payloads on proprietary adapter.

        Args:
            transmission_ids (FaxTransmission): To fetch for
        """
        for record in self:
            adapter = record.get_adapter()
            adapter.action_fetch_payloads(transmission_ids, )

    @api.multi
    def action_send(self, dialable, payload_ids, send_name=False):
        """Sends payload using action_send on proprietary adapter.

        Args:
            dialable (str): Number to fax to (convert_to_dial_number)
            payload_ids (FaxPayload): record(s) To Send
            send_name (str): Name of person to send to
        """
        for record in self:
            adapter = record.get_adapter()
            transmission_vals = adapter.action_send(
                dialable, payload_ids, send_name
            )
            record.write({
                'transmission_ids': [(0, 0, transmission_vals)],
            })
