from odoo import models, fields, api
from odoo import tools
from odoo.addons import decimal_precision as dp


class account_entries_analysis(models.Model):
    _name = 'account.entries.analysis'
    _description = "Journal Items Analysis"
    _order = 'date desc'
    _auto = False

    date = fields.Date('Effective Date', readonly=True)  # TDE FIXME master: rename into date_effective
    create_date = fields.Datetime('Date Created', readonly=True)
    date_maturity = fields.Date('Date Maturity', readonly=True)
    ref = fields.Char('Reference', readonly=True)
    nbr = fields.Integer('# of Items', readonly=True)
    debit = fields.Float('Debit', readonly=True)
    credit = fields.Float('Credit', readonly=True)
    balance = fields.Float('Balance', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    amount_currency = fields.Float('Amount Currency', digits=dp.get_precision('Account'), readonly=True)
    account_id = fields.Many2one('account.account', 'Account', readonly=True)
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True)
    account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    move_state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], 'Status', readonly=True)
    move_line_state = fields.Selection([('draft', 'Unbalanced'), ('valid', 'Valid')], 'State of Move Line', readonly=True)
    full_reconcile_id = fields.Many2one('account.full.reconcile', 'Reconciliation number', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    quantity = fields.Float('Products Quantity', digits=(16, 2), readonly=True)
    user_type_id = fields.Many2one('account.account.type', 'Account Type', readonly=True)
    internal_type = fields.Selection(related='user_type_id.type', store=True, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    def _select(self):
        select_str = """
            SELECT
                l.id AS id,
                am.id AS account_move_id,
                am.date AS date,
                l.date_maturity AS date_maturity,
                l.create_date AS create_date,
                am.ref AS ref,
                am.state AS move_state,
                am.state AS move_line_state,
                l.full_reconcile_id AS full_reconcile_id,
                l.partner_id AS partner_id,
                l.product_id AS product_id,
                l.product_uom_id AS product_uom_id,
                am.company_id AS company_id,
                am.journal_id AS journal_id,
                l.account_id AS account_id,
                l.analytic_account_id as analytic_account_id,
                a.internal_type AS internal_type,
                a.user_type_id AS user_type_id,
                1 AS nbr,
                l.quantity AS quantity,
                l.currency_id AS currency_id,
                l.amount_currency AS amount_currency,
                l.debit AS debit,
                l.credit AS credit,
                COALESCE(l.debit, 0.0) - COALESCE(l.credit, 0.0) AS balance
        """
        return select_str

    def _from(self):
        from_str = """
            FROM
                account_move_line l
        """
        return from_str

    def _join(self):
        join_str = """
                LEFT JOIN account_account a ON (l.account_id = a.id)
                LEFT JOIN account_move am ON (am.id=l.move_id)
        """
        return join_str

    def _where(self):
        where_str = """
            WHERE am.state != 'draft'
        """
        return where_str

    def _group_by(self):
        group_by_str = """
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            %s
            %s
            %s
            %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
