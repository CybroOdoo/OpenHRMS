# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WizardReason(models.TransientModel):
    """
        Hr custody contract refuse wizard.
            """
    _name = 'wizard.reason'

    def send_reason(self):
        context = self._context
        reject_obj = self.env[context.get('model_id')].search([('id', '=', context.get('reject_id'))])
        if 'renew' in context.keys():
            reject_obj.write({'state': 'approved',
                              'renew_reject': True,
                              'renew_rejected_reason': self.reason})
        else:
            if context.get('model_id') == 'hr.holidays':
                reject_obj.write({'rejected_reason': self.reason})
                reject_obj.action_refuse()
            else:
                reject_obj.write({'state': 'rejected',
                                  'rejected_reason': self.reason})

    reason = fields.Text(string="Reason", help="Reason")
