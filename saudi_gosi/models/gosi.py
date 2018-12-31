from odoo import fields, api, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta


class Saudi(models.Model):

    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee = fields.Many2one('hr.employee', string="Employee", required=True)
    department = fields.Char(string="Department", required=True)
    position = fields.Char(string='Job Position', required=True)
    nationality = fields.Char(string='Nationality', required=True)
    type_gosi =fields.Char(string='Type',required=True,track_visibility='onchange')
    dob = fields.Char(string='Date Of Birth',required=True)
    gos_numb = fields.Char(string='GOSI Number',required=True,track_visibility='onchange')
    issued_dat =fields.Char(string='Issued Date',required=True,track_visibility='onchange')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    img_view = fields.Binary()
    employee_name = fields.Char()

    gosi_line = fields.One2many('gosi.payslip.line', 'connect_id1',string="NOne")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(Saudi, self).create(vals)

    @api.onchange('employee')
    def onchange_employee(self):
        for rec in self:
            if rec.employee:
                department = rec.employee
                rec.department = department.department_id.name if department.department_id else False
                rec.position = department.job_id.name
                rec.nationality = department.country_id.name
                rec.type_gosi = department.type
                rec.dob = department.birthday
                rec.gos_numb = department.gosi_number
                rec.issued_dat = department.issue_date
                rec.img_view = department.image
                rec.employee_name = department.name


class Gosi(models.Model):

    _inherit = 'hr.employee'

    type = fields.Selection([('saudi','Saudi')],string='Type')
    gosi_number = fields.Char(string='GOSI Number')
    issue_date = fields.Date(string='Issued Date')
    limit = fields.Boolean(string='Eligible For GOSI',compute='compute_age',default=False)
    age = fields.Integer(string="Age")

    @api.onchange('birthday')
    def _onchange_birth_date(self):

        if self.birthday:
            d1 = datetime.strptime(self.birthday, "%Y-%m-%d").date()

            d2 = date.today()

            self.age = relativedelta(d2, d1).years

    def compute_age(self):
        for re in self:
            if int(re.age) <= 60 and int(re.age)>=18:
                re.limit = True
            else:
                re.limit = False



class Pay(models.Model):

    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip', string='GOSI Reference',readonly=True)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search([('employee', '=', rec.employee_id.name)])
            rec.gosi_no=gosi_no.id


class Getter(models.Model):

    _inherit = 'hr.payslip'

    @api.multi
    def action_payslip_done(self):
        res = super(Getter, self).action_payslip_done()
        check = self.env['hr.payslip.line'].search([('slip_id','=',self.id)])
        change = self.env['gosi.payslip'].search([('employee','=',self.employee_id.id)])
        lines = []
        for i in check:
            if i.code == 'GOSI_COMP':
                vals = (0,0,{
                    'connect_id1': change.id,
                    'gosi_description': i.name,
                    'start_date':self.date_from,
                    'gosi_amount': i.amount,
                })
                lines.append(vals)
                change.update({'gosi_line': lines})
        return res


class GosiPayslipLine(models.Model):

    _name = 'gosi.payslip.line'

    gosi_description = fields.Char(string='Description', required=True)
    gosi_amount = fields.Char(string='Amount', required=True)
    start_date = fields.Char(string='Start Date')
    connect_id1 = fields.Many2one('gosi.payslip', required=True)
