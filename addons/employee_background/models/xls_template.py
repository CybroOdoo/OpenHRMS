# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import logging
from odoo import models


class DefaultTemplateXls(models.AbstractModel):
    _name = 'report.employee_background.default_verification_details'
    # _inherit = 'report.report_xlsx.abstract'

    _logger = logging.getLogger(__name__)

    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})

        sheet.merge_range('B1:E1', 'Required Details', format1)
        sheet.merge_range('A2:B2', 'Applicant Name:', format3)
        sheet.merge_range('A3:C3', 'Information Required', format2)
        sheet.merge_range('D3:F3', 'Details Given', format2)
        sheet.merge_range('G3:I3', 'Details(Correct/Wrong)', format2)
        sheet.merge_range('A5:C5', 'Education Details', format3)
        sheet.merge_range('B6:C6', 'Graduation', format3)
        sheet.merge_range('D6:F6', '', format3)
        sheet.merge_range('G6:I6', '', format3)
        sheet.merge_range('B7:C7', 'Plus Two', format3)
        sheet.merge_range('D7:F7', '', format3)
        sheet.merge_range('G7:I7', '', format3)
        sheet.merge_range('A9:C9', 'Work Details', format3)
        sheet.merge_range('D9:F9', '', format3)
        sheet.merge_range('G9:I9', '', format3)
        sheet.merge_range('A11:C11', 'Criminal Background', format3)
        sheet.merge_range('D11:F11', '', format3)
        sheet.merge_range('G11:I11', '', format3)
        sheet.merge_range('A13:C13', 'Disciplinary Allegation in Previous Work Locations', format3)
        sheet.merge_range('D13:F13', '', format3)
        sheet.merge_range('G13:I13', '', format3)
