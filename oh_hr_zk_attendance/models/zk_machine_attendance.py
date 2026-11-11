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


class ZkMachineAttendance(models.Model):
    """Model to hold data from the biometric device"""
    _name = 'zk.machine.attendance'
    _description = 'Attendance'
    _inherit = 'hr.attendance'

    device_id_num = fields.Char(string='Biometric Device ID',
                                help="The ID of the Biometric Device")
    punch_type = fields.Selection([('0', 'Check In'), ('1', 'Check Out'),
                                   ('2', 'Break Out'), ('3', 'Break In'),
                                   ('4', 'Overtime In'), ('5', 'Overtime Out'),
                                   ('255', 'Duplicate')],
                                  string='Punching Type',
                                  help='Punching type of the attendance')
    attendance_type = fields.Selection([('1', 'Finger'), ('15', 'Face'),
                                        ('2', 'Type_2'), ('3', 'Password'),
                                        ('4', 'Card'), ('255', 'Duplicate')],
                                       string='Category',
                                       help="Attendance detecting methods")
    punching_time = fields.Datetime(string='Punching Time',
                                    help="Punching time in the device")
    address_id = fields.Many2one('res.partner', string='Working Address',
                                 help="Working address of the employee")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Name of the Company",
                                 default=lambda self: self.env.company)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """Override the validity check constraint from hr.attendance to allow
        staging punch records."""
        pass

    def _get_overtimes_to_update_domain(self):
        """Return an empty domain to prevent updating overtime records for
        staging biometric device attendances."""
        return []

    def _update_overtime(self, attendance_domain=None):
        """Bypass overtime calculation for biometric device attendance
        records."""
        pass

    @api.depends('check_in', 'check_out', 'employee_id')
    def _compute_overtime_hours(self):
        """Compute overtime hours as zero for machine attendance records."""
        for record in self:
            if hasattr(record, 'overtime_hours'):
                record.overtime_hours = 0.0

    @api.depends('employee_id')
    def _compute_validated_overtime_hours(self):
        """Compute validated overtime hours as zero for machine attendance
        records."""
        for record in self:
            if hasattr(record, 'validated_overtime_hours'):
                record.validated_overtime_hours = 0.0
