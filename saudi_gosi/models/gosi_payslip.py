# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
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
from odoo import api, fields, models


class GosiPayslip(models.Model):
    """This class create GOSI payslip record"""
    _name = 'gosi.payslip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee_id = fields.Many2one('hr.employee', required=True, help="Employee")
    department = fields.Char(string="Department",
                             related='employee_id.department_id.name',
                             help="Department")
    position = fields.Char(string='Job Position',
                           related='employee_id.job_id.name',
                           help="Job Position")
    nationality = fields.Char(string='Nationality',
                              related='employee_id.country_of_birth.name', store=True,
                              help="Nationality")
    type_gosi = fields.Selection(string='Type',
                                 related='employee_id.type', help="Gosi Type")
    dob = fields.Date(string='Date Of Birth',
                      related='employee_id.birthday', help="Date Of Birth")
    gos_number = fields.Char(string='GOSI Number',
                           related='employee_id.gosi_number',
                           tracking=True, help="Gosi number")
    issued_date = fields.Date(string='Issued Date',
                             related='employee_id.issue_date',
                             help="Issued date")
    name = fields.Char(string='Reference', required=True, copy=False,
                       help="Name",
                       readonly=True, default=lambda self: self.env._('New'))

    @api.model_create_multi
    def create(self, vals_list):
        """This function is used to create a sequence number for the GOSI
        payslip record"""
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == self.env._('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'gosi.payslip',
                ) or '/'

        return super().create(vals_list)
