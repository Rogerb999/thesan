# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.http import request


class SignRequestProcess(models.TransientModel):
    _name = 'sign.request.process'
    _description = 'Sign Request Process'

    template_id = fields.Many2one('document.sign.template')
    email_to = fields.Many2one('res.partner', string='Send To', required=True)
    subject = fields.Char('Subject')
    message = fields.Html('Message')
    file_name = fields.Char('Filename')

    def action_send_request(self):
        signrequestdetails = self.env['sign.request.details']
        signrequestuserlist = self.env['sign.request.user.list']
        sign_request_details_id = signrequestdetails.create({
            'template_id': self.template_id.id,
            'name': self.file_name,
            'state': 'sent',
            'reference_model': self._context.get('model'),
            'reference_id': self._context.get('res_id'),
        })
        user = self.env.user
        base_url = request and request.httprequest.url_root
        base_url += 'sign_documents/' + str(sign_request_details_id.id)
        body = '<html><body>' \
               '<p> Signature document requested to you by <b>' + \
               user.name + '</b> for the document <b>' + self.subject + \
               ' </b></p></br> <a class="btn btn-primary" href="' + \
               base_url + '"> Click here </a></body></html>'
        values = {
            'email_from': user.partner_id.email,
            'email_to': self.email_to.email,
            'reply_to': user.partner_id.email,
            'subject': self.subject,
            'body_html': self.message + body,
            'notification': True,
        }
        mail = self.env['mail.mail'].create(values)
        mail.send()
        signrequestuserlist.create({
            'sign_request_user_id': sign_request_details_id.id,
            'partner_id': self.email_to.id,
            'state': 'sent'
        })
        sign_request_details_id.message_subscribe(
            partner_ids=self.email_to.ids)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sign.request.details',
            'target': 'current',
            'res_id': sign_request_details_id.id,
        }
