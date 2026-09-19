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
from odoo import api, fields, models, _

class HrPayslipRunGenerate(models.TransientModel):
    """Wizard to select a salary structure and generate a payslip batch."""
    _name = 'hr.payslip.run.generate'
    _description = 'Payslip Run Generation Wizard'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure',
                                help='Select the Salary Structure to generate payslips for.')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batch')
    name = fields.Char(related='payslip_run_id.name', string='Name', readonly=True)
    date_start = fields.Date(related='payslip_run_id.date_start', string='Date From', readonly=True)
    date_end = fields.Date(related='payslip_run_id.date_end', string='Date To', readonly=True)

    @api.model
    def default_get(self, fields):
        """Populate the default payslip run id from the context."""
        res = super(HrPayslipRunGenerate, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'hr.payslip.run':
            res['payslip_run_id'] = self.env.context.get('active_id')
        return res

    def action_continue(self):
        """Proceed to the next wizard to select employees, passing the structure"""
        self.ensure_one()
        
        context = dict(self.env.context)
        if self.struct_id:
            context['default_struct_id'] = self.struct_id.id
        if self.payslip_run_id:
            context['active_id'] = self.payslip_run_id.id
            context['active_ids'] = [self.payslip_run_id.id]
            context['batch_run_id'] = self.payslip_run_id.id
        return {
            'name': _('Select Employees'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.employees',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
