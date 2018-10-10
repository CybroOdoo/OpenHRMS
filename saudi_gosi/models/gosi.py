from odoo import fields, api, models, _


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

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(Saudi, self).create(vals)

    @api.onchange('employee')
    def onchange_employee(self):
        department = self.env['hr.employee'].search([('name', '=', self.employee.name)])
        self.department = department.department_id.name
        self.position = department.job_id.name
        self.nationality = department.country_id.name
        self.type_gosi = department.type
        self.dob = department.birthday
        self.gos_numb = department.gosi_number
        self.issued_dat = department.issue_date


class Gosi(models.Model):

    _inherit = 'hr.employee'

    type = fields.Selection([('saudi','Saudi')],string='Type')
    gosi_number = fields.Char(string='GOSI Number')
    issue_date = fields.Date(string='Issued Date')
    age = fields.Char(string='AGE',required=True)
    limit = fields.Boolean(string='Eligible For GOSI',compute='compute_age',default=False)

    def compute_age(self):
        self.ensure_one()
        if int(self.age) <= 60 and int(self.age)>=18:
            self.limit = True
        else:
            self.limit = False



class Pay(models.Model):

    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip', string='GOSI Reference',readonly=True)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search([('employee', '=', rec.employee_id.name)])
            rec.gosi_no=gosi_no.id