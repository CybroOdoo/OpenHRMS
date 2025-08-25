/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { HrDashboard } from "@hrms_dashboard/js/dashboard";
import { patch } from "@web/core/utils/patch";
/**
 * Adds a method to the HrDashboard to open the "Company Policy" form.
 * If no company policy is found for the user's company, it shows a message.
 * Otherwise, it opens the form view with the company policy data.
 */
patch(HrDashboard.prototype, {
     getCompanyPolicy() {
        this.action.doAction({
            name: _t("Company Policy"),
            type: 'ir.actions.act_window',
            res_model: 'res.company.policy',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                'default_company_id': session.user_companies.current_company,
            },
            target: 'new'
        })
     }
});
