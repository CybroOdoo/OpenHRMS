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
from odoo import fields, models, _


class HrEmployee(models.Model):
    """ Inherited model 'hr.employee' with additional
    fields and methods related to announcements."""
    _inherit = 'hr.employee'

    announcement_count = fields.Integer(compute='_compute_announcement_count',
                                        string='# Announcements',
                                        help="Count of Announcements")

    def _compute_announcement_count(self):
        """ Compute announcement count for an employee """
        for employee in self:
            domain = [
                ('state', '=', 'approved'),
                ('date_start', '<=', fields.Date.today())
            ]
            or_conditions = [
                ('is_announcement', '=', True),
                ('employee_ids', 'in', employee.id)
            ]
            if employee.department_id:
                or_conditions.append(('department_ids', 'in', employee.department_id.id))
            if employee.job_id:
                or_conditions.append(('position_ids', 'in', employee.job_id.id))
            
            # For N conditions, we need N-1 '|' strings at the beginning.
            or_domain = ['|'] * (len(or_conditions) - 1) + or_conditions
            domain.extend(or_domain)
            
            employee.announcement_count = self.env['hr.announcement'].sudo().search_count(domain)

    def action_open_announcements(self):
        """ Open a view displaying announcements related to the employee. """
        self.ensure_one()
        domain = [
            ('state', '=', 'approved'),
            ('date_start', '<=', fields.Date.today())
        ]
        or_conditions = [
            ('is_announcement', '=', True),
            ('employee_ids', 'in', self.id)
        ]
        if self.department_id:
            or_conditions.append(('department_ids', 'in', self.department_id.id))
        if self.job_id:
            or_conditions.append(('position_ids', 'in', self.job_id.id))
            
        or_domain = ['|'] * (len(or_conditions) - 1) + or_conditions
        domain.extend(or_domain)
        
        announcement_ids = self.env['hr.announcement'].sudo().search(domain).ids
        view_id = self.env.ref('hr_reward_warning.hr_announcement_view_form').id
        if announcement_ids:
            if len(announcement_ids) > 1:
                value = {
                    'domain': [('id', 'in', announcement_ids)],
                    'view_mode': 'list,form',
                    'res_model': 'hr.announcement',
                    'type': 'ir.actions.act_window',
                    'name': _('Announcements'),
                }
            else:
                value = {
                    'view_mode': 'form',
                    'res_model': 'hr.announcement',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Announcements'),
                    'res_id': announcement_ids and announcement_ids[0],
                }
            return value
