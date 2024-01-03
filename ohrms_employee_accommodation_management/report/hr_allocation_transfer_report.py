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
from odoo import api, models


class HrAllocationTransferReport(models.AbstractModel):
    """Class to print form view"""
    _name = 'report.ohrms_employee_accommodation_management.form_print'
    _description = "Room Transfer or Allocation Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Function to print form view"""
        room_allocation = self.env['hr.allocation.transfer'].browse(docids)
        return {
            'room_allocation': room_allocation,
        }
