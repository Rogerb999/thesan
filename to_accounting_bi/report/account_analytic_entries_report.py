from odoo import models, fields, api
from odoo import tools


class analytic_entries_report(models.Model):
    _name = "analytic.entries.report"
    _description = "Analytic Entries Statistics"
    _auto = False

    date = fields.Date('Date', readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    name = fields.Char('Description', size=64, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    company_id = fields.Many2one('res.company', 'Company', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    account_id = fields.Many2one('account.analytic.account', 'Account', required=False)
    general_account_id = fields.Many2one('account.account', 'General Account', required=True)
    move_id = fields.Many2one('account.move.line', 'Move', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)
    amount = fields.Float('Amount', readonly=True)
    unit_amount = fields.Integer('Quantity', readonly=True)
    nbr_entries = fields.Integer('# Entries', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    group_id = fields.Many2one('account.analytic.group', string='Group', readonly=True)
    parent_group_id = fields.Many2one('account.analytic.group', string='Parent Group', readonly=True)

    def _select(self):
        select_str = """
            SELECT
                 min(a.id) as id,
                 count(distinct a.id) as nbr_entries,
                 a.date as date,
                 a.user_id as user_id,
                 a.name as name,
                 analytic.partner_id as partner_id,
                 a.company_id as company_id,
                 a.currency_id as currency_id,
                 a.account_id as account_id,
                 a.general_account_id as general_account_id,
                 a.move_id as move_id,
                 a.product_id as product_id,
                 a.product_uom_id as product_uom_id,
                 sum(a.amount) as amount,
                 sum(a.unit_amount) as unit_amount,
                 aml.journal_id AS journal_id,
                 aag.id AS group_id,
                 p_aag.id AS parent_group_id
        """
        return select_str

    def _from(self):
        from_str = """
            FROM
                account_analytic_line a
        """
        return from_str

    def _join(self):
        join_str = """
            JOIN account_analytic_account analytic ON analytic.id = a.account_id
            LEFT JOIN account_move_line AS aml ON aml.id = a.move_id
            LEFT JOIN account_analytic_group AS aag ON aag.id = analytic.group_id
            LEFT JOIN account_analytic_group AS p_aag ON p_aag.id = aag.parent_id
        """
        return join_str

    def _where(self):
        where_str = """
            WHERE analytic.id = a.account_id
        """
        return where_str

    def _group_by(self):
        group_by_str = """
        GROUP BY
            a.date, a.user_id,a.name,analytic.partner_id,a.company_id,a.currency_id,
            a.account_id,a.general_account_id,
            a.move_id,a.product_id,a.product_uom_id,
            aml.journal_id,
            aag.id,
            p_aag.id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                 %s
                 %s
                 %s
                 %s
                 %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
