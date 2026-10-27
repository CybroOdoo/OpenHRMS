/** @odoo-module **/

import { EmployeeFormController } from "@hr/views/form_view";
import { patch } from "@web/core/utils/patch";

patch(EmployeeFormController.prototype, {
    async onWillSaveRecord(record, changes) {
        if (Boolean(record?._config?.resId) && (!record._values?.employee_id || !record._values.employee_id.id)) {
            if (!record._values) {
                record._values = {};
            }
            record._values.employee_id = { id: record._config.resId || record.resId };
        }
        return super.onWillSaveRecord(...arguments);
    },
});
