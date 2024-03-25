/** @odoo-module */

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import framework from 'web.framework';
import session from 'web.session';


registry.category("ir.actions.report handlers").add('xlsx', async (action) => {

    if (action.report_type === 'wps_xlsx') {
        framework.blockUI();
        var def = $.Deferred();
        var dd = session.get_file({
            url: '/xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
            complete: framework.unblockUI,
        });
        return def;
    }
});

