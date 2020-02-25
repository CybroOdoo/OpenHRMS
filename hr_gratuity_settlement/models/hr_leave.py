import datetime
from datetime import date

from odoo import models


class LeaveDetails(models.Model):
    _inherit = 'hr.leave'

    def action_validate(self):
        """
        function for calculating leaves and updating
        probation period upon the leave days

        """
        res = super(LeaveDetails, self).action_validate()
        contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'probation')], limit=1)
        # check valid contract and probation details.
        if contract and contract.probation_id:
            training_dtl = contract.probation_id
            leave_type = self.env.ref('hr_holidays.holiday_status_unpaid')
            no_of_days = 0
            leave_info = []

            # calculating half day leave :
            if self.request_unit_half:
                for half in contract.half_leave_ids:
                    leave_info.append(half.id)
                leave_info.append(self.id)
                contract.write({'half_leave_ids': leave_info})
                if len(contract.half_leave_ids) == 2:
                    no_of_days = 1
                    contract.half_leave_ids = False

            # calculating full day leaves and updating period :
            if self.holiday_status_id.id == leave_type.id \
                    and contract.state == "probation" and training_dtl and \
                    not self.request_unit_half and not self.request_unit_hours:
                from_date = date(self.request_date_from.year,
                                 self.request_date_from.month,
                                 self.request_date_from.day)
                to_date = date(self.request_date_to.year,
                               self.request_date_to.month,
                               self.request_date_to.day)
                if from_date >= training_dtl.start_date and \
                        to_date <= training_dtl.end_date:
                    updated_date = training_dtl.end_date + datetime.timedelta(
                        days=self.number_of_days)
                    leave_info = []
                    for leave in training_dtl.leave_ids:
                        leave_info.append(leave.id)
                    leave_info.append(self.id)
                    training_dtl.write({
                        'end_date': updated_date,
                        'state': "extended",
                        'leave_ids': leave_info
                    })
                    contract.write({'trial_date_end': updated_date})

            # updating period based on half day leave:
            elif self.holiday_status_id.id == leave_type.id \
                    and contract.state == "probation" and training_dtl \
                    and self.request_unit_half:
                from_date = date(self.request_date_from.year,
                                 self.request_date_from.month,
                                 self.request_date_from.day)
                if training_dtl.end_date >= from_date >= training_dtl.start_date:
                    updated_date = training_dtl.end_date + datetime.timedelta(
                        days=no_of_days)
                    for leave in training_dtl.leave_ids:
                        leave_info.append(leave.id)
                    leave_info.append(self.id)
                    training_dtl.write({
                        'end_date': updated_date,
                        'state': "extended",
                        'leave_ids': leave_info
                    })
                    contract.write({'trial_date_end': updated_date})
        return res
