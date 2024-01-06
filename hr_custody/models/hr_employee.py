# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    custody_count = fields.Integer(compute='_compute_custody_count',
                                   string='# Custody',
                                   help='This field represents '
                                        'the count of custodies.')
    equipment_count = fields.Integer(compute='_compute_equipment_count',
                                     string='# Equipments',
                                     help='This field represents '
                                          'the count of equipments.',
                                     )

    @api.depends('custody_count')
    def _compute_custody_count(self):
        """The compute function
        the count of custody
        associated with each employee."""
        for each in self:
            custody_ids = self.env['hr.custody'].search(
                [('employee_id', '=', each.id)])
            each.custody_count = len(custody_ids)

    @api.depends('equipment_count')
    def _compute_equipment_count(self):
        """The Compute function the count
        of distinct equipment
        properties associated
        with each employee. """
        for each in self:
            equipment_obj = self.env['hr.custody'].search(
                [('employee_id', '=', each.id), ('state', '=', 'approved')])
            equipment_ids = []
            for each1 in equipment_obj:
                if each1.custody_property_id.id not in equipment_ids:
                    equipment_ids.append(each1.custody_property_id.id)
            each.equipment_count = len(equipment_ids)

    def custody_view(self):
        """ The function Used to returning the
        view of all custody contracts
        related to the current employee"""
        for each1 in self:
            custody_obj = self.env['hr.custody'].search(
                [('employee_id', '=', each1.id)])
            custody_ids = []
            for each in custody_obj:
                custody_ids.append(each.id)
            view_id = self.env.ref('hr_custody.hr_custody_form_view').id
            if custody_ids:
                if len(custody_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'hr.custody',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),
                        'res_id': custody_ids and custody_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', custody_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'hr.custody',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),
                        'res_id': custody_ids
                    }

                return value

    def equipment_view(self):
        """The function used to returning the
         view of all custody contracts
         that are in approved state,"""
        for each1 in self:
            equipment_obj = self.env['hr.custody'].search(
                [('employee_id', '=', each1.id), ('state', '=', 'approved')])
            equipment_ids = []
            for each in equipment_obj:
                if each.custody_property_id.id not in equipment_ids:
                    equipment_ids.append(each.custody_property_id.id)
            view_id = self.env.ref('hr_custody.custody_custody_form_view').id
            if equipment_ids:
                if len(equipment_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'custody.property',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Equipments'),
                        'res_id': equipment_ids and equipment_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', equipment_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'custody.property',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Equipments'),
                        'res_id': equipment_ids
                    }
                return value
