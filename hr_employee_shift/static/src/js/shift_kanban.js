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

ShiftKanbanController.template = "hr_employee_shift.ShiftKanbanView";

export const shiftKanbanView = {
    ...kanbanView,
    Controller: ShiftKanbanController,
};

registry.category("views").add("shift_kanban", shiftKanbanView);
