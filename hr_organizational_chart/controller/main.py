# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies (<https://www.cybrosys.com>)
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

    @http.route('/get/parent/colspan', type='json', auth='public', method=['POST'], csrf=False)
    def get_col_span(self, emp_id):
        if emp_id:
            employee = request.env['hr.employee'].sudo().browse(int(emp_id))
            if employee.child_ids:
                child_count = len(employee.child_ids) * 2
                return child_count

    @http.route('/get/parent/employee', type='json', auth='public', method=['POST'], csrf=False)
    def get_employee_ids(self):
        employees = request.env['hr.employee'].sudo().search([('parent_id', '=', False)])
        names = []
        key = []
        if len(employees) == 1:
            key.append(employees.id)
            key.append(len(employees.child_ids))
            return key
        elif len(employees) == 0:
            raise UserError(
                "Should not have manager for the employee in the top of the chart")
        else:
            for emp in employees:
                names.append(emp.name)
            raise UserError(
                "These employee have no Manager %s" % (names))

    def get_lines(self, loop_count):
        if loop_count:
            lines = """<tr class='lines'><td colspan='""" + str(loop_count) + """'>
                <div class='downLine'></div></td></tr><tr class='lines'>"""
            for i in range(0, loop_count):
                if i % 2 == 0:
                    if i == 0:
                        lines += """<td class="rightLine"></td>"""
                    else:
                        lines += """<td class="rightLine topLine"></td>"""
                else:
                    if i == loop_count-1:
                        lines += """<td class="leftLine"></td>"""
                    else:
                        lines += """<td class="leftLine topLine"></td>"""
            lines += """</tr>"""
            return lines

    def get_nodes(self, child_ids):
        if child_ids:
            child_nodes = """<tr>"""
            for child in child_ids:
                child_table = """<td colspan='""" + str(2) + """'>
                    <table><tr><td><div>"""
                view = """ <div id='""" + str(child.id) + """' class='o_level_1'><a>
                    <div id='""" + str(child.id) + """' class="o_employee_border">
                    <img src='/web/image/hr.employee.public/""" + str(child.id) + """/image_1024/'/></div>
                    <div class='employee_name'><p>""" + str(child.name) + """</p>
                    <p>""" + str(child.job_id.name) + """</p></div></a></div>"""
                child_nodes += child_table + view + """</div></td></tr></table></td>"""
            nodes = child_nodes + """</tr>"""
            return nodes

    @http.route('/get/parent/child', type='http', auth='user', method=['POST'], csrf=False)
    def get_parent_child(self, **post):
        if post:
            val = 0
            for line in post:
                if line:
                    val = int(line)
            child_ids = request.env['hr.employee'].sudo().browse(val).child_ids
            emp = request.env['hr.employee'].sudo().browse(val)
            table = """<table><tr><td colspan='""" + str(len(child_ids) * 2) + """'><div class="node">"""
            view = """ <div id="parent" class='o_chart_head'><a>
                <div id='""" + str(val) + """' class="o_employee_border">
                <img class='o_emp_active' src='/web/image/hr.employee.public/""" + str(val) + """/image_1024/'/></div>
                <div class='employee_name o_width'><p>""" + str(emp.name) + """</p>
                <p>""" + str(emp.job_id.name) + """</p></div></a></div>"""
            table += view + """</div></td></tr>"""
            loop_len = len(child_ids)*2
            lines = self.get_lines(loop_len)
            nodes = self.get_nodes(child_ids)
            table += lines + nodes
            return table

    @http.route('/get/child/data', type='json', auth='user', method=['POST'], csrf=False)
    def get_child_data(self, click_id):
        if click_id:
            employee = request.env['hr.employee'].sudo().browse(int(click_id))
            if employee.child_ids:
                child_count = len(employee.child_ids) * 2
                value = [child_count]
                lines = self.get_lines(child_count)
                nodes = self.get_nodes(employee.child_ids)
                child_table = lines + nodes
                value.append(child_table)
                return child_table






