# -*- coding: utf-8 -*-

import pytz
import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import float_compare
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
#from ip2geotools.databases.noncommercial import DbIpCity
from odoo.http import request


class HrNovelty(models.Model):
    _name = 'hr.novelty'
    _description = 'Novelty'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    @api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            if rec.employee_id.address_home_id.vat:
                rec.identification_id = rec.employee_id.address_home_id.vat

    @api.depends('employee_id')
    def _compute_wage(self):
        for rec in self:
            contract = self.env['hr.contract'].search(
                [('state', 'not in', ['close', 'cancel']),
                 ('employee_id', '=', rec.employee_id.id)],
                limit=1)
            if contract:
                rec.wage = contract.wage
                rec.fix_wage_amount = contract.fix_wage_amount
                rec.flex_wage_amount = contract.flex_wage_amount

    name = fields.Char(copy=False, required=True, readonly=True,
                       default=lambda self: _('New'), help="Sequence Name",
                       track_visibility='onchange')
    type_id = fields.Many2one('hr.novelty.type', string="Type", readonly=True,
                              states={'draft': [('readonly', False)]},
                              track_visibility='onchange')
    subtype_id = fields.Many2one('hr.novelty.type.subtype', string="Sub-Type",
                                 readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]})
    event_id = fields.Many2one(
        'hr.novelty.event', string="Event", readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange')
    responsible_required = fields.Boolean(
        related="event_id.responsible_required")
    responsible_id = fields.Many2one(
        'hr.employee', string="Responsible",
        readonly=True, track_visibility='onchange',
        states={'draft': [('readonly', False)]},)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", readonly=True,
        track_visibility='onchange',
        states={'draft': [('readonly', False)]},
        )
    partner_id = fields.Many2one('res.partner', track_visibility='onchange',
                                 help="third party who owns the debt")
    start_date = fields.Datetime(readonly=True,
                                 required=True,
                                 default=lambda self: fields.datetime.now(),
                                 states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    unit_half = fields.Boolean(string="Half Day", track_visibility='onchange')
    start_date_period = fields.Selection(
        [('am', 'Morning'), ('pm', 'Afternoon')],
        track_visibility='onchange')
    end_date = fields.Datetime(readonly=True, track_visibility='onchange',
                               states={'draft': [('readonly', False)]},)
    approved_date = fields.Datetime(readonly=True, track_visibility='onchange',
                                    states={'draft': [('readonly', False)]})
    total_days = fields.Float(compute='_compute_total_days', store=True)
    total_hours = fields.Float(
        compute='_compute_total_days')
    amount = fields.Float(readonly=True, track_visibility='onchange',
                          states={'draft': [('readonly', False)]},)
    description = fields.Text(readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]},)
    reject_reason = fields.Text(string="Reject Reason", readonly=True,
                                states={'draft': [('readonly', False)]},
                                track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('wait', 'Wait'),
         ('wait_comments', 'Wait for comments'),
         ('wait_second_approval', 'Waiting Second Approval'),
         ('approved', 'Approved'),
         ('processed', 'Processed'),
         ('cancel', 'Cancel'),
         ('rejected', 'Rejected')],
        default='draft',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]})
    is_user_appr = fields.Boolean(
        "Logged user is the approver",
        compute='compute_is_user_appr',
        store=False)
    is_sec_appr_user = fields.Boolean(
        "Logged user is the second approver",
        compute='compute_is_sec_appr_user',
        store=False)
    company_only = fields.Boolean(
        related="event_id.company_only")
    is_aplica_fecha_final = fields.Boolean(
        related="event_id.is_aplica_fecha_final")
    leave_id = fields.Many2one('hr.leave', 'Leave',
                               track_visibility='onchange')
    file_name = fields.Char("File Name", track_visibility='onchange')
    support = fields.Binary('Support')
    support_name = fields.Char('Support Name', track_visibility='onchange')
    support_size = fields.Char('Support Size', track_visibility='onchange')
    identification_id = fields.Char(
        compute='_compute_identification_id',
        string='Identification No',
        store=True)
    hr_job_id = fields.Many2one(
        'hr.job', string="HR Job", copy=False, track_visibility='onchange')
    recruitment_reason_id = fields.Many2one(
        'recruitment.reason',
        'Recruitment Reasons', copy=False, track_visibility='onchange')
    support_attachment_url = fields.Char(
        "Support URL", track_visibility='onchange')
    is_requiere_adjunto = fields.Boolean(
        related="event_id.is_requiere_adjunto")
    is_recruitment = fields.Boolean(
        related="event_id.is_recruitment")
    is_motivo_de_retiro = fields.Boolean(
        related="event_id.is_motivo_de_retiro")
    motivo_talento_id = fields.Many2one(
        'motivo.talento', 'Motivo Talento', track_visibility='onchange')
    is_h_e_procedimiento = fields.Boolean(
        related="event_id.is_h_e_procedimiento")
    h_e_procedimiento = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
        ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
        ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'),
        ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
        ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'),
        ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'),
        ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
        ('46', '46'), ('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
        ('51', '51'), ('52', '52'), ('53', '53'), ('54', '54'), ('55', '55'),
        ('56', '56'), ('57', '57'), ('58', '58'), ('59', '59'), ('60', '60'),
        ('61', '61'), ('62', '62'), ('63', '63'), ('64', '64'), ('65', '65'),
        ('66', '66'), ('67', '67'), ('68', '68'), ('69', '69'), ('70', '70'),
        ('71', '71'), ('72', '72'), ('73', '73'), ('74', '74'), ('75', '75'),
        ('76', '76'), ('77', '77'), ('78', '78'), ('79', '79'), ('80', '80'),
        ('81', '81'), ('82', '82'), ('83', '83'), ('84', '84'), ('85', '85'),
        ('86', '86'), ('87', '87'), ('88', '88'), ('89', '89'), ('90', '90')],
        string='H.E Procedimiento', track_visibility='onchange')
    is_horas_fijas = fields.Boolean(
        related="event_id.is_horas_fijas")
    transfer_employee = fields.Boolean(related="event_id.transfer_employee")
    total_fix_hours = fields.Float(string="Total Fix Hours",
                                   track_visibility='onchange',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    total_horas_fijas = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
        ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
        ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'),
        ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
        ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'),
        ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'),
        ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
        ('46', '46'), ('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
        ('51', '51'), ('52', '52'), ('53', '53'), ('54', '54'), ('55', '55'),
        ('56', '56'), ('57', '57'), ('58', '58'), ('59', '59'), ('60', '60'),
        ('61', '61'), ('62', '62'), ('63', '63'), ('64', '64'), ('65', '65'),
        ('66', '66'), ('67', '67'), ('68', '68'), ('69', '69'), ('70', '70'),
        ('71', '71'), ('72', '72'), ('73', '73'), ('74', '74'), ('75', '75'),
        ('76', '76'), ('77', '77'), ('78', '78'), ('79', '79'), ('80', '80'),
        ('81', '81'), ('82', '82'), ('83', '83'), ('84', '84'), ('85', '85'),
        ('86', '86'), ('87', '87'), ('88', '88'), ('89', '89'), ('90', '90')],
        string='Total Horas Fijas', track_visibility='onchange')
    is_tipo_de_incapacidad = fields.Boolean(
        related="event_id.is_tipo_de_incapacidad")
    is_eps = fields.Boolean(string='EPS', track_visibility='onchange')
    is_arl = fields.Boolean(string='ARL', track_visibility='onchange')
    is_adjunto_obligatorio = fields.Boolean(
        related="event_id.is_adjunto_obligatorio")
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.ref('base.COP'),
        track_visibility='onchange')
    experience_id = fields.Many2one(
        'hr.experience.time', 'Experience Time', track_visibility='onchange')
    hr_novelty_job_id = fields.Many2one(
        'hr.novelty.job', 'Recruitment', track_visibility='onchange')
    hr_novelty_job_id_state = fields.Selection(
        related='hr_novelty_job_id.state')
    language_level_ids = fields.One2many(
        'language.level.details', 'novelty_id', 'Language/Level Details')
    leave_message = fields.Char('Leave Message', track_visibility='onchange')
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account', track_visibility='onchange')
    requered_account = fields.Boolean(
        related="event_id.requered_account")
    increase_salary = fields.Boolean(
        related="event_id.increase_salary", store=True)
    requered_attachment_lic = fields.Boolean(
        related="event_id.requered_attachment_lic")
    show_you = fields.Boolean(
        related="event_id.show_you")
    wage = fields.Float(compute='_compute_wage')
    fix_wage_amount = fields.Float(
        compute='_compute_wage')
    flex_wage_amount = fields.Float(
        compute='_compute_wage')
    birth_certificate = fields.Binary()
    certificate_born_alive = fields.Binary()
    certificate_week_of_gestation = fields.Binary()
    original_maternity_leave = fields.Binary()
    relationship_id = fields.Many2one(
        'hr.family.relationship', 'Family Relationship',
        track_visibility='onchange')
    leave_code_id = fields.Many2one(
        'hr.leave.code', 'Leave Code', track_visibility='onchange')
    approved_by = fields.Many2one('res.users', 'Approved By')
    confidential = fields.Boolean()
    hiring_type = fields.Selection(
        [('direct', 'Direct'), ('temporary', 'Temporary')],
        default='direct')
    work_group_id = fields.Many2one('work.group', 'Work Group')
    observation_recruitment = fields.Text()
    project_type = fields.Text()
    observation_increase = fields.Text()
    date = fields.Datetime(
        track_visibility='onchange')
    location = fields.Char(
        'Location',
        track_visibility='onchange')
    ip_from = fields.Char(
        'IP From',
        track_visibility='onchange')
    approved_ip_date = fields.Datetime(
        track_visibility='onchange', string="Approved Date")
    approved_location = fields.Char(
        'Approved Location',
        track_visibility='onchange')
    approved_ip_from = fields.Char(
        'Approved IP From',
        track_visibility='onchange')
    contact_id = fields.Many2one('res.partner', 'Contact', copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contract', copy=False)
    wage_assign = fields.Float()
    Fix_wage_assing = fields.Float()
    subcontract = fields.Boolean(
        related="contract_id.subcontract")
    is_end_business_day = fields.Boolean(
        related="event_id.is_end_business_day")
    end_business_day = fields.Datetime()
    upc = fields.Boolean(
        related="event_id.upc")
    family_id = fields.Many2one(
        'hr.cv.family.employee', 'HR CV Family',
        domain="[('employee_id', '=', employee_id)]")

    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(HrNovelty, self).search(
            args, offset, limit, order, count=count)
        if not self._context.get('novelty_approve'):
            return res
        if isinstance(res, int):
            return res
        login_user = self.env['res.users'].sudo().browse(self._uid)
        daf_novelty = bp_novelty = sst_novelty = self.env['hr.novelty']
        if login_user.has_group('base_product.group_daf'):
            daf_novelty = res.filtered(
                lambda novelty: novelty.event_id.approver == 'daf')
        if login_user.has_group('base_product.group_bp'):
            bp_novelty = res.filtered(
                lambda novelty: novelty.event_id.approver == 'bp')
        if login_user.has_group('base_product.group_sst'):
            sst_novelty = res.filtered(
                lambda novelty: novelty.event_id.approver == 'sst')
        # if daf_novelty and bp_novelty and sst_novelty:
        novelty_combination = daf_novelty + bp_novelty + sst_novelty
        remaining_novelty = res - novelty_combination
        for novelty in remaining_novelty:
            if novelty.event_id and novelty.event_id.is_optional_approver and\
                    novelty.event_id.optional_approver_group_id:
                self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE\
                    uid=%s AND gid=%s""", (
                    self._uid,
                    novelty.event_id.optional_approver_group_id.id))
                if bool(self._cr.fetchone()):
                    novelty_combination += novelty
            if novelty.event_id and\
                    novelty.event_id.is_optional_approver_2 and\
                    novelty.event_id.optional_approver2_group_id:
                self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE\
                    uid=%s AND gid=%s""", (
                    self._uid,
                    novelty.event_id.optional_approver2_group_id.id))
                if bool(self._cr.fetchone()):
                    novelty_combination += novelty
        return novelty_combination

    @api.constrains('total_days', 'start_date', 'end_date', 'subtype_id')
    def limit_total_days(self):
        if self.event_id:
            min_days = self.event_id.min_days
            max_days = self.event_id.max_days
            if (self.total_days < min_days) or (
                self.total_days > max_days) and\
                    self.subtype_id.name != 'Fija':
                raise UserError(_("the amount of days exceeds "
                                  "(default or excess) the event limit"))
            return False
        '''
        if self.start_date and self.end_date:
            tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
            start_utc = pytz.timezone('UTC').localize(
                self.start_date, is_dst=False)
            context_start = start_utc.astimezone(pytz.timezone(tz_name))
            end_utc = \
                pytz.timezone('UTC').localize(self.end_date, is_dst=False)
            context_end = end_utc.astimezone(pytz.timezone(tz_name))
            if context_start.date() == context_end.date() and \
                    self.total_hours > 5.0:
                raise UserError(_("Total Hours must not exceed 5 hours."))
        '''

    @api.constrains('employee_id', 'start_date', 'end_date')
    def _check_date(self):
        for item in self:
            if item.subtype_id.name not in ('Fija', 'Ocasional') and \
                    not item.event_id.is_horas_fijas and not\
                    item._context.get('check_duplicate', ''):
                item_ids = self.search([
                    ('start_date', '<=', item.end_date),
                    ('end_date', '>=', item.start_date),
                    ('employee_id', '=', item.employee_id.id),
                    ('id', '<>', item.id),
                    ('subtype_id', '=', self.env.ref(
                        'hr_novelty.novelty_subtype_AUS').id),
                    ('state', 'not in', ('rejected', 'cancel'))])
                if item_ids:
                    raise UserError(
                        _("You cannot create two novelty with the same "
                            "Employee and Start Date and End Date mix."))
        return True

    @api.depends('start_date', 'end_date', 'unit_half',
                 'total_fix_hours')
    def _compute_total_days(self):
        for rec in self:
            if rec.event_id.is_horas_fijas and rec.total_fix_hours:
                rec.total_days = float((rec.total_fix_hours) / 8)
            else:
                if rec.start_date and rec.end_date:
                    start_date = rec.start_date - datetime.timedelta(hours=5)
                    end_date = rec.end_date - datetime.timedelta(hours=5)
                    rec.total_days = rec.event_id.get_total_days(
                        rec.start_date, rec.end_date, rec.employee_id)
                    rec.total_hours = rec.total_days * 8
                    global_leave_days = 0
                    if rec.event_id.calendar_type == 'employee':
                        global_leave_days = self.env[
                            'resource.calendar.leaves'].search_count(
                                [('calendar_id', '=',
                                    rec.employee_id.resource_calendar_id.id),
                                 ('resource_id', '=', False),
                                 ('date_from', '>=', start_date),
                                 ('date_to', '<=', end_date)])
                elif rec.start_date and rec.unit_half:
                    rec.total_days = '0.5'
                else:
                    rec.unit_half = 0
        return True

    @api.onchange('event_id', 'employee_id')
    def onchange_event_id_change(self):
        self.type_id = self.subtype_id = False
        if self.event_id:
            self.type_id = self.event_id.type_id
            self.subtype_id = self.event_id.subtype_id
        """Domain on employee based on the event."""
        if not self.event_id and self.employee_id:
            self.employee_id = ''
        if self.event_id and self.event_id.name ==\
                'Licencia de Maternidad' and self.employee_id and\
                self.employee_id.gender != 'female':
            self.employee_id = ''
        if self.event_id and self.event_id.name ==\
                'Licencia de Paternidad' and self.employee_id and\
                self.employee_id.gender != 'male':
            self.employee_id = ''
        if self.event_id and self.event_id.name == 'Licencia de Maternidad':
            return {'domain': {'employee_id': [
                ('gender', '=', 'female'),
                ]}}
        if self.event_id and self.event_id.name == 'Licencia de Paternidad':
            return {'domain': {'employee_id': [
                ('gender', '=', 'male'),]}}
        return 

    @api.onchange('unit_half')
    def onchange_unithalf(self):
        self.end_date = ''

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise UserError(_("The start date cannot "
                                  "occur after end date"))

    '''
    @api.constrains('type_id', 'employee_id', 'start_date')
    def novelty_validations(self):
        if self.type_id == self.env.ref('hr_novelty.novelty_event_10'):
            self._check_worked_years()
    '''

    # Reason for comment this method is above method is commented
    # which used this method
    # def _check_worked_years(self):
    #     if self.seniority >= 1:
    #         return True
    #     else:
    #         raise UserError(_("The employee hasn't a completed "
    #                           "a Year in the Company"))

    '''
    @api.constrains('event_id')
    def _check_event(self):
        if self.event_id == self.env.ref('hr_novelty.novelty_event_12'):
            if self.total_days > 3:
                message = _("Warning, this novelty exceeds the 3 days limit!")
                self.message_post(body=messages,
                                  subtype='mail.mt_comment',
                                  message_type='email',
                                  partner_ids=self.message_follower_ids.mapped('partner_id.id'))
    '''

    @api.multi
    def action_wait(self):
        if self.event_id.attachment_required:
            self.check_exist_attachment()
        vals = {}
        if self.name == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code("hr.novelty")
        vals['state'] = 'wait'
        self.write(vals)

    def check_exist_attachment(self):
        att_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.novelty'),
            ('res_id', '=', self.id)])
        if not att_ids:
            raise UserError(_("This event requires an attachment"))

    @api.multi
    def action_wait_comments(self):
        self.state = 'wait_comments'

    @api.multi
    def action_recruitment(self):
        for rec in self:
            if rec.hr_job_id:
                rec.hr_job_id.write({
                    'no_of_recruitment': rec.hr_job_id.no_of_recruitment + 1})
                hr_novelty_job_id = self.env['hr.novelty.job'].create({
                    'novelty_id': rec.id,
                    'job_id': rec.hr_job_id.id,
                    'recruitment_reason_id': rec.recruitment_reason_id.id,
                    'employee_id': rec.employee_id.id or '',
                    'state': rec.hr_job_id.state
                })
                rec.write({'hr_novelty_job_id': hr_novelty_job_id.id})

    @api.multi
    def action_approve(self, boss_employee=False):
        res = {}
        if boss_employee and self.event_id.approver == 'jd':
            if self.employee_id.id == boss_employee:
                if not self.event_id.is_aplica_fecha_final:
                    if self.event_id.second_approver_required:
                        self.state = 'wait_second_approval'
                    else:
                        res = self._create_record()
                        self.state = 'approved'
                        self.approved_date = str(fields.Datetime.now())
                        self.approved_by = self.env.uid
                else:
                    if not self.end_date and not self.is_horas_fijas:
                        raise UserError(_("Please fill end date."))
                    else:
                        if self.event_id.second_approver_required:
                            self.state = 'wait_second_approval'
                        else:
                            res = self._create_record()
                            self.state = 'approved'
                            self.approved_date = str(fields.Datetime.now())
                            self.approved_by = self.env.uid
        else:
            if not self.event_id.is_aplica_fecha_final:
                if self.event_id.second_approver_required:
                    self.state = 'wait_second_approval'
                else:
                    res = self._create_record()
                    self.state = 'approved'
                    self.approved_date = str(fields.Datetime.now())
                    self.approved_by = self.env.uid
            else:
                if not self.end_date and not self.is_horas_fijas:
                    raise UserError(_("Please fill end date."))
                else:
                    if self.event_id.second_approver_required:
                        self.state = 'wait_second_approval'
                    else:
                        res = self._create_record()
                        self.state = 'approved'
                        self.approved_date = str(fields.Datetime.now())
                        self.approved_by = self.env.uid
        return res

    @api.multi
    def action_massive_approval(self):
        """Massive Approval Novelty."""
        flag = False
        novelties = ''
        for approval in self:
            if approval.state in ['wait', 'wait_comments'] and\
                    approval.is_user_appr:
                try:
                    approval.action_approve()
                except:
                    raise ValidationError(_(
                        'Novelty:- ' + str(approval.name) +
                        ' has a problem for approval'))
            else:
                flag = True
                if not novelties:
                    novelties += str(approval.name)
                else:
                    novelties += ', ' + str(approval.name)
        if flag:
            raise ValidationError(_(
                'Some Novelties are not in the Wait/Wait for Comments or may '
                'be Logged user is the approver is False.\n Novelties:- ' +
                novelties))

    @api.multi
    def action_second_approval(self):
        if not self.contact_id:
            raise UserError(_(
                "Please enter Contact"))
        if not self.employee_id:
            raise UserError(_(
                "Please enter Employee"))
        if not self.contract_id:
            raise UserError(_(
                "Please enter Contract"))
        if self.is_sec_appr_user:
            self._create_record()
            self.state = 'approved'
            self.approved_date = str(fields.Date.today())
        else:
            raise UserError(_(
                "This user can't approve. He/She is not in the "
                "group %s" % self.event_id.second_approver_group_id.name))

    @api.multi
    def action_draft(self):
        for rec in self:
            if rec.leave_id:
                if rec.leave_id.state == 'validate':
                    rec.leave_id.action_refuse()
                    rec.leave_id.action_draft()
                rec.leave_id.unlink()
            rec.after_close = False
            rec.state = 'draft'

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.leave_id:
                if rec.leave_id.state == 'validate':
                    rec.leave_id.action_refuse()
                    rec.leave_id.action_draft()
                rec.leave_id.unlink()
            rec.state = 'cancel'

    @api.multi
    def _create_record(self):
        ''' Override this method from new modules '''

        if self.subtype_id == self.env.ref(
                'hr_novelty.novelty_subtype_AUS') and self.employee_id:
            message = self.create_leave()
            self.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type='email',
                partner_ids=self.message_follower_ids.mapped('partner_id.id'))

            tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'

            st_utc = pytz.timezone('UTC').localize(
                self.start_date, is_dst=False)
            en_utc = pytz.timezone('UTC').localize(self.end_date, is_dst=False)

            start_date_local = st_utc.astimezone(pytz.timezone(tz_name)).date()
            end_date_local = en_utc.astimezone(pytz.timezone(tz_name)).date()

            if start_date_local != self.leave_id.request_date_from or\
                    end_date_local != self.leave_id.request_date_to:
                self.leave_message =\
                    'The leave create with Start Date (%s) and End Date (%s)!' % (
                        self.leave_id.request_date_from,
                        self.leave_id.request_date_to)
                view_id = self.env.ref('hr_novelty.check_date_wizard').id
                return {
                    'name': _('Mismatch Date'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.novelty.check.date.wizard',
                    'view_id': view_id,
                    'target': 'new',
                    'context': {'message': self.leave_message},
                }
        return True

    @api.multi
    def create_leave(self):
        res = False
        if self.event_id.advance_holidays:
            res = self.create_leave_allocation()
        elif self.event_id.projection_vacation:
            res = self.create_projection_leave_allocation()
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        if not self.end_date and self.event_id.is_horas_fijas:
            self.end_date = self.start_date

        if self.start_date and self.end_date and self.employee_id:
            st_utc = pytz.timezone('UTC').localize(
                self.start_date, is_dst=False)
            en_utc = pytz.timezone('UTC').localize(self.end_date, is_dst=False)
            leave_id = self.env['hr.leave'].create({
                'novelty_ref': self.name,
                'name': self.description,
                'holiday_status_id': self.event_id.leave_type_id.id,
                'holiday_type': 'employee',
                'employee_id': self.employee_id.id,
                'request_date_from': st_utc.astimezone(pytz.timezone(tz_name)),
                'request_date_to': en_utc.astimezone(pytz.timezone(tz_name)),
                'number_of_days': self.total_days,
                'report_note': self.description,
                'is_arl': self.is_arl,
                'is_eps': self.is_eps,
                'date_from': self.start_date,
                'date_to': self.end_date,
            })
            leave_id.action_approve()
            self.leave_id = leave_id
            if res:
                res.action_refuse()
                res.action_draft()
                self._cr.execute(
                    "DELETE FROM hr_leave_allocation WHERE id=%s", (res.id,))
        return "A new Leave has been created in HR Leaves"

    @api.multi
    def create_leave_allocation(self):
        """ Allocates New Leaves to Employees based on Limit Advance in
        Novelty Event - Darshan
        :param self:     Novelty.
        :return:         Leave Allocation."""
        for rec in self:
            leave_days = rec.event_id.leave_type_id.get_days(
                rec.employee_id.id)[rec.event_id.leave_type_id.id]
            if float_compare(leave_days['virtual_remaining_leaves'],
                             rec.total_days, precision_digits=2) == -1:
                if rec.total_days - leave_days[
                        'virtual_remaining_leaves'] >\
                        rec.event_id.limit_advance:
                    raise UserError(
                        _("Novelty Event doesn't have enough "
                            "Limit Advance Days : %d assigned. Please review "
                            "the process before continue." %
                            rec.event_id.limit_advance))
                elif float_compare(rec.total_days - leave_days[
                    'virtual_remaining_leaves'], rec.event_id.limit_advance,
                    precision_digits=2) == -1 or \
                        float_compare(rec.total_days - leave_days[
                            'virtual_remaining_leaves'],
                            rec.event_id.limit_advance, precision_digits=2
                ) == 0:
                    leave_allocation_id = self.env[
                        'hr.leave.allocation'].create({
                            'name': rec.name,
                            'holiday_status_id': rec.event_id.leave_type_id.id,
                            'holiday_type': 'employee',
                            'employee_id': rec.employee_id.id,
                            'number_of_days': rec.total_days - leave_days[
                                'virtual_remaining_leaves'],
                        })
                    leave_allocation_id.action_approve()
                return leave_allocation_id

    @api.multi
    def create_projection_leave_allocation(self):
        """ Allocates New Leaves to Employees based on Projection for
        Advance Months - Darshan
        :param self:     Novelty.
        :return:         Leave Allocation."""
        for rec in self:
            leave_days = rec.event_id.leave_type_id.get_days(
                rec.employee_id.id)[rec.event_id.leave_type_id.id]
            if float_compare(leave_days['virtual_remaining_leaves'],
                             rec.total_days, precision_digits=2) == -1:
                # today = date.today()
                date1 = rec.start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                date1 = datetime.datetime.strptime(
                    date1, DEFAULT_SERVER_DATETIME_FORMAT)
                current_date = datetime.date.today().replace(
                    day=1).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                current_date = datetime.datetime.strptime(
                    current_date, DEFAULT_SERVER_DATETIME_FORMAT)
                month_diff = relativedelta(date1, current_date).months
                if month_diff:
                    projected_leave = month_diff * 1.25
                    if rec.total_days > leave_days[
                            'virtual_remaining_leaves'] + projected_leave:
                        raise UserError(
                            _("Novelty Event doesn't have enough Projection "
                                "Vacation leaves. Please review the process "
                                "before continue."))
                    leave_allocation_id = self.env[
                        'hr.leave.allocation'].create({
                            'name': rec.name,
                            'holiday_status_id': rec.event_id.leave_type_id.id,
                            'holiday_type': 'employee',
                            'employee_id': rec.employee_id.id,
                            'number_of_days': rec.total_days -
                            leave_days['virtual_remaining_leaves'],
                        })
                    leave_allocation_id.action_approve()
                    return leave_allocation_id

    @api.multi
    def action_process(self):
        if not self.env.user.has_group('hr_novelty.group_novelty_process'):
            raise ValidationError(_("You are not allowed for this process!"))
        if not self.event_id.is_aplica_fecha_final:
            self.state = 'processed'
        else:
            payslip = self.env['hr.payslip'].search_count([
                ('state', 'in', ['done', 'paid']),
                ('employee_id', '=', self.employee_id.id),
                ('date_from', '<=', self.end_date),
                ('date_to', '>=', self.end_date)])
            if self.end_date:
                if fields.Date.today().month >= self.end_date.month and\
                        fields.Date.today().year >= self.end_date.year:
                    self.state = 'processed'

    @api.multi
    def action_set_to_approve(self):
        self.state = 'approved'

    @api.multi
    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.novelty.reject.wizard',
            'target': 'new',
        }

    @api.model
    def add_follower_id(self, res_id, model, partner_id):
        follower_obj = self.env['mail.followers']
        subtype = self.env['mail.message.subtype'].search([
            ('name', '=', 'Discussions')], limit=1)
        exist_partner = follower_obj.search(
            [('res_id', '=', res_id),
             ('res_model', '=', model),
             ('partner_id', '=', partner_id)])
        if not exist_partner:
            follower_id = False
            reg = {
                'res_id': res_id,
                'res_model': model,
                'partner_id': partner_id
            }
            if subtype:
                reg.update({'subtype_ids': [(6, 0, [subtype.id])]})
            follower_id = self.env['mail.followers'].create(reg)
            return follower_id
        else:
            return False

    @api.model
    def create(self, vals):
        if vals.get('employee_id') and vals.get('start_date') and vals.get(
                'end_date') and self._context.get('check_duplicate'):
            novelty_count = self.search_count([
                ('start_date', '<=', vals.get('end_date')),
                ('end_date', '>=', vals.get('start_date')),
                ('employee_id', '=', vals.get('employee_id'))])
            if novelty_count > 0:
                return False
        if not self.env.context.get('transfer', False):
            vals['name'] = self.env['ir.sequence'].next_by_code("hr.novelty")

        res = super(HrNovelty, self).create(vals)  # Save the form
        stage_followers = self.env['hr.novelty.stage_followers'].search(
            [('stage', '=', vals['state'])]).mapped('partner_id')
        BP_users = self.env.ref(
            'base_product.group_bp').users.mapped('partner_id')
        stage_followers += BP_users

        for follower in stage_followers:
            self.add_follower_id(res.id, 'hr.novelty', follower.id)

        if vals.get('state') and not self._context.get('check_duplicate'):
            if vals.get('state') == 'approved':
                raise ValidationError(_(
                    'Las novedades no se pueden cargar en estado aprobado.'))
        if vals.get('event_id', ''):
            event = self.env['hr.novelty.event'].browse(
                vals.get('event_id', ''))
            seguidores_partner = []
            if event.grupo_de_seguidores_ids:
                for seguidores in event.grupo_de_seguidores_ids:
                    seguidores_partner.extend(
                        x for x in seguidores.users.mapped(
                            'partner_id').ids if x not in seguidores_partner)
            if seguidores_partner:
                for follower in seguidores_partner:
                    self.add_follower_id(res.id, 'hr.novelty', follower)
        # Message posting is optional. Add_follower_id will
        # still make the partner follow the record
        res.message_post(
            body=_("A new Novelty has been Created"),
            subtype='mail.mt_comment',
            message_type='email',
            partner_ids=res.message_follower_ids.mapped('partner_id.id'))
        '''
        if vals.get('event_id', ''):
            event = self.env['hr.novelty.event'].browse(
                vals.get('event_id', ''))
            users = []
            if event.group_ids:
                for group in event.group_ids:
                    users += group.users.ids
            if self.env.user.id not in users:
                raise ValidationError(_(
                    'This user has no access right to create Novelty.'))
        '''
        # restriction month create novelties
        '''
        date_start = vals.get('start_date', '')
        date_start = fields.Date.from_string(date_start)
        if date_start.month <= 11 and date_start.year == 2019 and
        date_start.month != 8 and
        res.event_id.name != 'Terminación de contrato/Renuncia Voluntaria':
            raise ValidationError(_(
                'Recuerde que el cierre de novedades se generó
                el 15 de noviembre, las novedades ingresadas apartir
                de esta fecha deben tener fecha del siguiente mes'))
        '''
        users = res.event_id.group_ids.mapped('users').ids
        if self.env.context.get('uid') and self.env.user.id not in users and\
                res.event_id:
            raise ValidationError(_(
                'This user has no access right to create Novelty.'))
        return res

    @api.multi
    def write(self, vals):
        """Must contain group for user in event."""
        '''
        if vals.get('event_id', ''):
            event = self.env['hr.novelty.event'].browse(
                vals.get('event_id', ''))
            users = []
            if event.group_ids:
                for group in event.group_ids:
                    users += group.users.ids
            if self.env.user.id not in users:
                raise ValidationError(_(
                    'This user has no access right to create Novelty.'))
        return super(HrNovelty, self).write(vals)
        '''
        if self.event_id:
            users = self.event_id.group_ids.mapped('users').ids
            if self.env.context.get('uid') and self.env.user.id not in\
                    users and not self._context.get('support_data'):
                raise ValidationError(_(
                    'This user has no access right to write Novelty.'))
        if self.state and vals.get('state', ''):
            self.message_post(
                body=_(self.state + " -> " + vals.get('state', '')),
                subtype='mail.mt_comment',
                message_type='email',
                partner_ids=self.message_follower_ids.mapped('partner_id.id'))
        return super(HrNovelty, self).write(vals)

    @api.depends('event_id')
    def compute_is_user_appr(self):
        for rec in self:
            rec.is_user_appr = rec.check_approver()

    def check_approver(self):
        for rec in self:
            if rec.event_id.approver:
                if rec.event_id.approver == 'daf' and self.env.user.has_group(
                        'base_product.group_daf'):
                    return True
                elif rec.event_id.approver == 'bp' and self.env.user.has_group(
                        'base_product.group_bp'):
                    return True
                elif rec.event_id.approver == 'sst' and\
                        self.env.user.has_group('base_product.group_sst'):
                    return True
                elif rec.event_id.approver == 'jd' and\
                        rec.employee_id.parent_id in\
                        self.env.user.employee_ids:
                    return True
            if rec.event_id.is_optional_approver and\
                    rec.event_id.optional_approver_group_id:
                event_group = self.event_id.optional_approver_group_id
                if event_group.id in self.env.user.groups_id.ids:
                    return True
            if rec.event_id.is_optional_approver_2 and\
                    rec.event_id.optional_approver2_group_id:
                event_group = self.event_id.optional_approver2_group_id
                if event_group.id in self.env.user.groups_id.ids:
                    return True
            else:
                return False

    @api.depends('event_id')
    def compute_is_sec_appr_user(self):
        for record in self:
            event_group = record.event_id.second_approver_group_id
            if event_group.id in record.env.user.groups_id.ids:
                record.is_sec_appr_user = True
            else:
                record.is_sec_appr_user = False

    @api.onchange('motivo_talento_id')
    def onchange_motivo_talento_id(self):
        otro_rec = self.env['motivo.talento'].search([
            ('name', '=', 'Otro')], limit=1)
        if otro_rec and self.motivo_talento_id and\
                self.motivo_talento_id.id == otro_rec.id:
            return {
                'warning': {
                    'title': "Message", 'message':
                    _("Por favor indique en el campo descripción cual "
                      "es el motivo.")},
            }

    @api.multi
    def novelty_create_subcontract(self):
        if self.contract_id and self.amount:
            contract_id = self.contract_id
            percentage = float((((
                contract_id.wage) + self.amount) * 100) / contract_id.wage)
            new_subcontract_id = contract_id.copy()
            new_subcontract_id.with_context(from_novelty=True).write({
                'subcontract': True, 'father_contract_id': contract_id.id,
                'wage': float(percentage * contract_id.wage) / 100,
                'fix_wage_amount': float(
                    percentage * contract_id.fix_wage_amount) / 100})
            new_subcontract_id.onchange_fix_wage_amount()
            self.contract_id = new_subcontract_id.id

    @api.onchange('is_eps')
    def onchange_is_eps(self):
        if self.is_eps and self.leave_id and not self.leave_id.is_eps:
            self.leave_id.write({'is_eps': True})
        if not self.is_eps and self.leave_id and self.leave_id.is_eps:
            self.leave_id.write({'is_eps': False})

    @api.onchange('is_arl')
    def onchange_is_arl(self):
        if self.is_arl and self.leave_id and not self.leave_id.is_arl:
            self.leave_id.write({'is_arl': True})
        if not self.is_arl and self.leave_id and self.leave_id.is_arl:
            self.leave_id.write({'is_arl': False})


class HrNoveltyEvent(models.Model):
    _name = 'hr.novelty.event'
    _description = 'HR Novelty Event'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, track_visibility='onchange')
    type_id = fields.Many2one('hr.novelty.type', string="Type",
                              track_visibility='onchange')
    subtype_id = fields.Many2one('hr.novelty.type.subtype', string="Sub-Type",
                                 track_visibility='onchange')
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type",
                                    help="Only if event is a leave",
                                    track_visibility='onchange')
    responsible_required = fields.Boolean(track_visibility='onchange')
    approver = fields.Selection([('daf', 'DAF'),
                                 ('bp', 'BP'),
                                 ('sst', 'SST'),
                                 ('jd', 'Jefe Directo'),
                                 ], track_visibility='onchange')
    second_approver_required = fields.Boolean(track_visibility='onchange')
    second_approver_group_id = fields.Many2one('res.groups',
                                               track_visibility='onchange')
    is_optional_approver = fields.Boolean(
        'Optional Approver', track_visibility='onchange')
    optional_approver_group_id = fields.Many2one(
        'res.groups',
        track_visibility='onchange')
    is_optional_approver_2 = fields.Boolean(
        'Optional Approver 2', track_visibility='onchange')
    optional_approver2_group_id = fields.Many2one(
        'res.groups',
        track_visibility='onchange')
    affectation = fields.Selection(
        [('allowance', 'Allowance'), ('deduction', 'Deduction')],
        track_visibility='onchange')
    restriction_day = fields.Date(
        track_visibility='onchange',
        help='Limit day of the month to create a "novedad" of this type')
    min_days = fields.Float(
        track_visibility='onchange',
        help='Minimun limit for the days in the "Novedad"')
    max_days = fields.Float(
        track_visibility='onchange',
        help='Maximun limit for the days in the "Novedad"')
    calendar_type = fields.Selection(
        [('employee', 'Employee'), ('full', 'Full Calendar')],
        help="This is the way the total days are calculated:"
             "Based on Employee's Calendar or Full Calendar",
        track_visibility='onchange')
    sara = fields.Char(track_visibility='onchange')
    description = fields.Text(track_visibility='onchange')
    company_only = fields.Boolean(track_visibility='onchange')
    attachment_required = fields.Boolean(track_visibility='onchange')
    group_ids = fields.Many2many('res.groups')
    grupo_de_seguidores_ids = fields.Many2many(
        'res.groups', 'res_groups_grupo_de_seguidores_default_rel',
        'res_groups_id', 'grupo_de_seguidores_id', string='Grupo de seguidores'
    )
    new_recruitment = fields.Boolean(track_visibility='onchange')
    is_recruitment = fields.Boolean(
        'Recruitment', track_visibility='onchange')
    is_aplica_fecha_final = fields.Boolean('Aplica Fecha Final')
    active = fields.Boolean(string='Active', default=True)
    is_requiere_adjunto = fields.Boolean('Requiere Adjunto')
    is_adjunto_obligatorio = fields.Boolean('Adjunto Obligatorio')
    is_motivo_de_retiro = fields.Boolean("Motivo de Retiro")
    is_h_e_procedimiento = fields.Boolean("H.E Procedimiento")
    is_horas_fijas = fields.Boolean("Horas Fijas")
    is_tipo_de_incapacidad = fields.Boolean("Tipo de Incapacidad")
    unjustified = fields.Boolean("Unjustified")
    transfer_employee = fields.Boolean(copy=False)
    requered_account = fields.Boolean('Requered Account')
    increase_salary = fields.Boolean()
    requered_attachment_lic = fields.Boolean()
    show_you = fields.Boolean()
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]",
        track_visibility='onchange'
    )
    limit_advance = fields.Float("Limit Advance")
    advance_holidays = fields.Boolean("Advance Holidays")
    projection_vacation = fields.Boolean("Projection Vacation")
    is_end_business_day = fields.Boolean("End Business Day")
    upc = fields.Boolean("UPC")

    @api.multi
    def get_total_days(self, start_date, end_date, employee):
        if self.calendar_type == 'employee':
            calendar = None  # Employee's default calendar
        else:
            calendar = self.env.ref('hr_novelty.resource_calendar_std_full')
        if employee:
            return employee.get_work_days_data(
                start_date, end_date, calendar=calendar)['days']
        else:
            return 30

    @api.onchange('type_id')
    def onchange_type(self):
        self.subtype_id = ''

    @api.onchange('subtype_id')
    def onchange_subtype(self):
        self.leave_type_id = ''
        self.responsible_required = ''




class HrNoveltyType(models.Model):
    _name = 'hr.novelty.type'
    _description = 'HR Novelty Type'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, track_visibility='onchange')
    description = fields.Text(track_visibility='onchange')


class HrNoveltySubType(models.Model):
    _name = 'hr.novelty.type.subtype'
    _description = 'HR Novelty Subtype'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, track_visibility='onchange')
    description = fields.Text(track_visibility='onchange')
    type_id = fields.Many2one('hr.novelty.type', string="Type",
                              track_visibility='onchange')


class StageFollowers(models.Model):
    _name = 'hr.novelty.stage_followers'
    _description = 'HR Novelty Stage Followers'

    def stages(self):
        return self.env['hr.novelty']._fields['state'].selection

    partner_id = fields.Many2one('res.partner', required=True, string='User')
    stage = fields.Selection(selection=stages, default='draft', string='Stage')

    @api.multi
    def name_get(self):
        result = []
        name = '%s in %s' % (self.partner_id.name, self.stage)
        result.append((self.id, name))
        return result
