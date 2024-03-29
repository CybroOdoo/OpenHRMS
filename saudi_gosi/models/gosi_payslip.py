# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class GosiPayslip(models.Model):
    """This class create GOSI payslip record"""
    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  required=True, help="Employee")
    department = fields.Char(string="Department",
                             related='employee_id.department_id.name',
                             help="Department")
    position = fields.Char(string='Job Position', required=True,
                           related='employee_id.job_id.name',
                           help="Job Position")
    nationality = fields.Char(string='Nationality', required=True,
                              related='employee_id.country_id.name',
                              help="Nationality")
    type_gosi = fields.Selection(string='Type', required=True,
                                 related='employee_id.type', help="Gosi Type")
    dob = fields.Date(string='Date Of Birth', required=True,
                      related='employee_id.birthday', help="Date Of Birth")
    gos_numb = fields.Char(string='GOSI Number', required=True,
                           related='employee_id.gosi_number',
                           track_visibility='onchange', help="Gosi number")
    issued_dat = fields.Date(string='Issued Date', required=True,
                             related='employee_id.issue_date',
                             help="Issued date")
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        """Generate sequence number"""
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(GosiPayslip, self).create(vals)
