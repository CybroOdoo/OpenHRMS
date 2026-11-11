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
from odoo import api, fields, models


class ServiceExecute(models.Model):
    """ Model representing a service execution"""
    _name = 'service.execute'
    _rec_name = 'issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Execute'
    _order = 'create_date desc'

    client_id = fields.Many2one('hr.employee', string="Client",
                                help="Name of the client")
    executor_id = fields.Many2one('hr.employee', string='Executor',
                                  help="Select the Executor")
    issue = fields.Char(string="Issue",
                        help="What issue you have to request service")
    execute_date = fields.Datetime(string="Date Of Reporting",
                                   help="Issue reporting date")
    state_execute = fields.Selection(
        [('draft', 'Draft'), ('requested', 'Requested'),
         ('assign', 'Assigned')
            , ('check', 'Checked'), ('reject', 'Rejected'),
         ('approved', 'Approved')], string="State", tracking=True,
        help="state of the request")
    request_id = fields.Many2one('service.request', string='Service Request',
                              ondelete='cascade', help="Test service")
    notes = fields.Text(string="Internal notes", help="Any description")
    executor_product = fields.Char(string='Service Item',
                                   help="Which item is going to service")
    type_service = fields.Many2one('service.category', string='Service Type',
                               help="Which type of service")
    priority = fields.Selection(related='request_id.priority', string='Priority')
    deadline_date = fields.Datetime(related='request_id.deadline_date', string='Deadline')
    is_service_manager = fields.Boolean(
        string="Is Service Manager",
        compute='_compute_service_user_roles',
        help="Checks if current user has manager privileges"
    )
    is_service_executor = fields.Boolean(
        string="Is Service Executor",
        compute='_compute_service_user_roles',
        help="Checks if current user is an executor"
    )

    @api.depends_context('uid')
    def _compute_service_user_roles(self):
        """Compute user roles for button visibility."""
        is_manager = (
            self.env.user.has_group('hr.group_hr_manager')
            or self.env.user.has_group('hr_attendance.group_hr_attendance_manager')
            or self.env.user.has_group('project.group_project_manager')
        )
        is_executor = self.env.user.has_group('ohrms_service_request.service_group_executor')
        for record in self:
            record.is_service_manager = is_manager
            record.is_service_executor = is_executor

    def action_service_check(self):
        """ Change the state of the associated 'service.request' object to
            'check' and update the 'state_execute' field to 'check'."""
        self.request_id.sudo().state = 'check'
        self.write({
            'state_execute': 'check'
        })
        
        # Send email/message notification to the manager who created/assigned it
        if self.request_id.create_uid:
            self.request_id.sudo().message_post(
                body='Execution completed by technician. Please review and approve the service request.',
                subject='Service Execution Completed',
                partner_ids=[self.request_id.create_uid.partner_id.id],
                message_type='comment',
            )
        return
