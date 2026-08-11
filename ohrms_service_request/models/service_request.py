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
from odoo.exceptions import ValidationError, UserError


class ServiceRequest(models.Model):
    """ Model representing a service request in the system."""
    _name = 'service.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Service Request"
    _order = "create_date desc"

    def _get_employee_id(self):
        """Current employee"""
        employee_rec = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    service_name = fields.Char(required=True, string="Subject", tracking=True,
                               help="Service name")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=_get_employee_id, readonly=True,
                                  required=True, tracking=True, help="Related Employee")
    service_date = fields.Datetime(string="Service Date", required=True, tracking=True,
                                   help="Service date")
    state = fields.Selection([('draft', 'Draft'),
                              ('requested', 'Requested'),
                              ('assign', 'Assigned'),
                              ('check', 'Checked'),
                              ('reject', 'Rejected'),
                              ('approved', 'Approved')], default='draft',
                             tracking=True, help="Stages of serice")
    service_executor_id = fields.Many2one('hr.employee',
                                          string='Assigned To', tracking=True,
                                          help="Employee- executor for "
                                               "this service")
    read_only = fields.Boolean(string="Check field",
                               compute='_compute_read_only',
                               help="checking project manager privileges")
    execution_ids = fields.One2many('service.execute',
                                 'request_id', string='Executions',
                                 help="Related service executions")
    execution_count = fields.Integer(compute='_compute_execution_count', string='Execution Count')
    internal_note = fields.Text(string="Description",
                                help="Notes for the internal purpose")
    service_type = fields.Many2one('service.category', string='Service Type',
                                   required=True, tracking=True, help="Type for the service request")
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority', default='0', tracking=True)
    deadline_date = fields.Datetime(string="Deadline", tracking=True, help="Expected completion deadline")
    service_product_id = fields.Many2one('product.product',
                                         string='Product/Asset', tracking=True,
                                         required=True,
                                         help="Product you want to service")
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, help="Name- reference",
                       default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals):
        """Create a service request"""
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('service.request')
        return super(ServiceRequest, self).create(vals)

    @api.depends_context('uid')
    def _compute_read_only(self):
        """Compute method to determine if the user has project manager privileges."""
        for record in self:
            if self.env.user.has_group('project.group_project_manager') or self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
                record.read_only = True
            else:
                record.read_only = False

    @api.depends('execution_ids')
    def _compute_execution_count(self):
        """Compute the total number of executions for the service request."""
        for record in self:
            record.execution_count = len(record.execution_ids)

    def action_open_executions(self):
        """Open the tree/form view of related service executions."""
        self.ensure_one()
        return {
            'name': _('Service Executions'),
            'view_mode': 'list,form',
            'res_model': 'service.execute',
            'domain': [('request_id', '=', self.id)],
            'context': {'default_request_id': self.id},
            'type': 'ir.actions.act_window',
        }

    def action_submit_reg(self):
        """ Change the state of the service request to 'requested'."""
        self.ensure_one()
        self.sudo().write({
            'state': 'requested'
        })
        return

    def action_assign_executor(self):
        """ Change the state of the service request to 'assign'."""
        self.ensure_one()
        if not self.service_executor_id:
            raise ValidationError(
                _("Select Executer For the Requested Service"))
        self.write({
            'state': 'assign'
        })
        vals = {
            'issue': self.service_name,
            'executor_id': self.service_executor_id.id,
            'client_id': self.employee_id.id,
            'executor_product': self.service_product_id.name,
            'type_service': self.service_type.id,
            'execute_date': self.service_date,
            'state_execute': self.state,
            'notes': self.internal_note,
            'request_id': self.id,
        }
        execute_rec = self.env['service.execute'].sudo().create(vals)
        
        # Send email/message notification to the assigned executor
        if self.service_executor_id.user_id:
            execute_rec.message_post(
                body='You have been assigned to execute this service request. Please review and complete it.',
                subject='Service Execution Assigned',
                partner_ids=[self.service_executor_id.user_id.partner_id.id],
                message_type='comment',
            )
        return

    def action_service_approval(self):
        """Approve the service request"""
        for record in self:
            record.execution_ids.sudo().state_execute = 'approved'
            record.write({
                'state': 'approved'
            })
        return

    def action_service_rejection(self):
        """Reject the service request."""
        self.write({
            'state': 'reject'
        })
        return

    def unlink(self):
        """ Prevent deletion of records unless they are in 'draft' or 'reject' state. """
        for request in self:
            if request.state not in ('draft', 'reject'):
                raise UserError(_("You can only delete service requests that are in 'Draft' or 'Rejected' state."))
        return super(ServiceRequest, self).unlink()
