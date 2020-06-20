# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Jesni Banu (<https://www.cybrosys.com>)
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
from datetime import datetime
from odoo import models, fields, api, _


class HrAnnouncements(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _announcement_count(self):
        now = datetime.now()
        now_date = now.date()
        for rec in self:
            ann_ids_general = self.env['hr.announcement'].sudo().search([('is_announcement', '=', True),
                                                                         ('state', 'in', ('approved', 'done')),
                                                                         ('date_start', '<=', now_date),
                                                                         ('date_end', '>=', now_date)])
            ann_ids_emp = self.env['hr.announcement'].search([('employee_ids', 'in', [rec.id]),
                                                              ('announcement_type', '=', 'employee'),
                                                              ('state', 'in', ('approved', 'done')),
                                                              ('date_start', '<=', now_date),
                                                              ('date_end', '>=', now_date)])
            ann_ids_dep = self.env['hr.announcement'].sudo().search([('department_ids', 'in', [rec.department_id.id]),
                                                                     ('announcement_type', '=', 'department'),
                                                                     ('state', 'in', ('approved', 'done')),
                                                                     ('date_start', '<=', now_date),
                                                                     ('date_end', '>=', now_date)])
            ann_ids_job = self.env['hr.announcement'].sudo().search([('position_ids', 'in', [rec.job_id.id]),
                                                                     ('announcement_type', '=', 'job_position'),
                                                                     ('state', 'in', ('approved', 'done')),
                                                                     ('date_start', '<=', now_date),
                                                                     ('date_end', '>=', now_date)])
            rec.announcement_count = len(ann_ids_general) + len(ann_ids_emp) + len(ann_ids_dep) + len(ann_ids_job)

    @api.multi
    def announcement_view(self):
        now = datetime.now()
        now_date = now.date()
        for rec in self:
            ann_ids_general = self.env['hr.announcement'].sudo().search([('is_announcement', '=', True),
                                                                         ('state', 'in', ('approved', 'done')),
                                                                         ('date_start', '<=', now_date),
                                                                         ('date_end', '>=', now_date)])
            ann_ids_emp = self.env['hr.announcement'].sudo().search([('announcement_type', '=', 'employee'),
                                                                     ('employee_ids', 'in', [rec.id]),
                                                                     ('state', 'in', ('approved', 'done')),
                                                                     ('date_start', '<=', now_date),
                                                                     ('date_end', '>=', now_date)])
            ann_ids_dep = self.env['hr.announcement'].sudo().search([('announcement_type', '=', 'department'),
                                                                     ('department_ids', 'in', [rec.department_id.id]),
                                                                     ('state', 'in', ('approved', 'done')),
                                                                     ('date_start', '<=', now_date),
                                                                     ('date_end', '>=', now_date)])
            ann_ids_job = self.env['hr.announcement'].sudo().search([('announcement_type', '=', 'job_position'),
                                                                     ('position_ids', 'in', [rec.job_id.id]),
                                                                     ('state', 'in', ('approved', 'done')),
                                                                     ('date_start', '<=', now_date),
                                                                     ('date_end', '>=', now_date)])

            ann_obj = ann_ids_general.ids + ann_ids_emp.ids + ann_ids_job.ids + ann_ids_dep.ids
        ann_ids = []
        for each in ann_obj:
            ann_ids.append(each)
        view_id = self.env.ref('hr_reward_warning.view_hr_announcement_form').id
        if ann_ids:
            if len(ann_ids) > 1:
                value = {
                    'domain': str([('id', 'in', ann_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.announcement',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Announcements'),
                    'res_id': ann_ids
                }
            else:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.announcement',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Announcements'),
                    'res_id': ann_ids and ann_ids[0]
                }
            return value

    announcement_count = fields.Integer(compute='_announcement_count', string='# Announcements')
