# -*- coding: utf-8 -*-
#############################################################################
#   A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (<https://www.cybrosys.com>)
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
from odoo import models


class HrPayslip(models.Model):
    """Inherited to add fields"""
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """used get inputs , to add datas"""
        res = super().get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        for record in contract_ids:
            if contract_ids[0]:
                emp_id = contract_obj.browse(record[0].id).employee_id
                for result in res:
                    if emp_id.deduced_amount_per_month != 0:
                        if result.get('code') == 'INSUR':
                            result['amount'] = emp_id.deduced_amount_per_month
        return res
