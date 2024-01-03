# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ranjith R(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class HrAllocationReport(models.TransientModel):
    """Get report about hr allocation   """
    _name = 'hr.allocation.report'
    _description = 'Get Pdf Report'
    filter = fields.Selection(selection=[('type_wise', 'Type Wise'),
                                         ('employee_wise', 'Employee Wise')],
                              default="type_wise",
                              string="Filter Options for Report",
                              help="Field to choose filter of report", )
    employee_id = fields.Many2one('hr.employee',
                                  string="Choose Employee",
                                  help="Field to select employee for report")
    type = fields.Selection(
        [('transfer', 'Transfer'), ('allocation', 'Allocation')],
        string="Type", default="allocation",
        help="Field to specify type of report")
    from_date = fields.Date(string="From Date", required=True,
                            help="Field to select start date of report")
    to_date = fields.Date(string="To Date", required=True,
                          help="Field to select end date filter of report")

    def action_print_pdf(self):
        """
        Summary:
           function to print pdf
        """
        if self.filter == 'employee_wise':
            if not self.employee_id:
                raise ValidationError(_('Please select the employee'))
            query = """select * from hr_allocation_transfer
            inner join 
            hr_employee on hr_allocation_transfer.employee_id =hr_employee.id
            """
            query += f"""where hr_employee.id = {self.employee_id.id:d} """
            if self.from_date:
                query += \
                    f""" and hr_allocation_transfer.date >= '{self.from_date}' 
                     """
            if self.to_date:
                query += \
                    f""" and hr_allocation_transfer.date <= '{self.to_date}' """
            self.env.cr.execute(query)
            datas = self.env.cr.dictfetchall()
            data = {
                'form': self.read()[0],
                'datas': datas,
                'employee_id': self.employee_id.name,
                'from_date': self.from_date,
                'to_date': self.to_date
            }
            return self.env.ref(
                'ohrms_employee_accommodation_management.'
                'action_hr_allocation_report_employee').report_action(
                None,
                data=data)
        if self.filter == 'type_wise':
            if not self.type:
                raise ValidationError(_('Please select the type'))
            query = """select * from hr_allocation_transfer
                   """
            if self.type:
                query += \
                    f"""where hr_allocation_transfer.type = '{self.type}' """
            if self.from_date:
                query += \
                    f""" and hr_allocation_transfer.date >= '{self.from_date}' 
                     """
            if self.to_date:
                query += \
                    f""" and hr_allocation_transfer.date <= '{self.to_date}' """
            self.env.cr.execute(query)
            datas = self.env.cr.dictfetchall()
            data = {
                'form': self.read()[0],
                'datas': datas,
                'type': self.type,
                'from_date': self.from_date,
                'to_date': self.to_date
            }
            return self.env.ref(
                'ohrms_employee_accommodation_management'
                '.action_hr_allocation_report_type').report_action(
                None,
                data=data)
