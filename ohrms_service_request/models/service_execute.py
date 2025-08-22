# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Raneesha MK (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
from odoo import fields, models


class ServiceExecute(models.Model):
    """ Model representing a service execution"""
    _name = 'service.execute'
    _rec_name = 'issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Execute'

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
    test_id = fields.Many2one('service.request', string='test',
                              help="Test service")
    notes = fields.Text(string="Internal notes", help="Any description")
    executor_product = fields.Char(string='Service Item',
                                   help="Which item is going to service")
    type_service = fields.Char(string='Service Type',
                               help="Which type of service")

    def action_service_check(self):
        """ Change the state of the associated 'service.request' object to
            'check' and update the 'state_execute' field to 'check'."""
        self.test_id.sudo().state = 'check'
        self.write({
            'state_execute': 'check'
        })
        return
