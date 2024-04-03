odoo.define('hr_company_policy.CompanyPolicy', function (require) {
"use strict";
console.log("Company policy");

var HrDashboard = require('hrms_dashboard.DashboardRewrite');
// var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var session = require('web.session');
var _t = core._t;


var CompanyPolicy = HrDashboard.include({
     events: {
        'click .hr_leave_request_approve': 'leaves_to_approve',
        'click .hr_leave_allocations_approve': 'leave_allocations_to_approve',
        'click .hr_timesheets': 'hr_timesheets',
        'click .hr_job_application_approve': 'job_applications_to_approve',
        'click .hr_payslip':'hr_payslip',
        'click .hr_contract':'hr_contract',
        'click .hr_employee':'hr_employee',
        'click .oe_company_policy': 'company_policy',
        'click .leaves_request_month':'leaves_request_month',
        'click .leaves_request_today':'leaves_request_today',
        "click .o_hr_attendance_sign_in_out_icon": function() {
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            this.update_attendance();
        },
        'click #broad_factor_pdf': 'generate_broad_factor_report',
    },

    company_policy: function(e){
//        returning company policy related field added wizard view.
        var self = this;
        self.do_action({
            name: _t("Company Policy"),
            type: 'ir.actions.act_window',
            res_model: 'res.company.policy',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                'default_company_id': session.company_id,
            },
            target: 'new'
        });


        },
});


});
