# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Yadhu K (<https://www.cybrosys.com>)
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

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


class EmployeeChart(http.Controller):

    @http.route('/get/employees', type='json', auth='public', method=['POST'], csrf=False)
    def get_employee_ids(self):
        employees = request.env['hr.employee'].sudo().search([('parent_id', '=', False)])
        names = []
        if len(employees) == 1:
            key = employees.id
            return key
        elif len(employees) == 0:
            raise UserError(
                "Should not have manager for the employee in the top of the chart")
        else:
            for emp in employees:
                names.append(emp.name)
            raise UserError(
                "These employees have no Manager %s" % (names))


