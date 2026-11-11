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


class HrPayslip(models.Model):
    """This class shows GOSI Reference of corresponding employee"""
    _inherit = 'hr.payslip'

    gosi_no_id = fields.Many2one('gosi.payslip', string='GOSI Reference',
                                 compute='_compute_gosi_no_id', store=True,
                                 readonly=False, precompute=True,
                                 help="Gosi Number")

    @api.depends('employee_id')
    def _compute_gosi_no_id(self):
        """Compute the GOSI reference based on the selected employee."""
        for rec in self:
            if rec.employee_id:
                gosi = rec.env['gosi.payslip'].search(
                    [('employee_id', '=', rec.employee_id.id)], limit=1)
                rec.gosi_no_id = gosi.id if gosi else False
            else:
                rec.gosi_no_id = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """This function is used to update the GOSI number according to the employee."""
        for rec in self:
            if rec.employee_id:
                gosi = rec.env['gosi.payslip'].search(
                    [('employee_id', '=', rec.employee_id.id)], limit=1)
                rec.gosi_no_id = gosi.id if gosi else False
            else:
                rec.gosi_no_id = False
