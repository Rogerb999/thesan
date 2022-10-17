from odoo import fields, models, api, _
from odoo.exceptions import UserError


class KsCrColumn(models.Model):
    _name = 'ks_custom_report.ks_column'
    _description = 'Report Field'

    name = fields.Char(string="Field Name", required=True)
    ks_cr_model_id = fields.Many2one(comodel_name="ks_custom_report.ks_report", string="Report Model")
    ks_model_field_chan = fields.Char(string="Field Chain", required=True, default="id")
    ks_model_name = fields.Char(compute='_onchange_ks_cr_model_id', string="Model Name")
    ks_cr_field_id = fields.Many2one("ir.model.fields", string="Report Field")

    # Search Group Filter field
    ks_incl_search_filter = fields.Boolean(string="Search Filter", default=True)
    ks_incl_group_filter = fields.Boolean(string="Group Filter", default=True)

    @api.onchange('ks_cr_model_id')
    def _onchange_ks_cr_model_id(self):
        for rec in self:
            if rec.ks_cr_model_id.ks_model_id.id:
                rec.ks_model_name = rec.ks_cr_model_id.ks_model_id.model

    @api.multi
    def unlink(self):
        for rec in self:
            rec.ks_cr_model_id.ks_tree_view_id.sudo().unlink()
            rec.ks_cr_model_id.ks_search_view_id.sudo().unlink()
            rec.ks_cr_model_id.ks_pivot_view_id.sudo().unlink()

            rec.ks_cr_field_id.sudo().unlink()
            return super(KsCrColumn, self).unlink()

    # Handling (checking) Invalid Field chan
    @api.multi
    def write(self, values):
        for rec in self:
            if rec.ks_cr_model_id and values.get('ks_model_field_chan'):
                model = self.env[rec.ks_cr_model_id.ks_model_id.model]
                field_chain = values['ks_model_field_chan'].split(".")
                values['ks_model_field_chan'] = ".".join(self.ks_fallback_field(model, field_chain))
        return super(KsCrColumn, self).write(values)

    @api.model
    def create(self, values):
        if values.get('ks_cr_model_id') and values.get('ks_model_field_chan'):
            model = self.env[self.ks_cr_model_id.browse(values.get('ks_cr_model_id')).ks_model_id.model]
            field_chain = values['ks_model_field_chan'].split(".")
            values['ks_model_field_chan'] = ".".join(self.ks_fallback_field(model,field_chain))
        return super(KsCrColumn, self).create(values)


    def ks_fallback_field(self, model, field_chain):
        """
        Recursive Function for relation field to find fallback name field
        :param model: odoo_model class object
        :param field_chain: list
        :return: list
        """

        tmp_model_name = False
        for field in field_chain:
            tmp_model_name = model._fields.get(field).comodel_name
            model = self.env[tmp_model_name] if tmp_model_name else model

        if tmp_model_name:
            rec_name = model._rec_name_fallback()
        else:
            rec_name = field_chain[-1]

        if model._fields.get(rec_name).store:
            field_chain.append(rec_name) if rec_name not in field_chain else field_chain

        elif model._fields.get(rec_name).related:
            field_chain.extend(self.ks_fallback_field(model, list(model._fields.get(rec_name).related)))
        else:
            field_chain.append('id')

        return field_chain