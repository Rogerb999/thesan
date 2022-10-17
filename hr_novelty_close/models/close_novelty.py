# -*- coding: utf-8 -*-

from odoo import fields, models


class CloseEvent(models.Model):
    _name = 'close.event'
    _description = 'Close Event'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]
    name = fields.Char(track_visibility='onchange',
                       readonly=True,
                       states={'draft': [('readonly', False)]})
    date_finish = fields.Date(string="Finish Date",
                              track_visibility='onchange',
                              readonly=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange')
    additional_configuration = fields.Boolean('Additional Configuration',
                                              track_visibility='onchange')
    exempt_date_ids = fields.One2many(
        'close.event.date', 'close_id', track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]})

    def action_confirm(self):
        self.state = 'confirmed'


class CloseEventDate(models.Model):
    _name = 'close.event.date'
    _rec_name = 'date'
    _description = 'Close Event Dates'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]
    close_id = fields.Many2one('close.event',
                               track_visibility='onchange')
    state = fields.Selection(related="close_id.state")
    date = fields.Datetime(track_visibility='onchange')
    type_id = fields.Many2one('hr.novelty.type', string="Type",
                              track_visibility='onchange')
    subtype_id = fields.Many2one('hr.novelty.type.subtype', string="Sub-Type",
                                 track_visibility='onchange')
    event_id = fields.Many2one('hr.novelty.event', string="Event",
                               track_visibility='onchange')
