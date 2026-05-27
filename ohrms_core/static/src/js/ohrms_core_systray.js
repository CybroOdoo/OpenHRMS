/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { useService } from "@web/core/utils/hooks";

export class OhrmsCoreSystray extends Component {
    static template = "ohrms_core.OhrmsCoreSystray";
    static props = {};

    setup() {
        this.actionService = useService("action");
        useHotkey("alt+shift+h", () => this.openOhrmsCoreSupport(), {
            global: true,
        });
    }

    async openOhrmsCoreSupport() {
        return this.actionService.doAction({
            name: "Open HRMS Core Support",
            type: "ir.actions.act_window",
            res_model: "ohrms.core.support",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
        });
    }
}

registry.category("systray").add(
    "ohrms_core.OhrmsCoreSystray",
    { Component: OhrmsCoreSystray },
    { sequence: 100 }
);
