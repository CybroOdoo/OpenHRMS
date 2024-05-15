# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ServiceRequest(models.Model):
	"""
	Model representing a service request in the system.
	"""
	_name = 'service.request'
	_rec_name = 'name'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Service Request"

	def _get_employee_id(self):
		"""Current employee"""
		employee_rec = self.env['hr.employee'].search(
			[('user_id', '=', self.env.uid)], limit=1)
		return employee_rec.id

	service_name = fields.Char(required=True, string="Reason For Service",
							   help="Service name")
	employee_id = fields.Many2one('hr.employee', string="Employee",
	                              default=_get_employee_id, readonly=True,
	                              required=True, help="Employee")
	service_date = fields.Datetime(string="date", required=True,
	                               help="Service date")
	state = fields.Selection([('draft', 'Draft'),
	                          ('requested', 'Requested'),
	                          ('assign', 'Assigned'),
	                          ('check', 'Checked'),
	                          ('reject', 'Rejected'),
	                          ('approved', 'Approved')], default='draft',
	                         tracking=True, help="State")
	service_executer_id = fields.Many2one('hr.employee',
	                                      string='Service Executer',
	                                      help="Service executer")
	read_only = fields.Boolean(string="check field",
	                           compute='_compute_read_only', help="Readonly")
	tester_ids = fields.One2many('service.execute', 'test_id', string='tester',
	                             help="Tester")
	internal_note = fields.Text(string="internal notes", help="Internal Notes")
	service_type = fields.Selection([('repair', 'Repair'),
	                                 ('replace', 'Replace'),
	                                 ('updation', 'Updation'),
	                                 ('checking', 'Checking'),
	                                 ('adjust', 'Adjustment'),
	                                 ('other', 'Other')],
	                                string='Type Of Service', required=True,
	                                help="Type for the service request")
	service_product_id = fields.Many2one('product.product',
	                                     string='Item For Service',
	                                     required=True,
	                                     help="Product you want to service")
	name = fields.Char(string='Reference', required=True, copy=False,
	                   readonly=True,
	                   default=lambda self: _('New'))

	@api.model
	def create(self, vals):
		"""Create a service request"""
		vals['name'] = self.env['ir.sequence'].next_by_code('service.request')
		return super(ServiceRequest, self).create(vals)

	@api.depends('read_only')
	def _compute_read_only(self):
		"""
		Compute method to determine if the user has project manager privileges.
		"""
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('project.group_project_manager'):
			self.read_only = True
		else:
			self.read_only = False

	def action_submit_reg(self):
		"""
		Change the state of the service request to 'requested'.
		"""
		self.ensure_one()
		self.sudo().write({
			'state': 'requested'
		})
		return

	def action_assign_executer(self):
		"""
		Change the state of the service request to 'assign'.
		"""
		self.ensure_one()
		if not self.service_executer_id:
			raise ValidationError(
				_("Select Executer For the Requested Service"))
		self.write({
			'state': 'assign'
		})
		vals = {
			'issue': self.service_name,
			'executer_id': self.service_executer_id.id,
			'client_id': self.employee_id.id,
			'executer_product': self.service_product_id.name,
			'type_service': self.service_type,
			'execute_date': self.service_date,
			'state_execute': self.state,
			'notes': self.internal_note,
			'test_id': self.id,
		}
		self.env['service.execute'].sudo().create(vals)
		return

	def action_service_approval(self):
		"""Approve the service request"""
		for record in self:
			record.tester_ids.sudo().state_execute = 'approved'
			record.write({
				'state': 'approved'
			})
		return

	def action_service_rejection(self):
		"""
		Reject the service request.
		"""
		self.write({
			'state': 'reject'
		})
		return
