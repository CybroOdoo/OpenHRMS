/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Component, proxy, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useDropdownState } from "@web/core/dropdown/dropdown_hooks";

class ReminderMenu extends Component {
    static components = { Dropdown };

//   Setup function which will run after the component is constructed
    setup(){
        this.action = useService("action");
        this.dropdown = useDropdownState();

        this.reminder = [];
        this.rpc = this.env.services.rpc
        this.state = proxy({
            all_remainders:[],
            isHRUser: false,
        })
        
        onWillStart(async () => {
            const data = await rpc("/hr_reminder/all_reminder");
            if (data && data.error === 'access_denied') {
                this.state.isHRUser = false;
            } else {
                this.state.isHRUser = true;
                this.state.all_remainders = data;
            }
        });
    }
//    Function to work when clicked on the reminder in systray
    async showReminder(ev){
        // Fetch again to ensure it's fresh when opened
        const data = await rpc("/hr_reminder/all_reminder");
        if (data && data.error === 'access_denied') {
            this.state.isHRUser = false;
        } else {
            this.state.isHRUser = true;
            this.state.all_remainders = data;
        }
    }
//    Function to work when clicked on the view button from systray
    async reminderActive(ev, reminderId, reminderName){
        if (ev && ev.stopPropagation) ev.stopPropagation();
        if (ev && ev.preventDefault) ev.preventDefault();
        
        const current = await rpc('/hr_reminder/reminder_active', {
            'reminder_id': reminderId,
            'reminder_name': reminderName
        });
        
        if (!current || current.length === 0) return;
        
        const action = {
            type: 'ir.actions.act_window',
            res_model: current[0],
            view_mode: 'list',
            views: [[false, 'list']],
            target: 'new',
            context: { create: false }
        };
        
        let domain = [];
        if (current[2] === 'today') {
            domain = [
                [current[1], '>=', `${current[7]} 00:00:00`],
                [current[1], '<=', `${current[7]} 23:59:59`]
            ];
        } else if (current[2] === 'set_date') {
            domain = [
                [current[1], '>=', `${current[10]} 00:00:00`],
                [current[1], '<=', `${current[3]} 23:59:59`]
            ];
        } else if (current[2] === 'set_period') {
            domain = [
                [current[1], '>=', `${current[4]} 00:00:00`],
                [current[1], '<=', `${current[5]} 23:59:59`]
            ];
        }
        
        // Close the dropdown after clicking View
        this.dropdown.close();
        
        return this.action.doAction({ ...action, domain });
    }
}
ReminderMenu.template = 'owl.reminder_menu'
const Systray = {
    Component: ReminderMenu,
}
registry.category("systray").add("reminder_menu", Systray)
