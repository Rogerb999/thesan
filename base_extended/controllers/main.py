from odoo.addons.web.controllers.main import DataSet as DS
from odoo import http
from odoo.http import request


class DataSet(DS):

    @http.route('/web/dataset/search_wplan', type='json', auth="user")
    def search_wplan(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        return self.do_search_read_WPLAN(model, fields, offset, limit, domain, sort)

    def do_search_read_WPLAN(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        Model = request.env[model]
        records = Model.search_read(domain, fields,
                                    offset=offset or 0, limit=limit or False, order=sort or False)
        if not records:
            return {
                'length': 0,
                'records': []
            }
        if limit and len(records) == limit:
            length = Model.search_count(domain)
        else:
            length = len(records) + (offset or 0)
        res_details = {
            'length': length,
            'records': records
        }
        search_fields_config_id = request.env['search.fields.config'].search([('object_id.model', '=', model)])
        if not search_fields_config_id:
            return res_details
        extra_info = []
        ssfc_obj = request.env['search.sub.fields.config']
        for res in res_details.get('records', False):
            model_id = request.env[model].browse(int(res.get('id')))
            value = {}
            value.update(res)
            for rel in search_fields_config_id.field_ids:
                if fields and rel.field_name not in fields or not rel.sub_field_ids:
                    continue
                key = rel.field_name + '_extra'
                value[key] = []
                main_sub_fields = getattr(model_id, rel.field_name)
                om_sub_list_names = []
                sub_list_names = []
                for sub_field in rel.sub_field_ids:
                    sub_list_names.append(sub_field.name)
                    if sub_field.ttype in ['one2many', 'many2many']:
                        om_sub_list_names.append(sub_field.name)
                for main_sub_field in main_sub_fields:
                    value_of_fields = main_sub_field.read(sub_list_names)
                    for oms in om_sub_list_names:
                        oms_ids = getattr(main_sub_field, oms)
                        if oms_ids:
                            oms_key = oms + '_extra'
                            value_of_fields[0][oms_key] = []
                            ssfc_id = ssfc_obj.search([('model_id.model', '=', oms_ids[0]._name)])
                            sub_field_config_list = [field_id.name for field_id in ssfc_id.field_ids] or ['name']
                            for oms_id in oms_ids:
                                value_of_fields[0][oms_key].extend(oms_id.read(sub_field_config_list))
                    value[key].extend(value_of_fields)
            extra_info.append(value)
        res_details.update({'records': extra_info})
        return res_details
