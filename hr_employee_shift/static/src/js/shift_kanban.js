/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ShiftKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    onGenerateSchedule() {
        this.actionService.doAction("hr_employee_shift.generate_schedule_action_window");
    }
}

export const shiftKanbanView = {
    ...kanbanView,
    Controller: ShiftKanbanController,
    buttonTemplate: "hr_employee_shift.ShiftKanbanView.Buttons",
};

registry.category("views").add("shift_kanban", shiftKanbanView);
