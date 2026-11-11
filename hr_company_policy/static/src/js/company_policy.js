/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";
import { HrDashboard } from "@hrms_dashboard/js/dashboard";
import { patch } from "@web/core/utils/patch";

/**
 * Adds a method to the HrDashboard to open the "Company Policy" popup.
 */
patch(HrDashboard.prototype, {
    getCompanyPolicy() {
        const companyId = user.activeCompany?.id || user.context.allowed_company_ids?.[0] || false;
        this.action.doAction({
            name: _t("Company Policy"),
            type: 'ir.actions.act_window',
            res_model: 'res.company.policy',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                'default_company_id': companyId,
            },
            target: 'new',
        });
    },
});
