# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.web.controllers.main import content_disposition
import mimetypes
import base64
from odoo.http import request


class Signature(http.Controller):

    @http.route(['/get_download/<int:requestId>'], type='http', auth='public')
    def download_sign_document(self, requestId):
        request_id = http.request.env['sign.request.details'].browse(requestId)
        mime_types = mimetypes.guess_type(
            request_id.template_id.attachment_id.mimetype)
        headers = [
            ('Content-Type', mime_types),
            ('Content-Disposition', content_disposition(request_id.name)),
        ]
        return http.request.make_response(
            base64.b64decode(request_id.sign_document), headers=headers)

    @http.route(['/sign_documents/<int:requestId>'],
                type='http', auth='public')
    def sign_document(self, requestId):
        request_id = http.request.env['sign.request.details'].browse(requestId)
        base_url = request and request.httprequest.url_root
        return http.request.render('sign_documents.sign_by_mail', {
            'url': base_url + "web?debug=assets#id="+str(
                request_id.id)+"&model=sign.request.details&view_type=form"
        })
