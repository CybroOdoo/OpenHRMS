# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeVerification(models.Model):
    _name = 'employee.verification'
    _rec_name = 'verification_id'

    verification_id = fields.Char('ID', readonly=True, copy=False)
    employee = fields.Many2one('hr.employee', string='Employee', required=True, help='You can choose the employee for background verification')
    address = fields.Many2one(related='employee.address_home_id', string='Address')
    assigned_by = fields.Many2one('res.users', string='Assigned By', readonly=1, default=lambda self: self.env.uid)
    agency = fields.Many2one('res.users', string='Agency', domain=[['groups_id', 'ilike', 'agent']], help='You can choose a Verification Agent')
    resume_applicant = fields.Binary(compute='get_attachment', string='Resume of Applicant', readonly=True)
    required_details = fields.Binary(compute='get_details', string='Required Details')
    upload_result = fields.Many2many('ir.attachment', string='Collected Details', required=True, help='You can upload the Collected details')
    field_check = fields.Boolean(string='Check', invisible=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assigned'),
        ('ready', 'Upload Details'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
    ], string='Status', default='draft')

    # state changes and functions
    @api.multi
    def submit_statusbar(self):
        self.write({
            'state': 'submit',
        })

    @api.multi
    def approve_statusbar(self):
        self.write({
            'state': 'approve',
        })

    @api.multi
    def refused_statusbar(self):
        self.write({
            'state': 'refuse',
        })

    @api.multi
    def assign_statusbar(self):
        self.state = 'assign'
        template = self.env.ref('employee_background.assign_agency_email_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    @api.multi
    def upload_statusbar(self):
        self.write({
            'state': 'ready',
        })

    @api.multi
    def create_invoice_agency(self):
        self.write({
            'state': 'submit',
        })
        formview_ref = self.env.ref('hr_expense.hr_expense_form_view', False)
        return {
            'name': "Expense for Verification",
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "",
            'views': [
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {
            }
        }

    # sequence generation for employee verification
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('res.users') or '/'
        vals['verification_id'] = seq
        return super(EmployeeVerification, self).create(vals)

    # for getting the applicant's attachment
    def get_attachment(self):
        temp = self.env['hr.applicant'].search([('emp_id', '=', self.employee.id)])
        tempo = self.env['ir.attachment'].search([('res_id', '=', temp.id)], limit=1)
        self.resume_applicant = tempo.datas

    @api.multi
    def send_mail(self):
        self.field_check = True
        template = self.env.ref('employee_background.approved_email_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    @api.multi
    def reject_mail(self):
        self.field_check = True
        template = self.env.ref('employee_background.refused_email_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def get_details(self):
        data = {'vid': self.verification_id,
                'applicant': self.employee.name,
                }
        return self.env.ref('employee_background.employee_verification_defaultxlsx'). \
            with_context(landscape=False).report_action(self, data=data)

    @api.multi
    def unlink(self):
        if self.state not in 'draft':
            raise UserError(_('You cannot delete the verification created.'))
        super(EmployeeVerification, self).unlink()
