/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";

export class AnnouncementSystray extends Component {
    static components = { Dropdown };

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({ announcements: [] });

        onWillStart(async () => {
            await this.fetchAnnouncements();
        });
    }

    async fetchAnnouncements() {
        try {
            this.state.announcements = await this.orm.call("hr.announcement", "get_active_announcements", []);
        } catch (e) {
            console.error("Failed to fetch announcements:", e);
        }
    }

    openAnnouncement(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Announcement",
            res_model: "hr.announcement",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}
AnnouncementSystray.template = "hr_reward_warning.AnnouncementSystray";

// Register to the systray category
const systrayItem = {
    Component: AnnouncementSystray,
};
registry.category("systray").add("hr_reward_warning.AnnouncementSystray", systrayItem, { sequence: 50 });
