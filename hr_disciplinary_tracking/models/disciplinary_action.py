# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class DisciplinaryAction(models.Model):
    """Model representing an action for disciplinary"""
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"
    _order = 'id desc'

    @api.model_create_multi
    def create(self, vals_list):
        """Assigning sequence for new disciplinary action records"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'disciplinary.action') or _('New')
        return super().create(vals_list)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting Explanation'),
        ('submitted', 'Waiting Action'),
        ('action', 'Action Validated'),
        ('cancel', 'Cancelled'),
    ], default='draft', tracking=True,
        help="Stage for disciplinary action")
    name = fields.Char(string='Reference', copy=False,
                       readonly=True,
                       default=lambda self: _('New'),
                       help="Name for disciplinary action")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 required=True,
                                 help="Company of the current record")
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Employee name")
    department_id = fields.Many2one('hr.department', string='Department',
                                    required=True, help="Department name")
    discipline_reason_id = fields.Many2one('discipline.category', string='Reason',
                                           required=True,
                                           help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee",
                              help='Employee explanation regarding the disciplinary violation')
    action_id = fields.Many2one('discipline.category', string="Action",
                                help="Choose an action for this disciplinary action")
    read_only = fields.Boolean(compute="_compute_get_user", default=True,
                               help="Boolean field to check if the user is HR Manager")
    warning_letter = fields.Html(string="Warning Letter",
                                 help="Warning letter as disciplinary action")
    suspension_letter = fields.Html(string="Suspension Letter",
                                    help="Suspension letter as disciplinary action")
    termination_letter = fields.Html(string="Termination Letter",
                                     help="Termination letter as disciplinary action")
    warning = fields.Boolean(string='Warning', default=False,
                             help='Boolean field to show the message as warning message')
    action_details = fields.Text(string="Action Details",
                                 help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments",
                                      help="Employee can submit documents supporting their explanation")
    note = fields.Text(string="Internal Note",
                       help='Internal notes regarding the disciplinary action')
    joined_date = fields.Date(string="Joined Date",
                              help="Employee joining date")

    @api.depends_context('uid')
    def _compute_get_user(self):
        """Method for checking if the current user is an HR Manager"""
        is_manager = self.env.user.has_group('hr.group_hr_manager')
        for rec in self:
            rec.read_only = is_manager

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """On change function for employee to update department and validate state"""
        if self.state == 'action':
            raise ValidationError(_('You cannot edit a Validated Action!'))
        if self.employee_id:
            self.department_id = self.employee_id.department_id
            if not self.joined_date and self.employee_id.create_date:
                self.joined_date = self.employee_id.create_date.date()

    @api.onchange('discipline_reason_id')
    def _onchange_discipline_reason_id(self):
        """Check state on discipline reason change"""
        if self.state == 'action':
            raise ValidationError(_('You cannot edit a Validated Action!'))

    def assign_function(self):
        """Move state to Waiting Explanation"""
        return self.write({'state': 'explain'})

    def cancel_function(self):
        """Cancel the disciplinary action"""
        return self.write({'state': 'cancel'})

    def set_to_function(self):
        """Reset state to Draft"""
        return self.write({'state': 'draft'})

    def action_function(self):
        """Validate the disciplinary action"""
        for rec in self:
            if not rec.action_id:
                raise ValidationError(_('You have to select an Action!'))
            if not rec.action_details or rec.action_details in ('<p><br></p>', ''):
                raise ValidationError(
                    _('You have to fill up the Action Details in Action Information!'))
        return self.write({'state': 'action'})

    def explanation_function(self):
        """Submit employee explanation"""
        for rec in self:
            if not rec.explanation:
                raise ValidationError(_('You must give an explanation!'))
        return self.write({'state': 'submitted'})
