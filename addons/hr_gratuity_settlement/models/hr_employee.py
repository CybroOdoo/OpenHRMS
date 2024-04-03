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
from odoo import fields, models
from odoo.osv import expression


class HrEmployeeProbation(models.Model):
    _inherit = 'hr.employee'

    def generate_work_entries(self, date_start, date_stop):
        """
        function is used for Generate work entries When
        Contract State in Probation,Running,Expired

        """
        date_start = fields.Date.to_date(date_start)
        date_stop = fields.Date.to_date(date_stop)

        if self:
            current_contracts = self._get_contracts(date_start, date_stop, states=['probation', 'open', 'close'])
        else:
            current_contracts = self._get_all_contracts(date_start, date_stop, states=['probation', 'open', 'close'])

        return bool(current_contracts._generate_work_entries(date_start, date_stop))

    # override the existing function for considering the probation contracts
    def _get_contracts(self, date_from, date_to, states=['open', 'probation'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        state_domain = [('state', 'in', states)]
        if kanban_state:
            state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

        return self.env['hr.contract'].search(
            expression.AND([[('employee_id', 'in', self.ids)],
                            state_domain,
                            [('date_start', '<=', date_to),
                             '|',
                             ('date_end', '=', False),
                             ('date_end', '>=', date_from)]]))
