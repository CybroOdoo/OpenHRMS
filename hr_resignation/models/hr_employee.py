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
from odoo import fields, models


class HrEmployee(models.Model):
    """
    Extends the 'hr.employee' model to include additional fields related to
    employee resignation.
    """
    _inherit = 'hr.employee'

    resign_date = fields.Date(string='Resign Date', readonly=True,
                              groups="hr.group_hr_user",
                              help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False,
                              groups="hr.group_hr_user",
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False,
                           groups="hr.group_hr_user",
                           help="If checked then employee has fired")


class HrEmployeePublic(models.Model):
    """
    Extends 'hr.employee.public' so that normal employees can read employee
    joining_date and id_expiry_date without triggering Odoo 20 private field AccessError.
    """
    _inherit = 'hr.employee.public'

    joining_date = fields.Date(related='employee_id.joining_date', string='Joining Date', readonly=True, compute_sudo=True)
    id_expiry_date = fields.Date(related='employee_id.id_expiry_date', string='Expiry Date', readonly=True, compute_sudo=True)

