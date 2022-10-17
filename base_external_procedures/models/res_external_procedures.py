# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class ResExternalProcedures(models.Model):

    _name = "res.external.procedures"
    _rec_name = "model_id"
    _description = "Res External Procedures"

    model_id = fields.Many2one('ir.model', 'Model')
    function = fields.Char('Function')
    model_ids = fields.Char('Ids')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_process', 'In Process'),
        ('done', 'Done')], default='draft')

    @api.multi
    def check_process(self):
        search_ids = self.env['res.external.procedures'].search([('state', '=', 'draft')])
        for search_id in search_ids:
            search_id.state = 'in_process'

            # get ids in string ['1,2,3'] to '1,2,3'
            string_ids = search_id.model_ids[1:-1]
            _logger.info("string_ids ==> %s", string_ids)

            # Convert string '1,2,3' to [1,2,3]
            convert_ids = [int(s) for s in string_ids.split(',')]
            _logger.info("convert_ids ==> %s", convert_ids)

            #Browse the Records
            model_ids = self.env[search_id.model_id.model].browse(convert_ids)
            _logger.info("model_ids ==> %s", model_ids)
            for model_id in model_ids:
                # Check payslip state
                if model_id.state != 'draft':
                    continue
                _logger.info("model_id ==> %s", model_id)

                #model_id.compute_sheet()
                # Call the Function which assign in the record
                function = getattr(model_id, search_id.function)
                function()

            search_id.state = 'done'
