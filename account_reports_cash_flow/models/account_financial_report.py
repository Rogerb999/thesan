# -*- coding: utf-8 -*-
from odoo import models


class ReportAccountFinancialReport(models.Model):
    _inherit = 'account.financial.html.report'

    def _archive_menu(self):
        self.mapped('generated_menu_id').filtered('active').write({'active': False})
