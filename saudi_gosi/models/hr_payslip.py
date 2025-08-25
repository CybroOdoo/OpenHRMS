# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class HrPayslip(models.Model):
    """This class shows GOSI Reference of corresponding employee"""
    _inherit = 'hr.payslip'

    gosi_no_id = fields.Many2one('gosi.payslip', string='GOSI Reference',
                              readonly=True, help="Gosi Number")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """This function is used to have the GOSI number according to the
        employee"""
        for rec in self:
            gosi_no_id = rec.env['gosi.payslip'].search(
                [('employee_id', '=', rec.employee_id.id)])
            for gosi in gosi_no_id:
                rec.gosi_no_id = gosi.id
