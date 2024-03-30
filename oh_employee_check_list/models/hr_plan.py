# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
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
###############################################################################
from odoo import models, _
from odoo.exceptions import UserError


class HrPlan(models.Model):
    """Inherit hr_plan model for deleting plan
    which is related to checklist record"""
    _inherit = 'hr.plan'

    def unlink(self):
        """
        Function is used for checking while deleting
        plan which is related to checklist record
        and raise error.
        """
        onboard_id = self.env.ref('hr.onboarding_plan')
        offboard_id = self.env.ref('hr.offboarding_plan')
        for record in self:
            if record.id == offboard_id.id or record.id == onboard_id.id:
                raise UserError(_("Checklist Record's Can't Be Delete!"))
        return super(HrPlan, self).unlink()
