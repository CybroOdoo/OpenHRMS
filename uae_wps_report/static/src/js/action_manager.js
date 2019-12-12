odoo.define('scrap_move_report.action_manager', function (require) {
"use strict";

/**
 * The purpose of this file is to add the actions of type
 * 'ir_actions_xlsx_download' to the ActionManager.
 */

var ActionManager = require('web.ActionManager');
//var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var session = require('web.session');

ActionManager.include({

    /**
     * Executes actions of type 'ir_actions_xlsx_download'.
     *
     * @private
     * @param {Object} action the description of the action to execute
     * @returns {Deferred} resolved when the report has been downloaded ;
     *   rejected if an error occurred during the report generation
     */
    _executexlsxReportDownloadAction: function (action) {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    /**
     * Overrides to handle the 'ir_actions_xlsx_download' actions.
     *
     * @override
     * @private
     */
    _handleAction: function (action, options) {

        if (action.type === 'ir_actions_xlsx_download') {
            console.log("console")
            return this._executexlsxReportDownloadAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
});

});
