from odoo import tools
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class account_treasury_report(models.Model):
    _name = "account.treasury.report"
    _description = "Treasury Analysis"
    _auto = False

    debit = fields.Float('Debit', readonly=True)
    credit = fields.Float('Credit', readonly=True)
    balance = fields.Float('Balance', readonly=True, digits=dp.get_precision('Account'))
    date = fields.Date('Beginning of Period Date', readonly=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    account_move_line_id = fields.Many2one('account.move.line', string='Journal Item', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    _order = 'date asc'

    def _select(self):
        select_str = """
        SELECT
            min(l.id) AS id,
            l.id AS account_move_line_id,
            sum(l.debit) AS debit,
            sum(l.credit) AS credit,
            sum(l.debit-l.credit) AS balance,
            l.date AS date,
            am.journal_id,
            am.id AS move_id,
            l.partner_id AS partner_id,
            am.company_id AS company_id
        """
        return select_str

    def _from(self):
        from_str = """
        FROM account_move_line l
        """
        return from_str

    def _join(self):
        join_str = """
            LEFT JOIN account_account a ON (l.account_id = a.id)
            LEFT JOIN account_move am ON (am.id=l.move_id)
            LEFT JOIN account_account_type AS act ON act.id = a.user_type_id
            LEFT JOIN account_journal AS aj ON aj.id = am.journal_id
            LEFT JOIN res_partner AS p ON p.id = l.partner_id
        """
        return join_str

    def _where(self):
        where_str = """
        WHERE am.state != 'draft'
            AND act.type = 'liquidity'
        """
        return where_str

    def _group_by(self):
        group_by_str = """
        GROUP BY l.id, am.id, l.date, am.journal_id, am.company_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s AS (
            %s
            %s
            %s
            %s
            %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
