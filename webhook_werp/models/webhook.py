# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _, registry
from odoo.tools.safe_eval import safe_eval
import json
import threading
import requests
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)
from datetime import date, datetime

TYPE2REFUND = {'write': {}}


class Basewebhook_werp(models.Model):
    _name = 'webhook_werp'
    _inherit = ['base.automation', 'portal.mixin', 'mail.thread',
                'mail.activity.mixin']

    url = fields.Char(string='URL', track_visibility='always')
    default_json = fields.Text(
        string="Default JSON", track_visibility='always')
    url_type = fields.Selection(
        [('you', 'YOU'), ('w_plan', 'W-Plan'), ('other', 'Other')], default='you',
        track_visibility='always')
    check_active_deactive = fields.Boolean(
        'Check for Active/Deactivate', track_visibility='always')
    object_confg_id = fields.Many2one(
        'object.confg', 'Object Config',
        domain="[('object_id', '=', model_id)]")

    def sent_data(self, model_name, final_data, record_id):
        headers = {'content-type': 'application/json'}
        _logger.info(" Final Data Post : %s", json.dumps(final_data))
        _logger.info(" URL : %s", self.url)
        data = requests.post(self.url, data=json.dumps(final_data), headers=headers)
        _logger.info(" webhook_werp Info : %s", data)
        if model_name not in ['hr.employee', 'hr.contract']:
            _logger.info(" webhook_werp Process Done!")
        elif record_id and self.url_type == 'other' \
                and model_name in ['hr.employee', 'hr.contract']:
            if model_name == 'hr.employee':
                employee_id = record_id.id
            else:
                employee_id = record_id.employee_id.id
            data_dict = json.loads(data.text)
            db_registry = registry(record_id._cr.dbname)
            with api.Environment.manage(), db_registry.cursor() as cr:
                cr.execute('UPDATE hr_employee SET '
                           'response_message=%s, '
                           'response_time=%s WHERE id=%s', (
                               data_dict.get('Msg'),
                               fields.Datetime.now(),
                               employee_id))
        _logger.info(" webhook_werp Process Done!")

    def _filter_post_export_domain(self, records):
        """ Filter the records that satisfy the postcondition
         of action ``self``. """
        if self.filter_domain and records:
            domain = [('id', 'in', records.ids)
                      ] + safe_eval(
                self.filter_domain, self._get_eval_context())
            return records.search(domain), domain
        else:
            return records, None

    @api.model_cr
    def _register_hook(self):
        """ Patch models that should trigger action rules based on creation,
            modification, deletion of records and form onchanges.
        """
        #
        # Note: the patched methods must be defined inside another function,
        # otherwise their closure may be wrong. For instance, the function
        # create refers to the outer variable 'create', which you expect to be
        # bound to create itself. But that expectation is wrong if create is
        # defined inside a loop; in that case,
        # the variable 'create' is bound to
        # the last function defined by the loop.
        webhook_werp_id = False
        def make_create():
            """ Instanciate a create method that processes action rules. """
            @api.model_create_multi
            def create(self, vals_list, **kw):
                # retrieve the action rules to possibly execute
                actions = self.env['base.automation']._get_actions(self, ['on_create', 'on_create_or_write'])
                # call original method
                records = create.origin(self.with_env(actions.env), vals_list, **kw)
                # check postconditions, and execute actions on the records that satisfy them
                for action in actions.with_context(old_values=None):
                    action._process(action._filter_post(records))
                return records.with_env(self.env)

            return create

        def make_write():
            """ Instanciate a _write method that processes action rules. """
            #
            # Note: we patch method _write() instead of write() in order to
            # catch updates made by field recomputations.
            #
            @api.multi
            def _write(self, vals, **kw):
                # retrieve the action rules to possibly execute
                actions = self.env['base.automation']._get_actions(self, ['on_write', 'on_create_or_write'])
                records = self.with_env(actions.env)
                # check preconditions on records
                pre = {action: action._filter_pre(records) for action in actions}
                # read old values before the update
                old_values = {
                    old_vals.pop('id'): old_vals
                    for old_vals in (records.read(list(vals)) if vals else [])
                }
                # call original method
                _write.origin(records, vals, **kw)
                # check post conditions, and execute actions on the records that satisfy them
                for action in actions.with_context(old_values=old_values):
                    records, domain_post = action._filter_post_export_domain(pre[action])
                    action._process(records, domain_post=domain_post)
                return True

            return _write

        def make_unlink():
            """ Instanciate an unlink method that processes action rules. """
            @api.multi
            def unlink(self, **kwargs):
                # retrieve the action rules to possibly execute
                actions = self.env['webhook_werp']._get_actions(self, ['on_unlink'])
                records = self.with_env(actions.env)
                # records.mapped('')
                record_list = []
                # for record_id in records:
                #     record_list.append(record_id.read(
                #         ['name', 'street', 'street2', 'country_id']))
                # check conditions, and execute actions on the records that satisfy them
                for action in actions:
                    action._process(action._filter_post(records))
                # thread = threading.Thread(
                #     target=webhook_werp_id.sent_data,
                #     args=(webhook_werp_id.model_name, record_list, False))
                # thread.start()
                # call original method
                return unlink.origin(self, **kwargs)
            return unlink

        def make_onchange(action_rule_id):
            """ Instanciate an onchange method for the given action rule. """
            def base_automation_onchange(self):
                action_rule = self.env['webhook_werp'].browse(action_rule_id)
                result = {}
                server_action = action_rule.action_server_id.with_context(
                    active_model=self._name, onchange_self=self)
                res = server_action.run()
                if res:
                    if 'value' in res:
                        res['value'].pop('id', None)
                        self.update({
                            key: val for key, val in
                            res['value'].items() if key in self._fields})
                    if 'domain' in res:
                        result.setdefault('domain', {}).update(res['domain'])
                    if 'warning' in res:
                        result['warning'] = res['warning']
                return result

            return base_automation_onchange

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`,
            unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all actions, and patch their corresponding model
        for action_rule in self.with_context({}).search([]):
            Model = self.env.get(action_rule.model_name)

            # Do not crash if the model of the base_action_rule was uninstalled
            if Model is None:
                _logger.warning("Action rule with ID %d depends on model %s" %
                                (action_rule.id,
                                 action_rule.model_name))
                continue
            webhook_werp_id = action_rule
            default_json = action_rule.default_json or '{}'
            if action_rule.trigger == 'on_create':
                patch(Model, 'create', make_create())

            elif action_rule.trigger == 'on_create_or_write':
                patch(Model, 'create', make_create())
                patch(Model, '_write', make_write())

            elif action_rule.trigger == 'on_write':
                patch(Model, '_write', make_write())

            elif action_rule.trigger == 'on_unlink':
                patch(Model, 'unlink', make_unlink())

            elif action_rule.trigger == 'on_change':
                # register an onchange method for the action_rule
                method = make_onchange(action_rule.id)
                for field_name in action_rule.on_change_fields.split(","):
                    Model._onchange_methods[field_name.strip()].append(method)

    @api.multi
    def get_generic_details_common(self, webhook_werp_type, vals, record):
        final_data = {
            'from': {},
            'to': {},
            'data': {
                'normal_field': [],
            },
            'webhook_werp_type': webhook_werp_type,
            'webhook_werp_history_id': {},
            'reference': '%s,%s' % (record._name, record.id)
        }
        if record.read()[0].get('employee_id'):
            final_data['to'].update({
                'employee_id': record.employee_id.id,
            })
        else:
            final_data['to'].update({
                'id': record.id,
                'employee_id': 0
            })
        final_data['to'].update({
            'name': record.display_name,
            'token': ''
        })
        read_data = record.read(vals.keys())[0]
        return final_data, read_data

    @api.model
    def action_webhook_werp_create_form_data_common(self, webhook_werp_type, record):
        webhook_werp_ids = self.env['webhook_werp'].search([
            ('model_id.model', '=', record._name),
            ('trigger', 'in', ['on_create', 'on_create_or_write', 'on_unlink']),
            ('url_type', '=', 'you')])
        for webhook_werp_id in webhook_werp_ids:
            final_data = {'from': {}, 'to': {}, 'data': [],
                          'webhook_werp_type': webhook_werp_type,
                          'default_data': json.loads(
                              webhook_werp_id.default_json or '{}'),
                          'webhook_werp_history_id': {},
                          'reference': '%s,%s' % (record._name, record.id)
                          }
            if record.read()[0].get('employee_id'):
                final_data['to'].update({
                    'employee_id': record.employee_id.id,
                })
            else:
                final_data['to'].update({
                    'id': record.id,
                    'employee_id': 0
                })
            final_data['to'].update({
                'name': record.display_name,
                'token': ''
            })
            if webhook_werp_id.object_confg_id:
                fields_data = webhook_werp_id.object_confg_id.get_data_common(
                    record)
                final_data.update(fields_data)
                webhook_werp_history_id = \
                    self.env['webhook_werp.history'].action_webhook_werp_history_create(
                        final_data)
                if webhook_werp_history_id:
                    final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                    thread = threading.Thread(
                        target=webhook_werp_id.sent_data,
                        args=(webhook_werp_id.model_name, final_data, record))
                    thread.start()
                return True
            else:
                vals = record.read()[0]
                if webhook_werp_id and vals:
                    final_data, read_data = self.get_generic_details_common(
                        webhook_werp_type, vals, record)
                    # json_data = []
                    for v_data in vals:
                        if isinstance(read_data.get(v_data), tuple):
                            vals.update({v_data: read_data.get(v_data)[1]})
                        else:
                            if isinstance(vals.get(v_data), (datetime, date)):
                                vals.update({v_data: vals.get(
                                    v_data).isoformat()})
                    final_data.update({'data': vals})
                    webhook_werp_history_id = \
                        self.env['webhook_werp.history'].action_webhook_werp_history_create(
                            final_data)
                    if webhook_werp_history_id:
                        final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                        thread = threading.Thread(
                            target=webhook_werp_id.sent_data,
                            args=(webhook_werp_id.model_name, final_data, record))
                        thread.start()
                    return True


class Basewebhook_werpHistory(models.Model):
    _name = 'webhook_werp.history'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    from_emp_id = fields.Integer(
        string="From Emp ID", track_visibility='always')
    to_emp_id = fields.Integer(
        string="To Emp ID", track_visibility='always')
    json_data = fields.Text(
        string="Json Data", track_visibility='always')
    status = fields.Boolean(
        string="Status", track_visibility='always')
    email_from = fields.Char(
        string="Email From", track_visibility='always')
    email_to = fields.Char(
        string="Email To", track_visibility='always')
    webhook_werp_type = fields.Integer(
        string="webhook_werp Type", track_visibility='always')
    default_data = fields.Text(
        string="", required=False, track_visibility='always')
    reference = fields.Reference(
        string='Related Record',
        selection='_reference_models', track_visibility='always')

    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].sudo().search([])
        return [(model.model, model.name) for model in models]

    @api.multi
    def action_webhook_werp_history_create(self, final_data):
        domain = []
        if final_data.get('from') and final_data.get(
                'from')['employee_id']:
            ('from_emp_id', '=', final_data.get('from')['employee_id'])
        if final_data.get('to') and final_data.get(
                'to')['employee_id']:
            domain.append(('to_emp_id', '=', final_data.get('to')['employee_id']))
        if json.dumps(final_data.get('from')):
            domain.append(('email_from', '=', json.dumps(
                final_data.get('from'))))
        if json.dumps(final_data.get('to')):
            domain.append(('email_to', '=', json.dumps(final_data.get('to'))))
        if final_data.get('webhook_werp_type'):
            domain.append(('webhook_werp_type', '=', final_data.get('webhook_werp_type')))
        if json.dumps(final_data['data']):
            domain.append(('json_data', '=', json.dumps(final_data['data'])))
        if final_data.get('reference'):
            domain.append(('reference', '=', final_data.get('reference')))
        if domain:
            record = self.search(domain)
        if not record:
            return self.create({
                'from_emp_id': final_data.get('from') and final_data.get(
                    'from')['employee_id'],
                'to_emp_id': final_data.get('to') and final_data.get(
                    'to')['employee_id'],
                'email_from': json.dumps(final_data.get('from')),
                'email_to': json.dumps(final_data.get('to')),
                'webhook_werp_type': final_data.get('webhook_werp_type'),
                'json_data': json.dumps(final_data['data']),
                'reference': final_data.get('reference'),
            })
