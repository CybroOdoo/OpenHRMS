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
from odoo import fields, models, _


class HrEmployeeFamily(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.employee.family'
    _description = 'HR Employee Family Info'
    _rec_name = 'member_name'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help='Select corresponding Employee')
    relation_id = fields.Many2one('hr.employee.relation', string="Relation",
                                  help="Relationship with the employee")
    member_name = fields.Char(string='Name', help='Name of the family member')
    member_contact = fields.Char(string='Contact No',
                                 help='Contact No of the family member')
    birth_date = fields.Date(string="DOB",
                             help='Birth date of the family member')
