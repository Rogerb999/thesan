# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from dateutil.relativedelta import relativedelta


class AccountCashFlowReport(models.AbstractModel):
    _name = 'account.cash.flow.report'
    _description = 'Cash Flow Report'
    _inherit = 'account.report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_comparison = None
    filter_journals = True
    filter_unfold_all = False
    filter_all_entries = False

    # -------------------------------------------------------------------------
    # RETRO-COMPATIBILITY
    # -------------------------------------------------------------------------

    def open_journal_items(self, options, params):
        if params.get('financial_group_line_id'):
            params.pop('financial_group_line_id')
        return super(AccountCashFlowReport, self).open_journal_items(options, params)

    @api.model
    def _get_options_companies(self, options):
        if not options.get('multi_company'):
            company = self.env.company
            return [{'id': company.id, 'name': company.name, 'selected': True}]

        all_companies = []
        companies = []
        for company_option in options['multi_company']:
            if company_option['selected']:
                companies.append(company_option)
            all_companies.append(company_option)
        return companies or all_companies

    @api.model
    def _get_query_currency_table(self, options):
        ''' Construct the currency table as a mapping company -> rate to convert the amount to the user's company
        currency in a multi-company/multi-currency environment.
        The currency_table is a small postgresql table construct with VALUES.
        :param options: The report options.
        :return:        The query representing the currency table.
        '''

        user_company = self.env.user.company_id
        user_currency = user_company.currency_id
        if options.get('multi_company'):
            company_ids = [c['id'] for c in self._get_options_companies(options) if c['id'] != user_company.id]
            company_ids.append(user_company.id)
            companies = self.env['res.company'].browse(company_ids)
            conversion_date = options['date']['date_to']
            currency_rates = companies.mapped('currency_id')._get_rates(user_company, conversion_date)
        else:
            companies = user_company
            currency_rates = {user_currency.id: 1.0}

        conversion_rates = []
        for company in companies:
            conversion_rates.append((
                company.id,
                currency_rates[user_company.currency_id.id] / currency_rates[company.currency_id.id],
                user_currency.decimal_places,
            ))

        currency_table = ','.join('(%s, %s, %s)' % args for args in conversion_rates)
        return '(VALUES %s) AS currency_table(company_id, rate, precision)' % currency_table

    @api.model
    def _query_get(self, options, domain=None):
        return self.env['account.move.line'].with_context({
            **self._set_context(options),
            'date_from': options['date']['date_from'],
            'date_to': options['date']['date_to'],
            'strict_range': options['date'].get('strict_range'),
        })._query_get(domain=domain)

    @api.model
    def _get_options_journals(self, options):
        journals = []
        for journal_option in options.get('journals', []):
            if journal_option['id'] in ('divider', 'group'):
                continue
            if journal_option['selected']:
                journals.append(journal_option)
        return journals

    # -------------------------------------------------------------------------
    # OPTIONS
    # -------------------------------------------------------------------------

    @api.model
    def _get_options_current_period(self, options):
        ''' Create options with the 'strict_range' enabled on the filter_date / filter_comparison.
        :param options: The report options.
        :return:        A copy of the options.
        '''
        new_options = options.copy()
        new_options['date'] = {
            'mode': 'range',
            'date_from': options['date']['date_from'],
            'date_to': options['date']['date_to'],
            'strict_range': options['date']['date_from'] is not False,
        }
        new_options['journals'] = []
        return new_options

    @api.model
    def _get_options_beginning_period(self, options):
        ''' Create options with the 'strict_range' enabled on the filter_date.
        :param options: The report options.
        :return:        A copy of the options.
        '''
        new_options = options.copy()
        date_tmp = fields.Date.from_string(options['date']['date_from']) - relativedelta(days=1)
        new_options['date'] = {
            'mode': 'single',
            'date_from': False,
            'date_to': fields.Date.to_string(date_tmp),
        }
        return new_options

    @api.model
    def _get_filter_journals(self):
        # OVERRIDE to filter only bank / cash journals.
        return self.env['account.journal'].search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.user.company_id.id]),
            ('type', 'in', ('bank', 'cash'))
        ], order='company_id, name')

    # -------------------------------------------------------------------------
    # QUERIES
    # -------------------------------------------------------------------------

    @api.model
    def _get_tags_per_account(self, options, tag_ids):
        ''' Compute a map account_id => tags used to dispatch the lines in the cash flow statement:
        operating, investing, financing or unclassified activities.
        This part is done in sql to avoid browsing and prefetching all account.account records.
        :param options: The report options.
        :param tag_ids: The ids of the 3 tags used by the cash flow: operating, investing and the financing tags.
        :return:        A map account_id => tag_ids set on this account.
        '''
        tags_per_accounts = {}

        query = '''
            SELECT
                DISTINCT account_account_id,
                ARRAY_AGG(account_account_tag_id)
            FROM account_account_account_tag
            WHERE account_account_tag_id IN %s
            GROUP BY account_account_id
        '''
        params = [tag_ids]

        self._cr.execute(query, params)
        for account_id, tags in self._cr.fetchall():
            tags_per_accounts[account_id] = tags
        return tags_per_accounts

    @api.model
    def _get_liquidity_move_ids(self, options):
        ''' Retrieve all liquidity moves to be part of the cash flow statement and also the accounts making them
        such moves.
        :param options: The report options.
        :return:        payment_move_ids: A tuple containing all account.move's ids being the liquidity moves.
                        payment_account_ids: A tuple containing all account.account's ids being used in a liquidity journal.
        '''
        new_options = self._get_options_current_period(options)
        selected_journals = self._get_options_journals(options)

        # Fetch liquidity accounts:
        # Accounts being used by at least one bank / cash journal.
        selected_journal_ids = [j['id'] for j in selected_journals]
        if selected_journal_ids:
            where_clause = "account_journal.id IN %s"
            where_params = [tuple(selected_journal_ids)]
        else:
            where_clause = "account_journal.type IN ('bank', 'cash')"
            where_params = []

        payment_account_ids = set()
        self._cr.execute('''
            SELECT default_debit_account_id, default_credit_account_id
            FROM account_journal
            WHERE ''' + where_clause, where_params
        )
        for debit_account_id, credit_account_id in self._cr.fetchall():
            if debit_account_id:
                payment_account_ids.add(debit_account_id)
            if credit_account_id:
                payment_account_ids.add(credit_account_id)

        if not payment_account_ids:
            return (), ()

        # Fetch journal entries:
        # account.move having at least one line using a liquidity account.
        payment_move_ids = set()
        tables, where_clause, where_params = self._query_get(new_options, [('account_id', 'in', list(payment_account_ids))])

        query = '''
            SELECT DISTINCT account_move_line.move_id
            FROM ''' + tables + '''
            WHERE ''' + where_clause + '''
            GROUP BY account_move_line.move_id
        '''
        self._cr.execute(query, where_params)
        for res in self._cr.fetchall():
            payment_move_ids.add(res[0])

        return tuple(payment_move_ids), tuple(payment_account_ids)

    @api.model
    def _get_liquidity_move_report_lines(self, options, currency_table_query, payment_move_ids, payment_account_ids):
        ''' Fetch all information needed to compute lines from liquidity moves.
        The difficulty is to represent only the not-reconciled part of balance.
        :param options:                 The report options.
        :param currency_table_query:    The floating query to handle a multi-company/multi-currency environment.
        :param payment_move_ids:        A tuple containing all account.move's ids being the liquidity moves.
        :param payment_account_ids:     A tuple containing all account.account's ids being used in a liquidity journal.
        :return:                        A list of tuple (account_id, account_code, account_name, account_internal_type, amount).
        '''
        if not payment_move_ids:
            return []

        reconciled_amount_per_account = {}

        # ==== Compute the reconciled part of each account ====

        query = '''
            SELECT
                credit_line.account_id,
                account.code,
                account.name,
                account.internal_type,
                COALESCE(SUM(ROUND(partial.amount * currency_table.rate, currency_table.precision)), 0.0)
            FROM account_move_line credit_line
            LEFT JOIN ''' + currency_table_query + ''' ON currency_table.company_id = credit_line.company_id
            LEFT JOIN account_partial_reconcile partial ON partial.credit_move_id = credit_line.id
            JOIN account_account account ON account.id = credit_line.account_id
            WHERE credit_line.move_id IN %s AND credit_line.account_id NOT IN %s
            AND partial.max_date BETWEEN %s AND %s
            GROUP BY credit_line.company_id, credit_line.account_id, account.code, account.name, account.internal_type
            
            UNION ALL
            
            SELECT
                debit_line.account_id,
                account.code,
                account.name,
                account.internal_type,
                COALESCE(-SUM(ROUND(partial.amount * currency_table.rate, currency_table.precision)), 0.0)
            FROM account_move_line debit_line
            LEFT JOIN ''' + currency_table_query + ''' ON currency_table.company_id = debit_line.company_id
            LEFT JOIN account_partial_reconcile partial ON partial.debit_move_id = debit_line.id
            JOIN account_account account ON account.id = debit_line.account_id
            WHERE debit_line.move_id IN %s AND debit_line.account_id NOT IN %s
            AND partial.max_date BETWEEN %s AND %s
            GROUP BY debit_line.company_id, debit_line.account_id, account.code, account.name, account.internal_type
        '''
        self._cr.execute(query, [
            payment_move_ids, payment_account_ids, options['date']['date_from'], options['date']['date_to'],
            payment_move_ids, payment_account_ids, options['date']['date_from'], options['date']['date_to'],
        ])

        for account_id, account_code, account_name, account_internal_type, reconciled_amount in self._cr.fetchall():
            reconciled_amount_per_account.setdefault(account_id, [account_code, account_name, account_internal_type, 0.0, 0.0])
            reconciled_amount_per_account[account_id][3] += reconciled_amount

        # ==== Compute total amount of each account ====

        query = '''
            SELECT
                line.account_id,
                account.code,
                account.name,
                account.internal_type,
                COALESCE(SUM(ROUND(line.balance * currency_table.rate, currency_table.precision)), 0.0)
            FROM account_move_line line
            LEFT JOIN ''' + currency_table_query + ''' ON currency_table.company_id = line.company_id
            JOIN account_account account ON account.id = line.account_id
            WHERE line.move_id IN %s AND line.account_id NOT IN %s
            GROUP BY line.account_id, account.code, account.name, account.internal_type
        '''
        self._cr.execute(query, [payment_move_ids, payment_account_ids])

        for account_id, account_code, account_name, account_internal_type, balance in self._cr.fetchall():
            reconciled_amount_per_account.setdefault(account_id, [account_code, account_name, account_internal_type, 0.0, 0.0])
            reconciled_amount_per_account[account_id][4] += balance

        return [(k, v[0], v[1], v[2], v[4] + v[3]) for k, v in reconciled_amount_per_account.items()]

    @api.model
    def _get_reconciled_move_report_lines(self, options, currency_table_query, payment_move_ids, payment_account_ids):
        ''' Retrieve all moves being not a liquidity move to be shown in the cash flow statement.
        Each amount must be valued at the percentage of what is actually paid.
        E.g. An invoice of 1000 being paid at 50% must be valued at 500.
        :param options:                 The report options.
        :param currency_table_query:    The floating query to handle a multi-company/multi-currency environment.
        :param payment_move_ids:        A tuple containing all account.move's ids being the liquidity moves.
        :param payment_account_ids:     A tuple containing all account.account's ids being used in a liquidity journal.
        :return:                        A list of tuple (account_id, account_code, account_name, account_internal_type, amount).
        '''
        reconciled_account_ids = set()
        reconciled_percentage_per_move = {}

        if not payment_move_ids:
            return reconciled_percentage_per_move

        # ==== Compute reconciled amount per (move_id, account_id) ====

        query = '''
            SELECT
                debit_line.move_id,
                debit_line.account_id,
                COALESCE(SUM(partial.amount), 0.0)
            FROM account_move_line credit_line
            LEFT JOIN account_partial_reconcile partial ON partial.credit_move_id = credit_line.id
            INNER JOIN account_move_line debit_line ON debit_line.id = partial.debit_move_id
            WHERE credit_line.move_id IN %s
            AND credit_line.account_id NOT IN %s
            AND credit_line.credit > 0.0
            AND debit_line.move_id NOT IN %s
            AND partial.max_date BETWEEN %s AND %s
            GROUP BY debit_line.move_id, debit_line.account_id
            
            UNION ALL
            
            SELECT
                credit_line.move_id,
                credit_line.account_id,
                COALESCE(-SUM(partial.amount), 0.0)
            FROM account_move_line debit_line
            LEFT JOIN account_partial_reconcile partial ON partial.debit_move_id = debit_line.id
            INNER JOIN account_move_line credit_line ON credit_line.id = partial.credit_move_id
            WHERE debit_line.move_id IN %s
            AND debit_line.account_id NOT IN %s
            AND debit_line.debit > 0.0
            AND credit_line.move_id NOT IN %s
            AND partial.max_date BETWEEN %s AND %s
            GROUP BY credit_line.move_id, credit_line.account_id
        '''
        self._cr.execute(query, [
            payment_move_ids, payment_account_ids, payment_move_ids, options['date']['date_from'], options['date']['date_to'],
            payment_move_ids, payment_account_ids, payment_move_ids, options['date']['date_from'], options['date']['date_to'],
        ])
        for move_id, account_id, reconciled_amount in self._cr.fetchall():
            reconciled_percentage_per_move.setdefault(move_id, {})
            reconciled_percentage_per_move[move_id].setdefault(account_id, [0.0, 0.0])
            reconciled_percentage_per_move[move_id][account_id][0] += reconciled_amount
            reconciled_account_ids.add(account_id)

        if not reconciled_percentage_per_move:
            return []

        # ==== Compute the balance per (move_id, account_id) ====

        query = '''
            SELECT
                line.move_id,
                line.account_id,
                COALESCE(SUM(line.balance), 0.0)
            FROM account_move_line line
            JOIN ''' + currency_table_query + ''' ON currency_table.company_id = line.company_id
            WHERE line.move_id IN %s AND line.account_id IN %s
            GROUP BY line.move_id, line.account_id
        '''
        self._cr.execute(query, [tuple(reconciled_percentage_per_move.keys()), tuple(reconciled_account_ids)])
        for move_id, account_id, balance in self._cr.fetchall():
            if account_id in reconciled_percentage_per_move[move_id]:
                reconciled_percentage_per_move[move_id][account_id][1] += balance

        # ==== Fetch lines of reconciled moves ====

        reconciled_amount_per_account = {}

        query = '''
            SELECT
                line.move_id,
                line.account_id,
                account.code,
                account.name,
                account.internal_type,
                COALESCE(SUM(ROUND(line.balance * currency_table.rate, currency_table.precision)), 0.0)
            FROM account_move_line line
            LEFT JOIN ''' + currency_table_query + ''' ON currency_table.company_id = line.company_id
            JOIN account_account account ON account.id = line.account_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, line.account_id, account.code, account.name, account.internal_type
        '''
        self._cr.execute(query, [tuple(reconciled_percentage_per_move.keys())])

        for move_id, account_id, account_code, account_name, account_internal_type, balance in self._cr.fetchall():
            # Compute the total reconciled for the whole move.
            total_reconciled_amount = 0.0
            total_amount = 0.0
            for reconciled_amount, amount in reconciled_percentage_per_move[move_id].values():
                total_reconciled_amount += reconciled_amount
                total_amount += amount

            # Compute matched percentage for each account.
            if total_amount and account_id not in reconciled_percentage_per_move[move_id]:
                # Lines being on reconciled moves but not reconciled with any liquidity move must be valued at the
                # percentage of what is actually paid.
                reconciled_percentage = total_reconciled_amount / total_amount
                balance *= reconciled_percentage
            elif not total_amount and account_id in reconciled_percentage_per_move[move_id]:
                # The total amount to reconcile is 0. In that case, only add entries being on these accounts. Otherwise,
                # this special case will lead to an unexplained difference equivalent to the reconciled amount on this
                # account.
                # E.g:
                #
                # Liquidity move:
                # Account         | Debit     | Credit
                # --------------------------------------
                # Bank            |           | 100
                # Receivable      | 100       |
                #
                # Reconciled move:                          <- reconciled_amount=100, total_amount=0.0
                # Account         | Debit     | Credit
                # --------------------------------------
                # Receivable      |           | 200
                # Receivable      | 200       |             <- Only the reconciled part of this entry must be added.
                balance = -reconciled_percentage_per_move[move_id][account_id][0]
            else:
                # Others lines are not considered.
                continue

            reconciled_amount_per_account.setdefault(account_id, [account_id, account_code, account_name, account_internal_type, 0.0])
            reconciled_amount_per_account[account_id][4] += balance

        return list(reconciled_amount_per_account.values())

    @api.model
    def _compute_liquidity_balance(self, options, currency_table_query, payment_account_ids):
        ''' Compute the balance of all liquidity accounts to populate the following sections:
            'Cash and cash equivalents, beginning of period' and 'Cash and cash equivalents, closing balance'.
        :param options:                 The report options.
        :param currency_table_query:    The custom query containing the multi-companies rates.
        :param payment_account_ids:     A tuple containing all account.account's ids being used in a liquidity journal.
        :return:                        A list of tuple (account_id, account_code, account_name, balance).
        '''
        new_options = self._get_options_current_period(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=[('account_id', 'in', payment_account_ids)])

        query = '''
            SELECT
                account_move_line.account_id,
                account.code AS account_code,
                account.name AS account_name,
                COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0)
            FROM ''' + tables + '''
            JOIN account_account account ON account.id = account_move_line.account_id
            LEFT JOIN ''' + currency_table_query + ''' ON currency_table.company_id = account_move_line.company_id
            WHERE ''' + where_clause + '''
            GROUP BY account_move_line.account_id, account.code, account.name
        '''
        self._cr.execute(query, where_params)
        return self._cr.fetchall()

    # -------------------------------------------------------------------------
    # COLUMNS / LINES
    # -------------------------------------------------------------------------

    @api.model
    def _get_columns_name(self, options):
        return [{'name': ''}, {'name': _('Balance'), 'class': 'number'}]

    @api.model
    def _get_lines_to_compute(self, options):
        rows = [
            {
                'id': 'cash_flow_line_%s' % index,
                'name': name,
                'level': level,
                'columns': [{'name': 0.0, 'class': 'number'}],
            } for index, level, name in [
                (0, 2, _('Cash and cash equivalents, beginning of period')),
                (1, 2, _('Net increase in cash and cash equivalents')),
                (2, 3, _('Cash flows from operating activities')),
                (3, 4, _('Advance Payments received from customers')),
                (4, 4, _('Cash received from operating activities')),
                (5, 4, _('Advance payments made to suppliers')),
                (6, 4, _('Cash paid for operating activities')),
                (7, 3, _('Cash flows from investing & extraordinary activities')),
                (8, 4, _('Cash in')),
                (9, 4, _('Cash out')),
                (10, 3, _('Cash flows from financing activities')),
                (11, 4, _('Cash in')),
                (12, 4, _('Cash out')),
                (13, 3, _('Cash flows from unclassified activities')),
                (14, 4, _('Cash in')),
                (15, 4, _('Cash out')),
                (16, 2, _('Cash and cash equivalents, closing balance')),
            ]
        ]
        rows[1]['style'] = 'padding-top: 48px; vertical-align: text-bottom;'
        rows[1]['columns'][0]['style'] = 'padding-top: 48px; vertical-align: text-bottom;'
        rows[16]['style'] = 'padding-top: 48px; vertical-align: text-bottom;'
        rows[16]['columns'][0]['style'] = 'padding-top: 48px; vertical-align: text-bottom;'
        return rows

    @api.model
    def _get_lines(self, options, line_id=None):

        def _insert_at_index(index, account_id, account_code, account_name, amount):
            ''' Insert the amount in the right section depending the line's index and the account_id. '''
            # Helper used to add some values to the report line having the index passed as parameter
            # (see _get_lines_to_compute).
            line = lines_to_compute[index]

            if self.env.user.company_id.currency_id.is_zero(amount):
                return

            line.setdefault('unfolded_lines', {})
            line['unfolded_lines'].setdefault(account_id, {
                'id': account_id,
                'name': '%s %s' % (account_code, account_name),
                'level': line['level'] + 1,
                'parent_id': line['id'],
                'columns': [{'name': 0.0, 'class': 'number'}],
                'caret_options': 'account.account',
            })
            line['columns'][0]['name'] += amount
            line['unfolded_lines'][account_id]['columns'][0]['name'] += amount

        def _dispatch_result(account_id, account_code, account_name, account_internal_type, amount):
            ''' Dispatch the newly fetched line inside the right section. '''
            if account_internal_type == 'receivable':
                # 'Advance Payments received from customers'                (index=3)
                _insert_at_index(3, account_id, account_code, account_name, -amount)
            elif account_internal_type == 'payable':
                # 'Advance Payments made to suppliers'                      (index=5)
                _insert_at_index(5, account_id, account_code, account_name, -amount)
            elif amount < 0:
                if tag_operating_id in tags_per_account.get(account_id, []):
                    # 'Cash received from operating activities'             (index=4)
                    _insert_at_index(4, account_id, account_code, account_name, -amount)
                elif tag_investing_id in tags_per_account.get(account_id, []):
                    # 'Cash in for investing activities'                    (index=8)
                    _insert_at_index(8, account_id, account_code, account_name, -amount)
                elif tag_financing_id in tags_per_account.get(account_id, []):
                    # 'Cash in for financing activities'                    (index=11)
                    _insert_at_index(11, account_id, account_code, account_name, -amount)
                else:
                    # 'Cash in for unclassified activities'                 (index=14)
                    _insert_at_index(14, account_id, account_code, account_name, -amount)
            elif amount > 0:
                if tag_operating_id in tags_per_account.get(account_id, []):
                    # 'Cash paid for operating activities'                  (index=6)
                    _insert_at_index(6, account_id, account_code, account_name, -amount)
                elif tag_investing_id in tags_per_account.get(account_id, []):
                    # 'Cash out for investing activities'                   (index=9)
                    _insert_at_index(9, account_id, account_code, account_name, -amount)
                elif tag_financing_id in tags_per_account.get(account_id, []):
                    # 'Cash out for financing activities'                   (index=12)
                    _insert_at_index(12, account_id, account_code, account_name, -amount)
                else:
                    # 'Cash out for unclassified activities'                (index=15)
                    _insert_at_index(15, account_id, account_code, account_name, -amount)

        unfold_all = self._context.get('print_mode') or options.get('unfold_all')
        currency_table_query = self._get_query_currency_table(options)
        lines_to_compute = self._get_lines_to_compute(options)

        tag_operating_id = self.env.ref('account.account_tag_operating').id
        tag_investing_id = self.env.ref('account.account_tag_investing').id
        tag_financing_id = self.env.ref('account.account_tag_financing').id
        tag_ids = (tag_operating_id, tag_investing_id, tag_financing_id)
        tags_per_account = self._get_tags_per_account(options, tag_ids)

        payment_move_ids, payment_account_ids = self._get_liquidity_move_ids(options)

        # Compute 'Cash and cash equivalents, beginning of period'      (index=0)
        beginning_period_options = self._get_options_beginning_period(options)
        for account_id, account_code, account_name, balance in self._compute_liquidity_balance(beginning_period_options, currency_table_query, payment_account_ids):
            _insert_at_index(0, account_id, account_code, account_name, balance)
            _insert_at_index(16, account_id, account_code, account_name, balance)

        # Compute 'Cash and cash equivalents, closing balance'          (index=16)
        for account_id, account_code, account_name, balance in self._compute_liquidity_balance(options, currency_table_query, payment_account_ids):
            _insert_at_index(16, account_id, account_code, account_name, balance)

        # ==== Process liquidity moves ====
        res = self._get_liquidity_move_report_lines(options, currency_table_query, payment_move_ids, payment_account_ids)
        for account_id, account_code, account_name, account_internal_type, amount in res:
            _dispatch_result(account_id, account_code, account_name, account_internal_type, amount)

        # ==== Process reconciled moves ====
        res = self._get_reconciled_move_report_lines(options, currency_table_query, payment_move_ids, payment_account_ids)
        for account_id, account_code, account_name, account_internal_type, balance in res:
            _dispatch_result(account_id, account_code, account_name, account_internal_type, balance)

        # 'Cash flows from operating activities'                            (index=2)
        lines_to_compute[2]['columns'][0]['name'] = \
            lines_to_compute[3]['columns'][0]['name'] + \
            lines_to_compute[4]['columns'][0]['name'] + \
            lines_to_compute[5]['columns'][0]['name'] + \
            lines_to_compute[6]['columns'][0]['name']
        # 'Cash flows from investing & extraordinary activities'            (index=7)
        lines_to_compute[7]['columns'][0]['name'] = \
            lines_to_compute[8]['columns'][0]['name'] + \
            lines_to_compute[9]['columns'][0]['name']
        # 'Cash flows from financing activities'                            (index=10)
        lines_to_compute[10]['columns'][0]['name'] = \
            lines_to_compute[11]['columns'][0]['name'] + \
            lines_to_compute[12]['columns'][0]['name']
        # 'Cash flows from unclassified activities'                         (index=13)
        lines_to_compute[13]['columns'][0]['name'] = \
            lines_to_compute[14]['columns'][0]['name'] + \
            lines_to_compute[15]['columns'][0]['name']
        # 'Net increase in cash and cash equivalents'                       (index=1)
        lines_to_compute[1]['columns'][0]['name'] = \
            lines_to_compute[2]['columns'][0]['name'] + \
            lines_to_compute[7]['columns'][0]['name'] + \
            lines_to_compute[10]['columns'][0]['name'] + \
            lines_to_compute[13]['columns'][0]['name']

        # ==== Compute the unexplained difference ====

        closing_ending_gap = lines_to_compute[16]['columns'][0]['name'] - lines_to_compute[0]['columns'][0]['name']
        computed_gap = sum(lines_to_compute[index]['columns'][0]['name'] for index in [2, 7, 10, 13])
        delta = closing_ending_gap - computed_gap
        if not self.env.user.company_id.currency_id.is_zero(delta):
            lines_to_compute.insert(16, {
                'id': 'cash_flow_line_unexplained_difference',
                'name': _('Unexplained Difference'),
                'level': 0,
                'columns': [{'name': delta, 'class': 'number'}],
            })

        # ==== Build final lines ====

        lines = []
        for line in lines_to_compute:
            unfolded_lines = line.pop('unfolded_lines', {})
            sub_lines = [unfolded_lines[k] for k in sorted(unfolded_lines)]

            line['unfoldable'] = len(sub_lines) > 0
            line['unfolded'] = line['unfoldable'] and (unfold_all or line['id'] in options['unfolded_lines'])

            # Header line.
            line['columns'][0]['name'] = self.format_value(line['columns'][0]['name'])
            lines.append(line)

            # Sub lines.
            for sub_line in sub_lines:
                sub_line['columns'][0]['name'] = self.format_value(sub_line['columns'][0]['name'])
                sub_line['style'] = '' if line['unfolded'] else 'display: none;'
                lines.append(sub_line)

            # Total line.
            if line['unfoldable']:
                lines.append({
                    'id': '%s_total' % line['id'],
                    'name': _('Total') + ' ' + line['name'],
                    'level': line['level'] + 1,
                    'parent_id': line['id'],
                    'columns': [{**c, 'style': ''} for c in line['columns']],
                    'class': 'o_account_reports_domain_total',
                    'style': '' if line['unfolded'] else 'display: none;',
                })
        return lines

    @api.model
    def _get_report_name(self):
        return _('Cash Flow Statement')
