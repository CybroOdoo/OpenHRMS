# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    discipline_count = fields.Integer(compute="_compute_discipline_count")

    def _compute_discipline_count(self):
        all_actions = self.env['disciplinary.action'].read_group([
            ('employee_name', 'in', self.ids),
            ('state', '=', 'action'),
        ], fields=['employee_name'], groupby=['employee_name'])
        mapping = dict([(action['employee_name'][0], action['employee_name_count']) for action in all_actions])
        for employee in self:
            employee.discipline_count = mapping.get(employee.id, 0)


class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'

    # Discipline Categories

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Details")


class CategoryAction(models.Model):
    _name = 'action.category'
    _description = 'Action Category'

    # Action Categories

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Details")

class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting Explanation'),
        ('submitted', 'Waiting Action'),
        ('action', 'Action Validated'),
        ('cancel', 'Cancelled'),

    ], default='draft', track_visibility='onchange')

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    employee_name = fields.Many2one('hr.employee', string='Employee', required=True)
    department_name = fields.Many2one('hr.department', string='Department', required=True)
    discipline_reason = fields.Many2one('discipline.category', string='Reason', required=True)
    explanation = fields.Text(string="Explanation by Employee", help='Employee have to give Explanation'
                                                                     'to manager about the violation of discipline')
    action = fields.Many2one('action.category', string="Action")
    read_only = fields.Boolean(compute="get_user", default=True)
    warning_letter = fields.Html(string="Warning Letter")
    suspension_letter = fields.Html(string="Suspension Letter")
    termination_letter = fields.Html(string="Termination Letter")
    warning = fields.Integer(default=False)
    action_details = fields.Text(string="Action Details")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments",
                                      help="Employee can submit any documents which supports their explanation")
    note = fields.Text(string="Internal Note")
    joined_date = fields.Date(string="Joined Date")

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)

    # Check the user is a manager or employee
    @api.depends('read_only')
    def get_user(self):

        if self.env.user.has_group('hr.group_hr_manager'):
            self.read_only = True
        else:
            self.read_only = False

    # Check the Action Selected
    @api.onchange('action')
    def onchange_action(self):
        if self.action.name == 'Written Warning':
            self.warning = 1
        elif self.action.name == 'Suspend the Employee for one Week':
            self.warning = 2
        elif self.action.name == 'Terminate the Employee':
            self.warning = 3
        elif self.action.name == 'No Action':
            self.warning = 4
        else:
            self.warning = 5

    @api.onchange('employee_name')
    @api.depends('employee_name')
    def onchange_employee_name(self):

        department = self.env['hr.employee'].search([('name', '=', self.employee_name.name)])
        self.department_name = department.department_id.id

        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    @api.depends('discipline_reason')
    def onchange_reason(self):
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    
    def assign_function(self):

        for rec in self:
            rec.state = 'explain'

    
    def cancel_function(self):
        for rec in self:
            rec.state = 'cancel'

    
    def set_to_function(self):
        for rec in self:
            rec.state = 'draft'

    
    def action_function(self):
        for rec in self:
            if not rec.action:
                raise ValidationError(_('You have to select an Action !!'))

            if self.warning == 1:
                if not rec.warning_letter or rec.warning_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Warning Letter in Action Information !!'))

            elif self.warning == 2:
                if not rec.suspension_letter or rec.suspension_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Suspension Letter in Action Information !!'))

            elif self.warning == 3:
                if not rec.termination_letter or rec.termination_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Termination Letter in  Action Information !!'))

            elif self.warning == 4:
                self.action_details = "No Action Proceed"

            elif self.warning == 5:
                if not rec.action_details:
                    raise ValidationError(_('You have to fill up the  Action Information !!'))
            rec.state = 'action'

    
    def explanation_function(self):
        for rec in self:

            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))
        if len(self.explanation.split()) < 5:
            raise ValidationError(_('Your explanation must contain at least 5 words   !!'))

        self.write({
            'state': 'submitted'
        })
