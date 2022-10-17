# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, sql_db
from odoo.exceptions import UserError
from odoo import tools


class IrModel(models.Model):
    _inherit = 'ir.model'

    ks_is_custom_model = fields.Boolean(
        string="Report View", default=False,
        help="Whether this model supports custom report.",
    )

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        if model_data.get('ks_is_custom_model', False):
            model_class._auto = False

        return model_class


class KsCustomReport(models.Model):
    _name = 'ks_custom_report.ks_report'
    _description = 'Report Model'

    name = fields.Char(string="Report Name", required=True)
    ks_model_id = fields.Many2one("ir.model", string="Model", required=True,
                                  domain=[('access_ids', '!=', False), ('transient', '=', False),
                                          ('model', 'not ilike', 'base_import%'), ('model', 'not ilike', 'ir.%'),
                                          ('model', 'not ilike', 'web_editor.%'), ('model', 'not ilike', 'web_tour.%'),
                                          ('model', '!=', 'mail.thread'), ('model', 'not ilike', 'ks_%'),
                                          ('model', 'not ilike', 'ks_%')])

    ks_cr_model_id = fields.Many2one("ir.model", string="Report Model", ondelete='cascade')

    # Views ---------------------------------
    ks_tree_view_id = fields.Many2one("ir.ui.view", string="Report Tree View", ondelete='set null')
    ks_search_view_id = fields.Many2one("ir.ui.view", string="Report Search View")
    ks_pivot_view_id = fields.Many2one("ir.ui.view", string="Report Pivot View")

    ks_cr_column_ids = fields.One2many(comodel_name="ks_custom_report.ks_column", inverse_name="ks_cr_model_id",
                                       string="Report Fields", ondelete='cascade')

    # Menu Fields ----------------
    ks_cr_menu_name = fields.Char(string="Menu Name", required=True)
    ks_cr_top_menu_id = fields.Many2one('ir.ui.menu', default=lambda self: self.env.ref('ks_custom_report.menu_root'),
                                        string="Show Under Menu", required=True)
    ks_cr_menu_priority = fields.Integer(string="Menu Priority", required=True, default=50)
    ks_cr_active = fields.Boolean(string="Active", default=True)
    ks_cr_group_access = fields.Many2many('res.groups', string="Group Access")

    ks_cr_menu_id = fields.Many2one('ir.ui.menu', string="cr Menu Id")
    ks_cr_action_id = fields.Many2one('ir.actions.act_window', string="Web Server Action Id")

    # Show Pivot and Graph View
    ks_show_pivot_view = fields.Boolean(string="Show Pivot View", default=True)
    ks_show_graph_view = fields.Boolean(string="Show Graph View", default=True)

    @api.model
    def create(self, values):
        rec = super(KsCustomReport, self).create(values)
        self._ks_create_custom_report(rec)
        self._ks_cr_model_init(rec)
        return rec

    @api.multi
    def write(self, vals):
        record = super(KsCustomReport, self).write(vals)
        for rec in self:

            if vals.get('ks_model_id'):
                raise UserError(_('Report Model cannot be changed after it is created !'))

            if vals.get('ks_cr_column_ids'):
                self._ks_cr_model_init(rec)

            if vals.get('name'):
                rec.ks_cr_action_id.name = vals.get('name')

            menu_update_vals = {}
            if 'ks_cr_menu_name' in vals:
                menu_update_vals['name'] = vals['ks_cr_menu_name']
            if 'ks_cr_group_access' in vals:
                menu_update_vals['groups_id'] = vals['ks_cr_group_access']
            if 'ks_cr_active' in vals and rec.ks_cr_menu_id:
                menu_update_vals['active'] = vals['ks_cr_active']
            if 'ks_cr_top_menu_id' in vals:
                menu_update_vals['parent_id'] = vals['ks_cr_top_menu_id']
            if 'ks_cr_menu_priority' in vals:
                menu_update_vals['sequence'] = vals['ks_cr_menu_priority']
            rec.ks_cr_menu_id.sudo().write(menu_update_vals)

            if rec.ks_cr_action_id:
                view_mode = rec.ks_cr_action_id.view_mode.split(",")
                if 'ks_show_pivot_view' in vals:
                    view_mode.append("pivot") if vals['ks_show_pivot_view'] else view_mode.remove("pivot")
                if 'ks_show_graph_view' in vals:
                    view_mode.append("graph") if vals['ks_show_graph_view'] else view_mode.remove("graph")
                rec.ks_cr_action_id.sudo().write({'view_mode': ",".join(view_mode)})

        return record

    @api.multi
    def unlink(self):
        for rec in self:
            rec.ks_tree_view_id.sudo().unlink()
            rec.ks_search_view_id.sudo().unlink()
            rec.ks_pivot_view_id.sudo().unlink()

            rec.ks_cr_action_id.sudo().unlink()
            rec.ks_cr_menu_id.sudo().unlink()

            if rec.ks_cr_model_id:
                rec.ks_cr_model_id.sudo().unlink()
        return super(KsCustomReport, self).unlink()

    def _ks_create_custom_report(self, rec):
        self._ks_cr_model(rec)
        self._ks_cr_menu_action(rec)
        self._ks_cr_access_rights(rec)

    def _ks_cr_model(self, rec):
        rec.ks_cr_model_id = self.env['ir.model'].sudo().create({
            'name': rec.name,
            'model': "x_ks_cr.ks_" + "".join([x[0] for x in rec.ks_model_id.model.split(".")]) + str(rec.id),
            'state': 'manual',
            'ks_is_custom_model': True,
        })

    def _ks_cr_fields(self, rec, column_id, field_name, ir_field_id, display_name=False):
        ttype = 'float' if ir_field_id.ttype == 'monetary' else ir_field_id.ttype
        if ir_field_id.ttype == 'selection':
            ks_selection = str(self.env[ir_field_id.model].fields_get()[ir_field_id.name]['selection'])
        elif ir_field_id.ttype == 'selection' and ir_field_id.related:
            ks_selection = str(self.env[ir_field_id.model].fields_get()[ir_field_id.name]['selection'])
        else:
            ks_selection = False
        values = {
            'name': field_name,
            'ttype': ttype,
            'field_description': display_name if display_name else ir_field_id.field_description,
            'model_id': rec.ks_cr_model_id.id,
            'state': 'manual',
            'selection': ir_field_id.selection if ir_field_id.selection else ks_selection,
        }

        column_id.ks_cr_field_id = self.env['ir.model.fields'].sudo().create(values)

    def _ks_cr_menu_action(self, rec):
        cr_model = rec.ks_cr_model_id
        view_mode = ["tree", "form"]

        if rec.ks_show_pivot_view:
            view_mode.append("pivot")

        if rec.ks_show_graph_view:
            view_mode.append("graph")

        action_vals = {
            'name': rec.name,
            'res_model': cr_model.model,
            'view_mode': ",".join(view_mode),
            'views': [(False, 'tree'), (False, 'form')],
        }

        rec.ks_cr_action_id = self.env['ir.actions.act_window'].sudo().create(action_vals)

        rec.ks_cr_menu_id = self.env['ir.ui.menu'].sudo().create({
            'name': rec.ks_cr_menu_name,
            'parent_id': rec.ks_cr_top_menu_id.id,
            'action': 'ir.actions.act_window,%d' % (rec.ks_cr_action_id.id,),
            'groups_id': [(6, 0, rec.ks_cr_group_access.ids)],
            'sequence': rec.ks_cr_menu_priority,
            'active': rec.ks_cr_active,
        })

    def _ks_cr_access_rights(self, rec):
        cr_model = rec.ks_cr_model_id
        self.env['ir.model.access'].sudo().create({
            'name': cr_model.name + ' all_user',
            'model_id': cr_model.id,
            'perm_read': True,
            'perm_write': False,
            'perm_create': False,
            'perm_unlink': False,
        })

    def _query(self, rec):

        rec.ks_tree_view_id.sudo().unlink()
        rec.ks_search_view_id.sudo().unlink()
        rec.ks_pivot_view_id.sudo().unlink()

        field_list = []
        search_filter_field_list = []
        group_filter_field_list = []

        select_clause_list = []
        from_clause_list = []

        ks_model = self.env['ir.model'].search([('model', '=', rec.ks_model_id.model)], limit=1)

        temp_model_name = ks_model.model

        query_data = {"".join([x[0] for x in temp_model_name.split(".")]): temp_model_name}

        from_clause_list.append(
            "_".join(temp_model_name.split(".")) + ' ' + "".join([x[0] for x in temp_model_name.split(".")]))

        select_clause_list.append('ROW_NUMBER () over() as id')

        # x_name field default value set
        rec_name = self.env[temp_model_name]._rec_name_fallback()
        if not self.env[temp_model_name]._fields.get(rec_name).store :
            rec_name = 'id'
        select_clause_list.append("".join([x[0] for x in temp_model_name.split(".")]) + '.' +
                                  rec_name + ' as x_name')

        for column_id in rec.ks_cr_column_ids:
            column_id.ks_cr_field_id.sudo().unlink()
            temp_model_name = ks_model.model
            current_abbr_chain = "".join([x[0] for x in temp_model_name.split(".")])
            field_chain = column_id.ks_model_field_chan.split(".")

            for field in field_chain:
                field_id = self.env['ir.model.fields'].search([('model', '=', temp_model_name), ('name', '=', field)])
                if field_id.relation:
                    prev_abbr = current_abbr_chain
                    current_abbr_chain = current_abbr_chain + '_' + "".join(
                        [x[0] for x in field_id.relation.split(".")])
                    temp_model_name = field_id.relation

                    if query_data.get(current_abbr_chain) != field_id.relation:
                        i = 1
                        while query_data.get(current_abbr_chain) and query_data.get(
                                current_abbr_chain) != field_id.relation:
                            current_abbr_chain + str(i)
                            i += 1

                        query_data[current_abbr_chain] = field_id.relation

                        if field_id.ttype == 'one2many':
                            join_type = 'left join '
                            join_condition = ' on %s = %s' % (
                                current_abbr_chain + '.' + field_id.relation_field, prev_abbr + '.id')

                            from_clause_list.append(join_type + "_".join(
                                temp_model_name.split(".")) + ' ' + current_abbr_chain + ' ' + join_condition)
                        elif field_id.ttype == 'many2many':
                            attrs = {}
                            rel, col1, col2 = self.ks_many2many_names(field_id['model'], field_id['relation'])
                            attrs['relation'] = field_id['relation_table'] or rel
                            attrs['column1'] = field_id['column1'] or col1
                            attrs['column2'] = field_id['column2'] or col2
                            rel_chain = current_abbr_chain + "_rel"

                            from_clause_list.append(
                                'left join ' + attrs['relation'] + ' ' + rel_chain + ' on ' + rel_chain + '.' + attrs[
                                    'column1'] + '=' + prev_abbr + '.id')

                            from_clause_list.append('left join ' + "_".join(
                                temp_model_name.split(".")) + ' ' + current_abbr_chain + ' on ' + rel_chain + '.' +
                                                    attrs['column2'] + '=' + current_abbr_chain + '.id')
                        else:
                            join_type = 'left join '
                            join_condition = ' on %s = %s' % (
                                prev_abbr + '.' + field_id.name, current_abbr_chain + '.id')

                            from_clause_list.append(join_type + "_".join(
                                temp_model_name.split(".")) + ' ' + current_abbr_chain + ' ' + join_condition)

            if query_data.get(current_abbr_chain):
                field = field_chain[-1]
                field_id = self.env['ir.model.fields'].search([('model', '=', temp_model_name), ('name', '=', field)])
                ks_field_name = 'x_ks_' + field
                i = 1

                while ks_field_name in field_list:
                    ks_field_name = 'x_ks_' + str(i) + '_' + field
                    i += 1

                field_list.append(ks_field_name)

                if column_id.ks_incl_search_filter:
                    search_filter_field_list.append(ks_field_name)
                if column_id.ks_incl_group_filter:
                    group_filter_field_list.append(ks_field_name)

                select_clause_list.append(current_abbr_chain + '.' + field + ' as ' + ks_field_name)
                self._ks_cr_fields(rec, column_id, ks_field_name, field_id, column_id.name)

        ks_query = 'SELECT %s FROM %s' % (",".join(select_clause_list), " ".join(from_clause_list))
        self.ks_query_validate(ks_query)

        self.ks_create_tree_view(rec, field_list)
        self.ks_create_search_filter_view(rec, search_filter_field_list, group_filter_field_list)
        return ks_query

    def _ks_cr_model_init(self, rec):
        cr_model = rec.ks_cr_model_id
        table = self.env[cr_model.model]._table
        tools.drop_view_if_exists(self.env.cr, table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (table, self._query(rec)))

    # Tree View override to show all fields in list view
    def ks_create_tree_view(self, rec, field_list):
        cr_model = rec.ks_cr_model_id
        rec.ks_tree_view_id = self.env['ir.ui.view'].sudo().create({
            'name': rec.name + ' List View',
            'model': cr_model.model,
            'arch': '<tree string="%s">' % (rec.name + ' List View') + "\n".join(
                ['<field name="%s"/>' % x for x in field_list]) + '</tree>',
        })

    def ks_create_search_filter_view(self, rec, search_filter_field_list, group_filter_field_list):
        cr_model = rec.ks_cr_model_id
        fields_desc = self.env[cr_model.model]._fields

        group_arch = '<group expand="0" string="Group By">' + \
                     "\n".join(['<filter name="%s" string="%s" context="%s"/>' % (
                         x, fields_desc.get(x).string, "{'group_by': '%s'}" % x) for x in group_filter_field_list]) + \
                     '</group>'

        search_filter_arch = "\n".join(['<field name="%s"/>' % x for x in search_filter_field_list])

        rec.ks_search_view_id = self.env['ir.ui.view'].sudo().create({
            'name': rec.name + ' Search View',
            'model': cr_model.model,
            'arch': '<search string="%s">' % ('Search ' + rec.name) + search_filter_arch + group_arch + '</search>',
        })

    def ks_many2many_names(self, model_name, relation):
        """ Return default names for the table and columns of a custom many2many field. """
        rel1 = self.env[model_name]._table
        rel2 = self.env[relation]._table
        table = '%s_%s_rel' % tuple(sorted([rel1, rel2]))
        if rel1 == rel2:
            return (table, 'id1', 'id2')
        else:
            return (table, '%s_id' % rel1, '%s_id' % rel2)

    # To remove columns if model is changed
    @api.onchange('ks_model_id')
    def _onchange_ks_model(self):
        for rec in self:
            rec.ks_cr_column_ids = False

    def ks_query_validate(self, ks_query):
        with api.Environment.manage():
            try:
                conn = sql_db.db_connect(self.env.cr.dbname)
                new_env = api.Environment(conn.cursor(), self.env.uid,
                                          self.env.context)
                new_env.cr.execute(ks_query)
            except Exception as e:
                raise UserError(_(e))
            finally:
                new_env.cr.close()
