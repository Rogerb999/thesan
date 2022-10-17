# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import logging
import threading

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Mail(models.Model):
    _inherit = "mail.mail"

    permission_sent = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        res = super(Mail, self).create(vals)
        if self._context.get('__action_done', ''):
            base_automation_rec = list(
                self._context.get('__action_done', '').keys())[0]
            if base_automation_rec.state == 'email' and base_automation_rec.permission_sent:
                res.permission_sent = True
        return res

    @api.model
    def process_email_queue(self, ids=None):
        """Send immediately queued messages, committing after each
           message is sent - this is not transactional and should
           not be called during another transaction!

           :param list ids: optional list of emails ids to send. If passed
                            no search is performed, and these ids are used
                            instead.
           :param dict context: if a 'filters' key is present in context,
                                this value will be used as an additional
                                filter to further restrict the outgoing
                                messages to send (by default all 'outgoing'
                                messages are sent).
        """
        filters = [('permission_sent', '=', True),
                   '&',
                   ('state', '=', 'outgoing'),
                   '|',
                   ('scheduled_date', '<', datetime.datetime.now()),
                   ('scheduled_date', '=', False)]
        if 'filters' in self._context:
            filters.extend(self._context['filters'])
        # TODO: make limit configurable
        filtered_ids = self.search(filters, limit=10000).ids
        if not ids:
            ids = filtered_ids
        else:
            ids = list(set(filtered_ids) & set(ids))
        ids.sort()

        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(
                threading.currentThread(), 'testing', False)
            res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed processing mail queue")
        return res
