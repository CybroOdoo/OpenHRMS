# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, _


class HrClearanceType(models.Model):
    """
    Model for defining different types of HR clearances required during employee resignation.
    """
    _name = 'hr.clearance.type'
    _description = 'HR Clearance Type'

    name = fields.Char(string='Name', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    default_responsible_id = fields.Many2one('res.users', string='Default Responsible')


class HrClearanceTemplate(models.Model):
    """
    Model for creating templates that group multiple clearance types together.
    """
    _name = 'hr.clearance.template'
    _description = 'HR Clearance Template'

    name = fields.Char(string='Template Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    clearance_type_ids = fields.Many2many('hr.clearance.type', string='Clearance Types')


class HrResignationClearanceLine(models.Model):
    """
    Model for individual clearance items assigned to specific users during a resignation.
    """
    _name = 'hr.resignation.clearance.line'
    _description = 'Resignation Clearance Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    resignation_id = fields.Many2one('hr.resignation', string='Resignation', ondelete='cascade')
    clearance_type_id = fields.Many2one('hr.clearance.type', string='Clearance Type', required=True)
    department_id = fields.Many2one('hr.department', related='clearance_type_id.department_id', store=True)
    responsible_user_id = fields.Many2one('res.users', string='Responsible', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('blocked', 'Blocked')
    ], string='Status', default='pending', tracking=True)
    has_dues = fields.Boolean(string='Has Dues', compute='_compute_has_dues', store=True, tracking=True)
    due_amount = fields.Float(string='Due Amount', tracking=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    cleared_date = fields.Datetime(string='Cleared Date')
    is_responsible = fields.Boolean(compute='_compute_is_responsible')

    @api.depends('due_amount')
    def _compute_has_dues(self):
        """
        Compute method to determine if there are any outstanding dues for this clearance line.
        """
        for rec in self:
            rec.has_dues = bool(rec.due_amount)

    @api.depends('responsible_user_id')
    def _compute_is_responsible(self):
        """
        Compute method to check if the current user is responsible for this clearance line
        or has HR Manager privileges.
        """
        for rec in self:
            rec.is_responsible = (self.env.user == rec.responsible_user_id) or self.env.user.has_group(
                'hr.group_hr_manager')

    def action_mark_cleared(self):
        """
        Action to mark the clearance line as cleared and record the clearance date.
        """
        for rec in self:
            rec.state = 'cleared'
            rec.cleared_date = fields.Datetime.now()
            # If all are cleared, we can trigger the resignation progress computation
            rec.resignation_id._compute_clearance_progress()

    def action_mark_blocked(self):
        """
        Action to mark the clearance line as blocked if there are unresolved issues.
        """
        for rec in self:
            rec.state = 'blocked'
