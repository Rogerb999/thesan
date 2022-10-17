# -*- coding: utf-8 -*-

import pytz
from calendar import monthrange
from datetime import datetime, timedelta
from odoo import models, fields, api

tipo_trabajador = [
    ('01', 'Dependiente'),
    ('02', 'Servicio domestico'),
    ('04', 'Madre comunitaria'),
    ('12', 'Aprendices del Sena en etapa lectiva'),
    ('18', 'Funcionarios públicos sin tope máximo de ibc'),
    ('19', 'Aprendices del SENA en etapa productiva'),
    ('20', 'Estudiantes (régimen especial ley 789 de 2002)'),
    ('21', 'Estudiantes de postgrado en salud'),
    ('22', 'Profesor de establecimiento particular'),
    ('23', 'Estudiantes aportes solo riesgos laborales'),
    ('30', 'Dependiente entidades o universidades públicas con régimen especial en salud'),
    ('31', 'Cooperados o pre cooperativas de trabajo asociado'),
    ('47', 'Trabajador dependiente de entidad beneficiaria del sistema general de participaciones - aportes patronales'),
    ('51', 'Trabajador de tiempo parcial'),
    ('54', 'Pre pensionado de entidad en liquidación'),
    ('55', 'Afiliado participe - dependiente'),
    ('56', 'Pre pensionado con aporte voluntario a salud'),
    ('57', 'Independiente voluntario al sistema de riesgos laborales'),
    ('58', 'Estudiantes de prácticas laborales en el sector público'),
]

sub_tipo_trabajador = [
    ('00', 'No Aplica'),
    ('01', 'Dependiente pensionado por vejez activo'),
]

medio_pago = [
    ('1', 'Instrumento no definido'),
    ('2', 'Crédito ACH'),
    ('3', 'Débito ACH'),
    ('4', 'Reversión débito de demanda ACH'),
    ('5', 'Reversión crédito de demanda ACH'),
    ('6', 'Crédito de demanda ACH'),
    ('7', 'Débito de demanda ACH'),
    ('8', 'Mantener'),
    ('9', 'Clearing Nacional o Regional'),
    ('10', 'Efectivo'),
    ('11', 'Reversión Crédito Ahorro'),
    ('12', 'Reversión Débito Ahorro'),
    ('13', 'Crédito Ahorro'),
    ('14', 'Débito Ahorro'),
    ('15', 'Bookentry Crédito'),
    ('16', 'Bookentry Débito'),
    ('17', 'Concentración de la demanda en efectivo /Desembolso Crédito (CCD)'),
    ('18', 'Concentración de la demanda en efectivo / Desembolso (CCD) débito'),
    ('19', 'Crédito Pago negocio corporativo (CTP)'),
    ('20', 'Cheque'),
    ('21', 'Proyecto bancario'),
    ('22', 'Proyecto bancario certificado'),
    ('23', 'Cheque bancario'),
    ('24', 'Nota cambiaria esperando aceptación'),
    ('25', 'Cheque certificado'),
    ('26', 'Cheque Local'),
    ('27', 'Débito Pago Negocio Corporativo (CTP)'),
    ('28', 'Crédito Negocio Intercambio Corporativo (CTX)'),
    ('29', 'Débito Negocio Intercambio Corporativo (CTX)'),
    ('30', 'Transferencia Crédito'),
    ('31', 'Transferencia Débito'),
    ('32', 'Concentración Efectivo / Desembolso Crédito plus (CCD+)'),
    ('33', 'Concentración Efectivo / Desembolso Débito plus (CCD+)'),
    ('34', 'Pago y depósito pre acordado (PPD)'),
    ('35', 'Concentración efectivo ahorros / Desembolso Crédito (CCD)'),
    ('36', 'Concentración efectivo ahorros / Desembolso Crédito (CCD)'),
    ('37', 'Pago Negocio Corporativo Ahorros Crédito (CTP)'),
    ('38', 'Pago Negocio Corporativo Ahorros Débito (CTP)'),
    ('39', 'Crédito Negocio Intercambio Corporativo (CTX)'),
    ('40', 'Débito Negocio Intercambio Corporativo (CTX)'),
    ('41', 'Concentración efectivo/Desembolso Crédito plus (CCD+)'),
    ('42', 'Consignación bancaria'),
    ('43', 'Concentración efectivo / Desembolso Débito plus (CCD+)'),
    ('44', 'Nota cambiaria'),
    ('45', 'Transferencia Crédito Bancario'),
    ('46', 'Transferencia Débito Interbancario'),
    ('47', 'Transferencia Débito Bancaria'),
    ('48', 'Tarjeta Crédito'),
    ('49', 'Tarjeta Débito'),
    ('50', 'Postgiro'),
    ('51', 'Telex estándar bancario francés'),
    ('52', 'Pago comercial urgente'),
    ('53', 'Pago Tesorería Urgente'),
    ('60', 'Nota promisoria'),
    ('61', 'Nota promisoria firmada por el acreedor'),
    ('62', 'Nota promisoria firmada por el acreedor, avalada por el banco'),
    ('63', 'Nota promisoria firmada por el acreedor, avalada por un tercero'),
    ('64', 'Nota promisoria firmada por el banco'),
    ('65', 'Nota promisoria firmada por un banco avalada por otro banco'),
    ('66', 'Nota promisoria firmada'),
    ('67', 'Nota promisoria firmada por un tercero avalada por un banco'),
    ('70', 'Retiro de nota por el por el acreedor'),
    ('71', 'Bonos'),
    ('72', 'Vales'),
    ('74', 'Retiro de nota por el por el acreedor sobre un banco'),
    ('75', 'Retiro de nota por el acreedor, avalada por otro banco'),
    ('76', 'Retiro de nota por el acreedor, sobre un banco avalada por un tercero'),
    ('77', 'Retiro de una nota por el acreedor sobre un tercero'),
    ('78', 'Retiro de una nota por el acreedor sobre un tercero avalada por un banco'),
    ('91', 'Nota bancaria transferible'),
    ('92', 'Cheque local trasferible'),
    ('93', 'Giro referenciado'),
    ('94', 'Giro urgente'),
    ('95', 'Giro formato abierto'),
    ('96', 'Método de pago solicitado no usado'),
    ('97', 'Clearing entre partners'),
    ('98', 'Cuentas de ahorro de tramite simplificado (CATS) (Nequi, Daviplata, etc)'),
    ('zzz', 'Acuerdo mutuo'),
]

class HrContract(models.Model):
    _inherit = 'hr.contract'

    porcentaje_comision = fields.Float(string='% Comisión')
    lunch_hours = fields.Float(string='Horas de comida', default=1)
    minute_delay_allowed = fields.Integer(string='Minutos de retraso permitidos', default=0)
    schedule_pay = fields.Selection(selection_add=[('day', 'Diario')])
    # fecha_pago_cesantias = fields.Date(string='Fecha pago cesantias', required=True)
    tipo_trabajador_ti = fields.Selection(tipo_trabajador, string='Tipo de trabajador', index=True, default=tipo_trabajador[0][0])
    cuenta_debito = fields.Integer(string='Debito', default=0)
    cuenta_credito = fields.Integer(string='Credito', default=0)
    sub_tipo_trabajador_ti = fields.Selection(sub_tipo_trabajador, string='Subtipo de trabajador', index=True, default=sub_tipo_trabajador[0][0])
    medio_de_pagos = fields.Selection(medio_pago, string='Medio de pago', index=True, default=medio_pago[0][0])
    # Prestaciones Sociales
    cesantias = fields.Float(string='Cesantias')
    interes_sobre_cesantias = fields.Float(string='Interes S/Cesantias')
    prima_no1 = fields.Float(string='Prima 1')
    prima_no2 = fields.Float(string='Prima 2')
    vacaciones = fields.Float(string='Vacaciones')
    # Adicionales salario
    salario_integral = fields.Boolean(string='Integral', default=False)
    pagar_auxilio_transporte = fields.Boolean(string='Pagar Aux. Transp.', compute='_compute_pagar_auxilio_transporte')
    actividad_alto_riesgo = fields.Boolean(string='Activ. Alto Riesgo', default=False)
    # XML
    contract_type = fields.Selection([
        ('1', 'Término fijo'),
        ('2', 'Término Indefinido'),
        ('3', 'Obra o Labor'),
        ('4', 'Aprendizaje'),
        ('5', 'Prácticas o Pasantías'),
    ], string='Tipo de Contrato')
    # Pagar Horas extras
    allow_extra_hours = fields.Boolean(string='Permitir horas extras', default=False)
    pay_dominical = fields.Boolean(string='Pagar dominical', default=False, help="Si no se habilita, no se pagarían dominical, se compensaria por un día de descanso")
    # Override field
    schedule_pay = fields.Selection([
        ('weekly', 'Semanal'),
        ('decenal', 'Decenal'),
        ('catorcenal', 'Catorcenal'),
        ('bi-weekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('days', 'Dias'),
    ])
    contract_schedule_pay = fields.Selection([
        ('weekly', 'Semanal'),
        ('decenal', 'Decenal'),
        ('catorcenal', 'Catorcenal'),
        ('bi-weekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('days', 'Dias'),
    ], string='Pago Planificado Según Contrato')
    
    @api.depends('wage')
    def _compute_pagar_auxilio_transporte(self):
        if self.wage <= float(self.env['ir.config_parameter'].get_param('hr_payroll_colombia.salario_minimo')) * 2:
            self.pagar_auxilio_transporte = True
        else:
            self.pagar_auxilio_transporte = False

    def _convert_utc_date_to_usertz(self, fecha_utc):
        user_tz = self.env.user.tz
        fmt = '%Y-%m-%d %H:%M:%S'
        local = pytz.timezone(user_tz)
        return str(datetime.strftime(pytz.utc.localize(datetime.strptime(fecha_utc, fmt)).astimezone(local), fmt))

    def convert_TZ_UTC(self, TZ_datetime):
        # Metodo que permite convertir la fecha y hora retornada por el SAT a la fecha y hora correcta para guardar en la base de datos y que coincida con la real
        fmt = "%Y-%m-%d %H:%M:%S"
        # Current time in UTC
        now_utc = datetime.now(pytz.timezone('UTC'))
        # Convert to current user time zone
        now_timezone = now_utc.astimezone(pytz.timezone(self.env.user.tz))
        UTC_OFFSET_TIMEDELTA = datetime.strptime(now_utc.strftime(fmt), fmt) - datetime.strptime(now_timezone.strftime(fmt), fmt)
        local_datetime = datetime.strptime(TZ_datetime, fmt)
        result_utc_datetime = local_datetime + UTC_OFFSET_TIMEDELTA
        return result_utc_datetime.strftime(fmt)
    

    def get_comision(self, payslip):
        sales = self.env['account.invoice'].search([('user_id', '=', payslip.contract_id.employee_id.user_id.id), ('date_invoice', '>=', payslip.date_from), ('date_invoice', '<=', payslip.date_to)])
        if not sales:
            return 0

        total_sales = 0
        for sale in sales:
            total_sales += sale.amount_total
        return total_sales * (payslip.contract_id.porcentaje_comision / 100)
    
    def get_minutos_trabajados(self, contract, payslip):
        manual_payroll = self.env['ir.config_parameter'].get_param('hr_payroll_colombia.manual_payroll')
        if not manual_payroll:
            fecha_inicial = payslip.date_from
            fecha_final = payslip.date_to

            fecha_control = fecha_inicial
            dias_fin_de_semana = 0

            for count in range(1, (fecha_final - fecha_inicial).days + 2):
                dayweek_control = datetime.weekday(fecha_control)
                
                if (dayweek_control == 5 or dayweek_control == 6) and not contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == dayweek_control):
                    dias_fin_de_semana += 1
                fecha_control += timedelta(days=1)
            
            #Determinar forma de pago:
            # Si es mensual, considerar cuantos días tiene el mes, si tiene menos de 30, sumas para completarlos, si tiene 31 restar uno
            month_days = monthrange(fecha_inicial.year, fecha_inicial.month)[1]
            if contract.schedule_pay == 'monthly':
                if month_days == 31:
                    dias_fin_de_semana -= 1
                elif month_days == 28:
                    dias_fin_de_semana += 2
                elif month_days == 29:
                    dias_fin_de_semana += 1
            elif contract.schedule_pay == 'bi-weekly':
                if fecha_inicial.day == 16:
                    if month_days == 31:
                        dias_fin_de_semana -= 1
                    elif month_days == 28:
                        dias_fin_de_semana += 2
                    elif month_days == 29:
                        dias_fin_de_semana += 1
            
            minute_pay =  contract.wage / 30 / 480

            # Consultamos todos los registros de asistencia del empleado
            attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id), 
                ('check_in', '>=', payslip.date_from), ('check_out', '<=', payslip.date_to)])
            
            # Consultar los minutos permitidos para llegar después de la hora de entrada
            minute_delay = contract.minute_delay_allowed
            # total_minutes = 0
            
            total_diurno = 0
            total_nocturno = 0
            totol_minutos_pagados = 0
            for attendance_id in attendance_ids:
                # Consultar el día de la semana de la asistencia en base a la hora de entrada
                attendance_day = datetime.weekday(attendance_id.check_in)

                # Consultar el horario de entrada del dia correspondiente a la asistencia
                calendar_day = contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == attendance_day)
                
                if not calendar_day:
                    continue
                
                # Sumar los minutos permitidos de tolerancia a la hora de entrada
                entrada = str(attendance_id.check_in).split(" ")[0] + ' ' + str(timedelta(hours=calendar_day.hour_from))
                salida = str(attendance_id.check_out).split(' ')[0] + ' ' + str(timedelta(hours=calendar_day.hour_to))
                tiempo_comida = timedelta(hours=contract.lunch_hours)

                minutos_tolerancia = timedelta(minutes=contract.minute_delay_allowed)
                hour_from_with_delay = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S') + minutos_tolerancia

                # Determinar la entrada
                check_in_system = self._convert_utc_date_to_usertz(str(attendance_id.check_in))
                check_in_system = datetime.strptime(check_in_system, '%Y-%m-%d %H:%M:%S')
                if check_in_system <= hour_from_with_delay:
                    check_in = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
                else:
                    check_in = check_in_system
                
                # Determinar la salida
                check_out_system = self._convert_utc_date_to_usertz(str(attendance_id.check_out))
                check_out_system = datetime.strptime(check_out_system, '%Y-%m-%d %H:%M:%S')
                if check_out_system <= datetime.strptime(salida, '%Y-%m-%d %H:%M:%S'):
                    check_out = check_out_system
                else:
                    check_out = datetime.strptime(salida, '%Y-%m-%d %H:%M:%S')
                
                tiempo_trabajado = check_out - check_in - tiempo_comida
                tiempo_trabajado_minutos = round(tiempo_trabajado.seconds / 60)
                if calendar_day.day_period == 'morning':
                    total_diurno += round(tiempo_trabajado_minutos, 0) * minute_pay
                else:
                    total_nocturno += round(tiempo_trabajado_minutos, 0) * (minute_pay * 1.35)
                totol_minutos_pagados += tiempo_trabajado_minutos
            
            fin_semana = dias_fin_de_semana * 480 * minute_pay
            return round(total_nocturno + total_diurno + fin_semana)
        else:
            day_pay =  contract.wage / 30
            total_days = (payslip.date_to - payslip.date_from).days + 1
            if contract.schedule_pay == 'monthly':
                total_days = 30
            elif contract.schedule_pay == 'bi-weekly':
                total_days = 15
            elif contract.schedule_pay == 'weekly':
                total_days = 6
                if contract.pay_dominical:
                    total_days += 1
            elif contract.schedule_pay == 'decenal':
                total_days = 10
            elif contract.schedule_pay == 'catorcenal':
                total_days = 14
            
            return total_days * day_pay
            

    def get_tipo_horas_extra(self, contract, payslip, type):
        # TODO: Agregar campo en contrato para permitir el pago o contabilización de horas extras
        # TODO: Agregar campo en contrato para permitir pago de hora adicional por petición del jefe.
        # TODO: Considerar horas adicionales si entra más temprano pero solo por petición del jefe.
        fecha_inicial = payslip.date_from
        fecha_final = payslip.date_to

        # Consultamos todos los registros de asistencia del empleado
        attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id), 
            ('check_in', '>=', payslip.date_from), ('check_out', '<=', payslip.date_to)])
        
        # Consultar los minutos permitidos para llegar después de la hora de entrada
        # minute_delay = contract.minute_delay_allowed
        # total_minutes = 0
        
        total_diurno = 0
        total_nocturno = 0
        totol_minutos_pagados = 0
        for attendance_id in attendance_ids:
            # Consultar el día de la semana de la asistencia en base a la hora de entrada
            attendance_day = datetime.weekday(attendance_id.check_in)

            # Consultar el horario de entrada del dia correspondiente a la asistencia
            calendar_day = contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == attendance_day)
            
            if not calendar_day:
                continue

            entrada = str(attendance_id.check_in).split(" ")[0] + ' ' + str(timedelta(hours=calendar_day.hour_from))
            salida = str(attendance_id.check_out).split(' ')[0] + ' ' + str(timedelta(hours=calendar_day.hour_to))

            # Determinar la entrada
            check_in_system = self._convert_utc_date_to_usertz(str(attendance_id.check_in))
            check_in_system = datetime.strptime(check_in_system, '%Y-%m-%d %H:%M:%S')
            if check_in_system <= hour_from_with_delay:
                check_in = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
            else:
                check_in = check_in_system
            
            # Determinar la salida
            check_out_system = self._convert_utc_date_to_usertz(str(attendance_id.check_out))
            check_out_system = datetime.strptime(check_out_system, '%Y-%m-%d %H:%M:%S')
            if check_out_system <= datetime.strptime(salida, '%Y-%m-%d %H:%M:%S'):
                check_out = check_out_system
            else:
                check_out = datetime.strptime(salida, '%Y-%m-%d %H:%M:%S')
            
            tiempo_trabajado = check_out - check_in - tiempo_comida
            tiempo_trabajado_minutos = round(tiempo_trabajado.seconds / 60)
            if calendar_day.day_period == 'morning':
                total_diurno += round(tiempo_trabajado_minutos, 0) * minute_pay
            else:
                total_nocturno += round(tiempo_trabajado_minutos, 0) * (minute_pay * 1.35)
            totol_minutos_pagados += tiempo_trabajado_minutos
        
        fin_semana = dias_fin_de_semana * 480 * minute_pay
        return round(total_nocturno + total_diurno + fin_semana)
    
    def get_seconds(self, contract, week_day, date_from, date_to):
        calendar_day = contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == week_day)
        calendar_hour_in = str(date_from).split(' ')[0] + ' ' + str(timedelta(hours=calendar_day.hour_from))
        calendar_hour_out = str(date_to).split(' ')[0] + ' ' + str(timedelta(hours=calendar_day.hour_to))
        lunch_time = timedelta(hours=contract.lunch_hours)
        return datetime.strptime(calendar_hour_out, '%Y-%m-%d %H:%M:%S') - datetime.strptime(calendar_hour_in, '%Y-%m-%d %H:%M:%S') - lunch_time
    
    def ausencia_no_remunerada_minutos(self, contract, ausencias):
        discount = 0

        for item in ausencias:
            if item.holiday_status_id.unpaid == True:

                # Ausencia por medio dia
                if item.request_unit_half == True:
                    week_day = datetime.weekday(item.request_date_from)
                    seconds = self.get_seconds(contract, week_day, item.request_date_from, item.request_date_to)
                    discount += ((seconds.seconds / 60) / 2) * (contract.wage / 14400)

                # Ausencia por dias
                elif item.holiday_status_id.request_unit == 'day':
                    # Consultar por los dias de ausencia las horas de trabajo por cada dia
                    current_day = item.request_date_from
                    for dia in range(1, int(item.number_of_days_display) + 1, 1):
                        week_day = datetime.weekday(current_day)
                        seconds = self.get_seconds(contract, week_day, item.request_date_from, item.request_date_to)
                        discount += (seconds.seconds / 60) * (contract.wage / 14400)
                        current_day = current_day + timedelta(days=1)
                
                # Ausencia por horas
                elif item.holiday_status_id.request_unit_hours == True:
                    return True
        return discount
    
    def get_arl(self, contract, payslip, employee):
        # Consultar ausencias que iniciean antes o al inicio de fecha de nomina
        ausencias = payslip.env['hr.leave'].search([
            ('request_date_from', '<=', payslip.date_from), 
            ('request_date_to', '>=', payslip.date_from), 
            ('employee_id', '=', employee.id), 
            ('state', '=', 'validate')])
        
        # Ausencias donde sus fechas están dentro o igual del periodo de nomina
        ausencias += payslip.env['hr.leave'].search([
            ('request_date_from', '>=', payslip.date_from),
            ('request_date_to', '<=', payslip.date_to),
            ('employee_id', '=', employee.id), 
            ('state', '=', 'validate')])
        
        # Ausencias que inician al final o igual de fecha final de nomina, y terminan en la siguiente nomina
        ausencias += payslip.env['hr.leave'].search([
            ('request_date_from', '<=', payslip.date_to),
            ('request_date_to', '>=', payslip.date_to),
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate')])

        if ausencias:
            dias = 0
            for ausencia in ausencias:
                if ausencia.holiday_status_id.leave_type == 'incapacidad_arl':
                    # Si la ausencia inicia antess del inicio de nomina y termina antes de de la fecha final
                    if ausencia.request_date_from <= payslip.date_from and ausencia.request_date_to <= payslip.date_to:            
                        dias += (ausencia.request_date_to - payslip.date_from).days + 1
                    # Si la ausencia esta dentro del periodo de la nomina
                    elif ausencia.request_date_from >= payslip.date_from and ausencia.request_date_to <= payslip.date_to:
                        dias += (ausencia.request_date_to - ausencia.request_date_from).days + 1
                    # Si inicio de la ausencia esta dentro del periodo de nomina y el final despues
                    elif ausencia.request_date_from >= payslip.date_from and ausencia.request_date_to >= payslip.date_to:
                        dias += (payslip.date_to - ausencia.request_date_from).days + 1
                    # Si la ausencia inicia antes o termina despues del periodo de la nomina
                    elif ausencia.request_date_from <= payslip.date_from and ausencia.request_date_to >= payslip.date_to:
                        dias += (payslip.date_to - payslip.date_from).days + 1

            pago_x_dia = contract.wage / 30

            return round(pago_x_dia * dias, 0)
        else:
            return 0
    
    def calcular_incapacidad_comun(self, payslip, contract, employee):
        # result = payslip.env['hr.contract'].dias_ausencia_eps(payslip)
        # Consultar ausencias que iniciean antes o al inicio de fecha de nomina
        ausencias_ids = payslip.env['hr.leave'].search([
            ('request_date_from', '<=', payslip.date_from), 
            ('request_date_to', '>=', payslip.date_from), 
            ('employee_id', '=', employee.id), 
            ('state', '=', 'validate')])
        
        # Ausencias donde sus fechas están dentro o igual del periodo de nomina
        ausencias_ids2 = payslip.env['hr.leave'].search([
            ('request_date_from', '>=', payslip.date_from),
            ('request_date_to', '<=', payslip.date_to),
            ('employee_id', '=', employee.id), 
            ('state', '=', 'validate')])
        
        # Ausencias que inician al final o igual de fecha final de nomina, y terminan en la siguiente nomina
        ausencias_ids3 = payslip.env['hr.leave'].search([
            ('request_date_from', '<=', payslip.date_to),
            ('request_date_to', '>=', payslip.date_to),
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate')])
        
        if ausencias_ids2:
            if ausencias_ids:
                ausencias_ids += ausencias_ids2
            else:
                ausencias_ids = ausencias_ids2
        if ausencias_ids3:
            if ausencias_ids:
                ausencias_ids += ausencias_ids3
            else:
                ausencias_ids = ausencias_ids3
 
        # Ausencias solo por enfermedad
        ausencias = ausencias_ids.filtered(lambda x: x.holiday_status_id.leave_type == 'incapacidad_eps')
        total = 0

        if ausencias:
            dias_ausencias = 0
            for ausencia in ausencias:
                # Ausencia de toda la fecha de nomina, e iniciando en una y cruzandose a otra nomina
                if ausencia.request_date_from >= payslip.date_from and ausencia.request_date_to >= payslip.date_to:
                    dias_ausencias += (payslip.date_to - ausencia.request_date_from + timedelta(days=1)).days
                    no_dia_ausencia = 1
                # Ausencia antes o al inicio de fecha de la nomina y, mayor o igual a fecha final de nomina
                elif ausencia.request_date_from <= payslip.date_from and ausencia.request_date_to >= payslip.date_to:
                    dias_ausencias += (payslip.date_to - payslip.date_from + timedelta(days=1)).days
                    no_dia_ausencia = ((ausencia.request_date_to - ausencia.request_date_from) - (payslip.date_to - payslip.date_from)).days
                # Ausencia entre o igual a fechas de nomina
                elif ausencia.request_date_from >= payslip.date_from and ausencia.request_date_to <= payslip.date_to:
                    dias_ausencias += (ausencia.request_date_to - ausencia.request_date_from + timedelta(days=1)).days
                    no_dia_ausencia = (ausencia.request_date_to - ausencia.request_date_from + timedelta(days=1)).days
                # Ausencia en la nomina anterior y en la nomina actual
                elif ausencia.request_date_from <= payslip.date_from and ausencia.request_date_to <= payslip.date_to:
                    dias_ausencias += (ausencia.request_date_to - payslip.date_from + timedelta(days=1)).days
                    no_dia_ausencia = ((ausencia.request_date_to - ausencia.request_date_from) - (ausencia.request_date_to - payslip.date_from) + timedelta(days=1)).days

            valor_x_dia_sm = self.env['hr.salary.rule'].search([('code', '=', 'SMLV_Parametro')])[0].amount_fix / 30
            pago_x_dia = (contract.wage / 30) * 0.6667

            if pago_x_dia < valor_x_dia_sm:
                pago_x_dia = valor_x_dia_sm

            # Saber que dia se le esta pagando
            if no_dia_ausencia <= 90:
                total = pago_x_dia * dias_ausencias
            elif no_dia_ausencia > 90 and no_dia_ausencia <= 180:
                total = pago_x_dia * dias_ausencias * 0.5


            #porcentaje90 = 1 if (pago_x_dia * 0.6667) <= (SMLV_Parametro / 30) else 0.6667
            #porcentaje91 = 1 if (pago_x_dia * 0.5) <= (SMLV_Parametro / 30) else 0.5

            # Pago de 1 a 90 dias
            #dias_pagar = 0
            #if no_dia_ausencia <= 90:
            #    dias_pagar = dias
            #else:
            #    dias_pagar = 90

            #subtotal = (dias_pagar * pago_x_dia * porcentaje90)

            # Pago del dia 91 al 180
            #dias_pagar = 0
            #if dias > 90 and dias <= 180:
            #    if dias <= 180:
            #        dias_pagar = dias - 90
            #    else:
            #        dias_pagar = 90

            #subtotal += dias_pagar * pago_x_dia * porcentaje91

        return total
    
    def dias_ausencia_eps(self, payslip):
        # Buscar que el primer día de la ausencia estre dentro de la fecha de pago de nomina
        ausencias = self.env['hr.leave'].search([
            ('date_from', '>=', payslip.date_from), 
            ('date_from', '<=', payslip.date_to),
            ('employee_id', '=', payslip.employee_id)]) #, ('state', '=', 'validate')])
        
        # Buscar ausencias antes y despues de fechas de nomina
        ausencias2 = self.env['hr.leave'].search([
            ('date_from', '<=', payslip.date_from), 
            ('date_to', '>=', payslip.date_to),
            ('employee_id', '=', payslip.employee_id)])
        for a2 in ausencias2:
            if a2 not in ausencias:
                ausencias += a2
        
        ausencias3 = self.env['hr.leave'].search([
            ('date_to', '>=', payslip.date_from), 
            ('date_to', '<=', payslip.date_to),
            ('employee_id', '=', payslip.employee_id)])
        for a3 in ausencias3:
            if a3 not in ausencias:
                ausencias += a3
        
        # Ausencias solo por enfermedad
        ausencias = ausencias.filtered(lambda x: x.holiday_status_id.leave_type == 'incapacidad_eps')

        # Establecer los días de ausencia
        dias_ausencias = 0
        for ausencia in ausencias:
            # Ausencia de toda la fecha de nomina, e iniciando en uno y cruzandose a otro nomina
            if ausencia.date_from.date() >= payslip.date_from and ausencia.date_to.date() >= payslip.date_to:
                dias_ausencias += (payslip.date_to - ausencia.date_from.date() + timedelta(days=1)).days
            # Ausencia antes o al inicio de fecha de la nomina y, mayor o igual a fecha final de nomina
            elif ausencia.date_from.date() <= payslip.date_from and ausencia.date_to.date() >= payslip.date_to:
                dias_ausencias += (payslip.date_to - payslip.date_from + timedelta(days=1)).days
            # Ausencia entre o igual a fechas de nomina
            elif ausencia.date_from.date() >= payslip.date_from and ausencia.date_to.date() <= payslip.date_to:
                dias_ausencias += (ausencia.date_to.date() - ausencia.date_from.date() + timedelta(days=1)).days
            # Ausencia en la nomina anterior y en la nomina actual
            elif ausencia.date_from.date() <= payslip.date_from and ausencia.date_to.date() <= payslip.date_to:
                dias_ausencias += (ausencia.date_to.date() - payslip.date_from + timedelta(days=1)).days
        return dias_ausencias
    
    def get_worked_days(self, payslip, contract):
        manual_payroll = self.env['ir.config_parameter'].get_param('hr_payroll_colombia.manual_payroll')
        if not manual_payroll:
            fecha_inicial = payslip.date_from
            fecha_final = payslip.date_to

            fecha_control = fecha_inicial
            dias_fin_de_semana = 0

            for count in range(1, (fecha_final - fecha_inicial).days + 2):
                dayweek_control = datetime.weekday(fecha_control)
                
                if (dayweek_control == 5 or dayweek_control == 6) and not contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == dayweek_control):
                    dias_fin_de_semana += 1
                fecha_control += timedelta(days=1)
            
            #Determinar forma de pago:
            # Si es mensual, considerar cuantos días tiene el mes, si tiene menos de 30, sumas para completarlos, si tiene 31 restar uno
            month_days = monthrange(fecha_inicial.year, fecha_inicial.month)[1]
            if contract.schedule_pay == 'monthly':
                if month_days == 31:
                    dias_fin_de_semana -= 1
                elif month_days == 28:
                    dias_fin_de_semana += 2
                elif month_days == 29:
                    dias_fin_de_semana += 1
            elif contract.schedule_pay == 'bi-weekly':
                if fecha_inicial.day == 16:
                    if month_days == 31:
                        dias_fin_de_semana -= 1
                    elif month_days == 28:
                        dias_fin_de_semana += 2
                    elif month_days == 29:
                        dias_fin_de_semana += 1

            # Consultamos todos los registros de asistencia del empleado
            attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id), 
                ('check_in', '>=', payslip.date_from), ('check_out', '<=', payslip.date_to)])
            
            dias_trabajados = 0
            for attendance_id in attendance_ids:
                # Consultar el día de la semana de la asistencia en base a la hora de entrada
                attendance_day = datetime.weekday(attendance_id.check_in)

                # Consultar el horario de entrada del dia correspondiente a la asistencia
                calendar_day = contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == attendance_day)
                
                if not calendar_day:
                    continue
                dias_trabajados += 1
                
            return dias_trabajados + dias_fin_de_semana
        
        else:
            # day_pay =  contract.wage / 30
            total_days = (payslip.date_to - payslip.date_from).days + 1
            month_days = monthrange(payslip.date_to.year, payslip.date_to.month)[1]
            
            if total_days > 30:
                total_days = 30
            if total_days == 16:
                total_days = 15
            
            """if contract.schedule_pay == 'monthly':
                total_days = 30
            elif contract.schedule_pay == 'bi-weekly':
                total_days = 15
            elif contract.schedule_pay == 'weekly':
                total_days = 6
                if contract.pay_dominical:
                    total_days += 1
            elif contract.schedule_pay == 'decenal':
                total_days = 10
            elif contract.schedule_pay == 'catorcenal':
                total_days = 14"""
            
            return total_days
    
    def calcular_cesantia(self, contract):
        return 10
