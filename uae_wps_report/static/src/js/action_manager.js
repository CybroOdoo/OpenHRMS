/** @odoo-module */
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

/**
 * Report handler for UAE WPS XLSX reports in Odoo 20.
 */
registry.category("ir.actions.report handlers").add("wps_xlsx", async function (action, options, env) {
    if (action.report_type === 'wps_xlsx') {
        env.services.ui?.block();
        try {
            await download({
                url: '/xlsx_reports',
                data: action.data,
            });
        } finally {
            env.services.ui?.unblock();
        }
        return true;
    }
});
