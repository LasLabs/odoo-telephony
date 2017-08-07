# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class SendFax(models.TransientModel):

    _name = 'fax.send.fax'
    _description = 'Wizard to send faxes'

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
        default=lambda s: s.env.user.company_id.country_id,
    )

    @api.model
    def _default_session(self):
        return self.env['fax.adapter'].browse(self._context.get('active_id'))

    @api.multi
    def action_send(self):
        for rec_id in self:
            payload_id = self.env['fax.payload'].create({
                'name': rec_id.name,
                'image': rec_id.image,
                'image_type': 'PNG',
            })
            dialable = None
            send_name = None
            rec_id.adapter_id.action_send(dialable, payload_id, send_name)
