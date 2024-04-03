# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys (<https://www.cybrosys.com>)
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
###################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TrainingDetails(models.Model):
    _name = 'hr.training'
    _rec_name = 'employee_id'
    _description = 'HR Training'

    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    start_date = fields.Date(string="Start Date", help="Probation starting date")
    end_date = fields.Date(string="End Date", help="Probation end date")
    state = fields.Selection([('new', 'New'), ('extended', 'Extended')], required=True, default='new')
    leave_ids = fields.Many2many('hr.leave', string="Leaves")




