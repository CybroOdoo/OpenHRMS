from odoo import fields, api, models, _


class Saudi(models.Model):
    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department = fields.Char(string="Department", required=True, help="Department")
    position = fields.Char(string='Job Position', required=True, help="Job Position")
    nationality = fields.Char(string='Nationality', required=True, help="Nationality")
    type_gosi = fields.Char(string='Type', required=True, track_visibility='onchange', help="Gosi Type")
    dob = fields.Char(string='Date Of Birth', required=True, help="Date Of Birth")
    gos_numb = fields.Char(string='GOSI Number', required=True, track_visibility='onchange', help="Gosi number")
    issued_dat = fields.Char(string='Issued Date', required=True, track_visibility='onchange', help="Issued date")
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(Saudi, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                department = rec.employee_id
                rec.department = department.department_id.name if department.department_id else False
                rec.position = department.job_id.name
                rec.nationality = department.country_id.name
                rec.type_gosi = department.type
                rec.dob = department.birthday
                rec.gos_numb = department.gosi_number
                rec.issued_dat = department.issue_date


class Gosi(models.Model):
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi')], string='Type', help="Select the type")
    gosi_number = fields.Char(string='GOSI Number', help="Gosi Number")
    issue_date = fields.Date(string='Issued Date', help="Issued Date")
    age = fields.Char(string='AGE', help="Age")
    limit = fields.Boolean(string='Eligible For GOSI', compute='_compute_age', default=False)

    def _compute_age(self):
        for res in self:
            if int(res.age) <= 60 and int(res.age) >= 18:
                res.limit = True
            else:
                res.limit = False


class Pay(models.Model):
    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip', string='GOSI Reference', readonly=True, help="Gosi Number")

    @api.onchange('employee_id')
    def onchange_employee_ref(self):
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search([('employee_id', '=', rec.employee_id.id)])
            rec.gosi_no = gosi_no.id
