# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import models, fields


class PropertyReturnReason(models.TransientModel):
    """
        Hr custody contract refuse wizard.
    """
    _name = 'property.return.reason'

    def send_reason(self):
        """The function used to send
        rejection reason for the associated record."""
        reject_obj = self.env[self._context.get('model_id')].search(
            [('id', '=', self._context.get('reject_id'))])
        if 'renew' in self._context.keys():
            reject_obj.write({'state': 'approved',
                              'is_renew_reject': True,
                              'renew_rejected_reason': self.reason})
        else:
            if self._context.get('model_id') == 'hr.holidays':
                reject_obj.write({'rejected_reason': self.reason})
                reject_obj.action_refuse()
            else:
                reject_obj.write({'state': 'rejected',
                                  'rejected_reason': self.reason})

    reason = fields.Text(string="Reason", help="Add the reason")
