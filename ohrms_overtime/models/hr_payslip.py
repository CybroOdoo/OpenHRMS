from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime')

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(PayslipOverTime, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                      ('contract_id', '=', self.contract_id.id),
                                                      ('state', '=', 'approved'), ('payslip_paid', '=', False)])
        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        if overtime_id:
            self.overtime_ids = overtime_id
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            res.append(input_data)
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True
        return super(PayslipOverTime, self).action_payslip_done()
