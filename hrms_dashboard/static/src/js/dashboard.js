/** @odoo-module **/
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { onMounted, Component, useRef } from "@odoo/owl";
import { onWillStart, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";
import { user } from "@web/core/user";
const actionRegistry = registry.category("actions");
import { ActivityMenu } from "@hr_attendance/components/attendance_menu/attendance_menu";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
export class HrDashboard extends Component{
    static template = 'HrDashboardMain';
    static props = ["*"];
    setup() {
        this.effect = useService("effect");
        this.action = useService("action");
        this.log_in_out = useRef("log_in_out")
        this.emp_graph = useRef("emp_graph")
        this.leave_graph = useRef("leave_graph")
        this.join_resign_trend = useRef("join_resign_trend")
        this.attrition_rate = useRef("attrition_rate")
        this.leave_trend = useRef("leave_trend")
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            is_manager: false,
            date_range: localStorage.getItem('hrms_dashboard_date_range') || 'week',
            dashboards_templates: ['LoginEmployeeDetails','ManagerDashboard', 'EmployeeDashboard'],
            employee_birthday: [],
            upcoming_events: [],
            announcements: [],
            login_employee: [],
            templates: [],
            pending_approvals: [],
            expiring_documents: [],
            urgent_count: 0,
            activities: [],
            open_hrms_requests: {},
            checkin_time_str: '00:00:00',
            checkin_since_str: 'Tap to start your day',
            checkin_hm_str: '0h 0m',
            show_profile_dropdown: false,
            show_notifications_dropdown: false,
            show_date_dropdown: false,
            date_dropdown_view: 'list',
            custom_date_from: localStorage.getItem('hrms_dashboard_custom_from') || '',
            custom_date_to: localStorage.getItem('hrms_dashboard_custom_to') || '',
        })
        
        onMounted(() => {
            this.timerInterval = setInterval(() => {
                this.updateTimer();
            }, 1000);
        });
        
        onWillUnmount(() => {
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }
        });
        
        onWillStart(async () => {
            this.isHrManager = await user.hasGroup("hr.group_hr_manager");
            this.state.login_employee = {}
            if ( await this.orm.call('hr.employee', 'check_user_group', []) ) {
                this.state.is_manager = true
            }
            else {
                this.state.is_manager = false
            }
            await this.fetch_data();
            try {
                const oContent = document.querySelector('.o_content');
                if (oContent) {
                    oContent.style.setProperty('padding', '0', 'important');
                    oContent.style.setProperty('margin', '0', 'important');

                    let parent = oContent.parentElement;
                    while (parent && !parent.classList.contains('o_action_manager')) {
                        parent.style.setProperty('padding', '0', 'important');
                        parent.style.setProperty('margin', '0', 'important');
                        parent = parent.parentElement;
                    }

                    if (parent && parent.classList.contains('o_action_manager')) {
                        parent.style.setProperty('padding-left', '0', 'important');
                        parent.style.setProperty('padding-right', '0', 'important');
                        parent.style.setProperty('padding-bottom', '0', 'important');
                        parent.style.setProperty('padding-top', '0', 'important');
                    }
                }
            } catch (e) {
                console.error("Dashboard onWillStart DOM manipulation failed", e);
            }
        });
        onWillUnmount(() => {
            try {
                const oContent = document.querySelector('.o_content');
                if (oContent) {
                    oContent.style.removeProperty('padding');
                    oContent.style.removeProperty('margin');
                    oContent.style.removeProperty('overflow');
                }
            } catch (e) {
                console.error("Dashboard onWillUnmount DOM manipulation failed", e);
            }
        });
        onMounted(() => {
            this.title = 'Dashboard'
            this.render_graphs();
        });
    }
    add_project_task() {
            console.log("add_project_task:", user)
                this.action.doAction({
                    name: _t("Project Task"),
                    type: 'ir.actions.act_window',
                    res_model: 'project.task',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        'default_user_ids': [user.userId]
                    }
                });
            }
    view_project_tasks() {
                this.action.doAction({
                    name: _t("My Tasks"),
                    type: 'ir.actions.act_window',
                    res_model: 'project.task',
                    view_mode: 'tree,form,kanban',
                    views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                    domain: [['user_ids','in', user.userId]],
                    target: 'current'
                });
            }
    view_birthdays() {
        this.action.doAction({
            name: _t("Birthdays"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form,kanban',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
            domain: [['birthday', '!=', false]],
            target: 'current'
        });
    }
    view_event_record(ev) {
        let event_id = parseInt(ev.currentTarget.dataset.id);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'event.event',
            res_id: event_id,
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current'
        });
    }
    view_events() {
        let nowStr = new Date().toISOString().slice(0, 19).replace('T', ' ');
        this.action.doAction({
            name: _t("Upcoming Events"),
            type: 'ir.actions.act_window',
            res_model: 'event.event',
            view_mode: 'kanban,tree,form',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            domain: [['date_begin', '>=', nowStr]],
            target: 'current'
        });
    }
    view_announcements() {
        this.action.doAction({
            name: _t("Announcements"),
            type: 'ir.actions.act_window',
            res_model: 'hr.announcement',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'approved']],
            target: 'current'
        });
    }
    get pending_activities_count() {
        if (!this.state.activities) return 0;
        return this.state.activities.filter(a => !a.is_done).length;
    }

    view_reminders() {
        if (this.state.open_hrms_requests['hr_reminder'] === false) {
            this.notification.add(_t("The Reminders Todo module is not installed."), { type: 'warning' });
            return;
        }
        this.action.doAction('hr_reminder.hr_reminder_action');
    }
    view_activities() {
        this.action.doAction('project_todo.project_task_action_todo');
    }
    
    // Request Navigation Methods
    open_loan_requests() {
        if (this.state.open_hrms_requests['loan'] === false) {
            this.notification.add(_t("The Loan Management module is not installed."), { type: 'warning' });
            return;
        }
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['waiting_approval_1']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Loan Requests"),
            type: 'ir.actions.act_window',
            res_model: 'hr.loan',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
    open_salary_advance() {
        if (this.state.open_hrms_requests['salary_advance'] === false) {
            this.notification.add(_t("The Salary Advance module is not installed."), { type: 'warning' });
            return;
        }
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['submitted']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Salary Advance"),
            type: 'ir.actions.act_window',
            res_model: 'salary.advance',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
    open_resignations() {
        if (this.state.open_hrms_requests['resignation'] === false) {
            this.notification.add(_t("The Resignation module is not installed."), { type: 'warning' });
            return;
        }
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['confirm']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Resignations"),
            type: 'ir.actions.act_window',
            res_model: 'hr.resignation',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
    open_transfers() {
        if (this.state.open_hrms_requests['transfer'] === false) {
            this.notification.add(_t("The Employee Transfer module is not installed."), { type: 'warning' });
            return;
        }
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['transfer']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Branch Transfers"),
            type: 'ir.actions.act_window',
            res_model: 'employee.transfer',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
    open_service_requests() {
        if (this.state.open_hrms_requests['shift'] === false) {
            this.notification.add(_t("The Service Request module is not installed."), { type: 'warning' });
            return;
        }
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['requested']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Service Requests"),
            type: 'ir.actions.act_window',
            res_model: 'service.request',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current'
        });
    }

    
    async mark_activity_done(ev) {
        let type = ev.currentTarget.dataset.type;
        let activity_id = parseInt(ev.currentTarget.dataset.id);
        
        let item = this.state.activities.find(a => a.id === activity_id && a.type === type);
        if (!item) return;
        
        // Mark as done visually
        item.is_done = true;
        
        // Re-sort: unchecked first, checked at bottom
        this.state.activities.sort((a, b) => {
            if (a.is_done === b.is_done) return 0;
            return a.is_done ? 1 : -1;
        });
        
        // Backend update (non-blocking)
        if (type === 'todo') {
            this.orm.write('project.task', [activity_id], { 'state': '1_done' });
        }
        // If type === 'reminder', we don't update the backend because it's a global rule.
    }
    view_expiring_document(ev) {
        let doc_id = parseInt(ev.currentTarget.dataset.id);
        this.action.doAction({
            name: _t("Document"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee.document',
            res_id: doc_id,
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current'
        });
    }
    
    async send_document_reminder(ev) {
        ev.stopPropagation();
        let doc_id_str = ev.currentTarget.dataset.id;
        let result = false;
        
        if (doc_id_str.startsWith('emp_id_')) {
            let emp_id = parseInt(doc_id_str.replace('emp_id_', ''));
            result = await this.orm.call('hr.employee', 'action_send_manual_reminder_id', [[emp_id]]);
        } else if (doc_id_str.startsWith('emp_pass_')) {
            let emp_id = parseInt(doc_id_str.replace('emp_pass_', ''));
            result = await this.orm.call('hr.employee', 'action_send_manual_reminder_pass', [[emp_id]]);
        } else {
            let doc_id = parseInt(doc_id_str);
            result = await this.orm.call('hr.employee.document', 'action_send_manual_reminder', [[doc_id]]);
        }

        if (result) {
            this.showCustomToast(_t("Reminder sent successfully!").toString(), "success");
        } else {
            this.showCustomToast(_t("Failed to send reminder.").toString(), "danger");
        }
    }
    showCustomToast(message, type = "success") {
        let toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '24px';
        toast.style.right = '24px';
        toast.style.backgroundColor = '#ffffff';
        toast.style.padding = '12px 16px';
        toast.style.borderRadius = '12px';
        toast.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '12px';
        toast.style.zIndex = '9999';
        toast.style.transition = 'all 0.3s ease-in-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.border = '1px solid #e2e8f0';
        
        let iconHtml = '';
        if (type === 'success') {
            iconHtml = `<div style="width: 24px; height: 24px; border-radius: 50%; background-color: #dcfce7; color: #16a34a; display: flex; align-items: center; justify-content: center;"><i class="fa fa-check" style="font-size: 12px;"></i></div>`;
        } else {
            iconHtml = `<div style="width: 24px; height: 24px; border-radius: 50%; background-color: #fee2e2; color: #dc2626; display: flex; align-items: center; justify-content: center;"><i class="fa fa-times" style="font-size: 12px;"></i></div>`;
        }
        
        toast.innerHTML = `
            ${iconHtml}
            <span style="font-size: 14px; font-weight: 500; color: #1e293b;">${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    async approve_leave(ev) {
        let leave_id = parseInt(ev.currentTarget.dataset.id);
        await this.orm.call('hr.leave', 'action_approve', [[leave_id]]);
        // Filter it out from UI temporarily
        this.state.pending_approvals = this.state.pending_approvals.filter(l => l.id !== leave_id);
        this.showCustomToast("Leave request approved.", "success");
    }
    async reject_leave(ev) {
        let leave_id = parseInt(ev.currentTarget.dataset.id);
        await this.orm.call('hr.leave', 'action_refuse', [[leave_id]]);
        // Filter it out from UI temporarily
        this.state.pending_approvals = this.state.pending_approvals.filter(l => l.id !== leave_id);
        this.showCustomToast("Leave request rejected.", "danger");
    }
    render_graphs(){
        var self = this;
        if (this.state.login_employee){
            if (this.state.is_manager) {
             self.render_department_employee();
                self.render_leave_graph();
                self.update_join_resign_trends();
                self.update_monthly_attrition();
            }
            self.update_leave_trend();
            self.render_employee_skill();
        }
    }
    async render_department_employee() {
        let [dFrom, dTo] = this.getDateRange();
        const colors = [
            '#8b5cf6', '#1B5298', '#10b981', '#f59e0b', '#ef4444',
            '#6366f1', '#ec4899', '#14b8a6', '#f97316', '#06b6d4',
            '#84cc16', '#eab308'
        ];
        const data = await this.orm.call('hr.employee', 'get_dept_employee', [], { date_from: dFrom, date_to: dTo });
        if (data) {
            const labels = data.map(d => d.label);
            const values = data.map(d => d.value);
            let canvas_pieCtx = document.getElementById('employeePieChart');
        if (!canvas_pieCtx) return;
        if (this.employeePieChartInstance) {
            this.employeePieChartInstance.destroy();
        }
        const pieCtx = canvas_pieCtx.getContext('2d');
            
            // Chart.js v2 & v3 compatible center text plugin
            Chart.pluginService = Chart.pluginService || Chart.plugins;
            const centerTextPlugin = {
                id: 'centerText',
                beforeDraw: function(chart) {
                    var ctx = chart.ctx || chart.chart.ctx;
                    var width = chart.width || chart.chart.width;
                    var height = chart.height || chart.chart.height;
                    ctx.restore();
                    
                    let mainText, subText;
                    let hoveredIndex = chart.options && chart.options.hoveredIndex !== undefined ? chart.options.hoveredIndex : null;
                    if (hoveredIndex !== null) {
                        mainText = chart.data.datasets[0].data[hoveredIndex].toString();
                        subText = chart.data.labels[hoveredIndex];
                    } else {
                        mainText = chart.data.datasets[0].data.reduce((a, b) => a + b, 0).toString();
                        subText = "Employees";
                    }

                    var fontSize = (height / 100).toFixed(2);
                    ctx.font = "bold " + fontSize + "em sans-serif";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#1E293B";
                    var textX = Math.round((width - ctx.measureText(mainText).width) / 2),
                        textY = height / 2 - 10;
                    ctx.fillText(mainText, textX, textY);
                    
                    ctx.font = "600 " + (fontSize * 0.35).toFixed(2) + "em sans-serif";
                    ctx.fillStyle = "#64748B";
                    var text2X = Math.round((width - ctx.measureText(subText).width) / 2),
                        text2Y = height / 2 + 15;
                    ctx.fillText(subText, text2X, text2Y);
                    ctx.save();
                }
            };

            this.employeePieChartInstance = new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                        borderWidth: 0
                    }]
                },
                options: {
                    layout: { padding: 12 },
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    cutoutPercentage: 75, // For Chart.js v2
                    legend: { display: false }, // For Chart.js v2
                    onHover: function(event, elements, chartInstance) {
                        const chart = chartInstance || this;
                        if (chart && chart.options && chart.options.isLegendHover) return; // Prevent reset from legend hover
                        let activeIndex = null;
                        if (elements && elements.length > 0) {
                            activeIndex = elements[0].index !== undefined ? elements[0].index : elements[0]._index;
                        }
                        let currentHovered = chart && chart.options && chart.options.hoveredIndex !== undefined ? chart.options.hoveredIndex : null;
                        if (currentHovered !== activeIndex) {
                            if (chart) {
                                if (!chart.options) chart.options = {};
                                chart.options.hoveredIndex = activeIndex;
                                chart.update();
                            }
                            const legendContainer = document.getElementById('employeePieLegend');
                            if (legendContainer) {
                                const legendItems = legendContainer.querySelectorAll('.legend-item');
                                legendItems.forEach((item, idx) => {
                                    item.style.opacity = (activeIndex === null || idx === activeIndex) ? '1' : '0.4';
                                });
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }, // For Chart.js v3+
                        tooltip: {
                            callbacks: {
                                label: function (tooltipItem, data) {
                                    // Handle both v2 and v3 tooltip arguments
                                    let label, value;
                                    if (data) { // v2
                                        label = data.labels[tooltipItem.index] || '';
                                        value = data.datasets[0].data[tooltipItem.index] || 0;
                                    } else { // v3
                                        label = tooltipItem.label || '';
                                        value = tooltipItem.raw || 0;
                                    }
                                    const percentage = (value / values.reduce((a, b) => a + b, 0) * 100).toFixed(2);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    // Tooltip fallback for v2
                    tooltips: {
                        callbacks: {
                            label: function (tooltipItem, data) {
                                const label = data.labels[tooltipItem.index] || '';
                                const value = data.datasets[0].data[tooltipItem.index] || 0;
                                const percentage = (value / values.reduce((a, b) => a + b, 0) * 100).toFixed(2);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                plugins: [centerTextPlugin]
            });

            // Generate custom HTML legend
            const legendContainer = document.getElementById('employeePieLegend');
            if (legendContainer) {
                let legendHTML = '<div style="display: flex; flex-direction: column; gap: 12px; padding-left: 20px; padding-right: 20px;">';
                labels.forEach((label, i) => {
                    const color = colors[i % colors.length];
                    const val = values[i];
                    legendHTML += `
                        <div class="legend-item" data-index="${i}" style="display: flex; align-items: center; justify-content: space-between; font-size: 13px; cursor: pointer; transition: opacity 0.2s ease;">
                            <div style="display: flex; align-items: center;">
                                <span style="width: 10px; height: 10px; border-radius: 3px; background-color: ${color}; display: inline-block; margin-right: 12px;"></span>
                                <span style="color: #334155; font-weight: 500;">${label}</span>
                            </div>
                            <span style="color: #64748B; font-weight: 600;">${val}</span>
                        </div>
                    `;
                });
                legendHTML += '</div>';
                legendContainer.innerHTML = legendHTML;
                
                const legendItems = legendContainer.querySelectorAll('.legend-item');
                const comp = this;
                legendItems.forEach(item => {
                    item.addEventListener('mouseenter', function() {
                        const idx = parseInt(this.getAttribute('data-index'));
                        const chart = comp.employeePieChartInstance;
                        if (!chart) return;
                        if (!chart.options) chart.options = {};
                        chart.options.hoveredIndex = idx;
                        chart.options.isLegendHover = true;
                        
                        // In Chart.js v3+, we can programmatically hover the segment to make it "pop"
                        if (chart.setActiveElements) {
                            chart.setActiveElements([{datasetIndex: 0, index: idx}]);
                            chart.update();
                        } else {
                            // Chart.js v2 fallback for native pop expansion
                            const meta = chart.getDatasetMeta(0);
                            const arc = meta.data[idx];
                            if (arc) {
                                if (chart.updateHoverStyle) chart.updateHoverStyle([arc], null, true);
                                if (!arc._popped) {
                                    arc._model.outerRadius += 10;
                                    arc._view.outerRadius += 10;
                                    arc._popped = true;
                                }
                                chart.draw(); // draw instead of update to preserve hover styles
                            }
                        }
                        
                        legendItems.forEach((l, i) => {
                            l.style.opacity = i === idx ? '1' : '0.4';
                        });
                    });
                    item.addEventListener('mouseleave', function() {
                        const chart = comp.employeePieChartInstance;
                        if (!chart) return;
                        if (!chart.options) chart.options = {};
                        chart.options.hoveredIndex = null;
                        chart.options.isLegendHover = false;
                        
                        if (chart.setActiveElements) {
                            chart.setActiveElements([]);
                            chart.update();
                        } else {
                            const meta = chart.getDatasetMeta(0);
                            if (meta.data) {
                                meta.data.forEach(arc => {
                                    if (arc._popped) {
                                        arc._model.outerRadius -= 10;
                                        arc._view.outerRadius -= 10;
                                        arc._popped = false;
                                    }
                                });
                            }
                            if (chart.updateHoverStyle) chart.updateHoverStyle(meta.data, null, false);
                            chart.draw();
                        }
                        
                        legendItems.forEach(l => {
                            l.style.opacity = '1';
                        });
                    });
                });
            }
        }
    }
    async render_leave_graph() {
        let [dFrom, dTo] = this.getDateRange();
        const colors = [
            '#8b5cf6', '#f59e0b', '#1B5298', '#10b981', '#ef4444', '#6366f1',
            '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16',
            '#eab308', '#d946ef'
        ];
        const data = await this.orm.call('hr.employee', 'get_department_leave', [], { date_from: dFrom, date_to: dTo });
        const trendData = await this.orm.call('hr.employee', 'get_monthly_leave_status_trend', [], { date_from: dFrom, date_to: dTo });
        if (data && trendData) {
            const fData = data[0];
            const dept = data[1];
            fData.forEach(function (d) {
                let total = 0;
                for (const dpt in dept) {
                    total += d.leave[dept[dpt]];
                }
                d.total = total;
            });
            // Extract 3-letter month abbreviations (e.g., "Jan 2026" -> "Jan")
            const labels = trendData.map(d => d.l_month ? d.l_month.split(' ')[0] : d.l_month);
            
            // Use real backend data
            const approvedData = trendData.map(d => d.Approved);
            const pendingData = trendData.map(d => d.Pending);
            const rejectedData = trendData.map(d => d.Rejected);

            let canvas_barCtx = document.getElementById('leave_barChart');
        if (!canvas_barCtx) return;
        if (this.leaveBarChartInstance) {
            this.leaveBarChartInstance.destroy();
        }
        const barCtx = canvas_barCtx.getContext('2d');
            this.leaveBarChartInstance = new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Approved',
                            data: approvedData,
                            backgroundColor: '#8b5cf6',
                            barPercentage: 0.9,
                            categoryPercentage: 0.5
                        },
                        {
                            label: 'Pending',
                            data: pendingData,
                            backgroundColor: '#f59e0b',
                            barPercentage: 0.9,
                            categoryPercentage: 0.5
                        },
                        {
                            label: 'Rejected',
                            data: rejectedData,
                            backgroundColor: '#ef4444',
                            barPercentage: 0.9,
                            categoryPercentage: 0.5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: { // v2
                        display: true,
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 20,
                            fontColor: '#64748B'
                        }
                    },
                    plugins: { // v3
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                boxWidth: 8,
                                boxHeight: 8,
                                padding: 20,
                                color: '#64748B',
                                font: { size: 12, weight: '500' }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw}`;
                                }
                            }
                        }
                    },
                    scales: {
                        xAxes: [{
                            gridLines: { display: false, drawBorder: false },
                            ticks: { fontColor: '#64748B', fontSize: 12 }
                        }],
                        yAxes: [{
                            display: false,
                            gridLines: { display: false },
                            ticks: { display: false }
                        }],
                        x: { // v3
                            grid: { display: false, drawBorder: false },
                            ticks: { color: '#64748B', font: { size: 12 } },
                            border: { display: false }
                        },
                        y: { // v3
                            display: false,
                            grid: { display: false },
                            ticks: { display: false }
                        }
                    },
                    tooltips: { // v2
                        callbacks: {
                            label: function (tooltipItem, data) {
                                const st = fData[tooltipItem.index];
                                if(st && st.leave) {
                                    const nD = Object.keys(st.leave).map(key => ({
                                        type: key,
                                        leave: st.leave[key]
                                    }));
                                    updatePieChart(nD);
                                }
                                return `${data.datasets[tooltipItem.datasetIndex].label}: ${tooltipItem.yLabel}`;
                            }
                        }
                    }
                }
            });
             const pieData = dept.map(d => {
                let val = fData.reduce((acc, t) => acc + (t.leave[d] || 0), 0);
                return {
                    type: d,
                    leave: parseFloat(val.toFixed(2))
                };
            });
            let canvas_pieCtx = document.getElementById('leave_doughnutChart');
        if (!canvas_pieCtx) return;
        if (this.leaveDoughnutChartInstance) {
            this.leaveDoughnutChartInstance.destroy();
        }
        const pieCtx = canvas_pieCtx.getContext('2d');
            
            // Re-use centerTextPlugin from department employee
            Chart.pluginService = Chart.pluginService || Chart.plugins;
            const centerTextPlugin = {
                id: 'centerText2',
                beforeDraw: function(chart) {
                    var ctx = chart.ctx || chart.chart.ctx;
                    var width = chart.width || chart.chart.width;
                    var height = chart.height || chart.chart.height;
                    ctx.restore();
                    
                    let mainText, subText;
                    if (chart.hoveredIndex !== undefined && chart.hoveredIndex !== null) {
                        mainText = chart.data.datasets[0].data[chart.hoveredIndex].toString();
                        subText = chart.data.labels[chart.hoveredIndex];
                    } else {
                        let sum = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        mainText = parseFloat(sum.toFixed(2)).toString();
                        subText = "of leaves";
                    }

                    var fontSize = (height / 100).toFixed(2);
                    ctx.font = "bold " + fontSize + "em sans-serif";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#1E293B";
                    var textX = Math.round((width - ctx.measureText(mainText).width) / 2),
                        textY = height / 2 - 10;
                    ctx.fillText(mainText, textX, textY);
                    
                    ctx.font = "600 " + (fontSize * 0.35).toFixed(2) + "em sans-serif";
                    ctx.fillStyle = "#64748B";
                    var text2X = Math.round((width - ctx.measureText(subText).width) / 2),
                        text2Y = height / 2 + 15;
                    ctx.fillText(subText, text2X, text2Y);
                    ctx.save();
                }
            };

            this.leaveDoughnutChartInstance = new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: pieData.map(d => d.type),
                    datasets: [{
                        data: pieData.map(d => d.leave),
                        backgroundColor: colors,
                        borderWidth: 0
                    }]
                },
                options: {
                    layout: { padding: 12 },
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    cutoutPercentage: 75,
                    legend: { display: false },
                    onHover: function(event, elements, chartInstance) {
                        const chart = chartInstance || this;
                        if (chart && chart.options && chart.options.isLegendHover) return;
                        let activeIndex = null;
                        if (elements && elements.length > 0) {
                            activeIndex = elements[0].index !== undefined ? elements[0].index : elements[0]._index;
                        }
                        let currentHovered = chart && chart.options && chart.options.hoveredIndex !== undefined ? chart.options.hoveredIndex : null;
                        if (currentHovered !== activeIndex) {
                            if (chart) {
                                if (!chart.options) chart.options = {};
                                chart.options.hoveredIndex = activeIndex;
                                chart.update();
                            }
                            const legendContainer = document.getElementById('leaveDoughnutLegend');
                            if (legendContainer) {
                                const legendItems = legendContainer.querySelectorAll('.legend-item');
                                legendItems.forEach((item, idx) => {
                                    item.style.opacity = (activeIndex === null || idx === activeIndex) ? '1' : '0.4';
                                });
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    let label, value;
                                    if (context.labels) { // v2
                                        label = pieData[context.index].type;
                                        value = pieData[context.index].leave;
                                    } else { // v3
                                        label = context.label || '';
                                        value = context.raw || 0;
                                    }
                                    const percentage = (value / pieData.reduce((acc, d) => acc + d.leave, 0) * 100).toFixed(2);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    tooltips: {
                        callbacks: {
                            label: function (tooltipItem, data) {
                                const label = pieData[tooltipItem.index].type;
                                const value = pieData[tooltipItem.index].leave;
                                const percentage = (value / pieData.reduce((acc, d) => acc + d.leave, 0) * 100).toFixed(2);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                plugins: [centerTextPlugin]
            });
            const pieChart = this.leaveDoughnutChartInstance;
            function updatePieChart(newData) {
                pieChart.data.datasets[0].data = newData.map(d => d.leave);
                pieChart.data.labels = newData.map(d => d.type);
                pieChart.update();
            }

            // Generate custom HTML legend
            const legendContainer = document.getElementById('leaveDoughnutLegend');
            if (legendContainer) {
                let legendHTML = '<div style="display: flex; flex-direction: column; gap: 12px; padding-left: 20px; padding-right: 20px;">';
                pieData.forEach((d, i) => {
                    const color = colors[i % colors.length];
                    const val = d.leave;
                    legendHTML += `
                        <div class="legend-item" data-index="${i}" style="display: flex; align-items: center; justify-content: space-between; font-size: 13px; cursor: pointer; transition: opacity 0.2s ease;">
                            <div style="display: flex; align-items: center;">
                                <span style="width: 10px; height: 10px; border-radius: 3px; background-color: ${color}; display: inline-block; margin-right: 12px;"></span>
                                <span style="color: #334155; font-weight: 500;">${d.type}</span>
                            </div>
                            <span style="color: #64748B; font-weight: 600;">${val}</span>
                        </div>
                    `;
                });
                legendHTML += '</div>';
                legendContainer.innerHTML = legendHTML;
                
                const legendItems = legendContainer.querySelectorAll('.legend-item');
                const comp = this;
                legendItems.forEach(item => {
                    item.addEventListener('mouseenter', function() {
                        const idx = parseInt(this.getAttribute('data-index'));
                        const chart = comp.leaveDoughnutChartInstance;
                        if (!chart) return;
                        if (!chart.options) chart.options = {};
                        chart.options.hoveredIndex = idx;
                        chart.options.isLegendHover = true;
                        
                        if (chart.setActiveElements) {
                            chart.setActiveElements([{datasetIndex: 0, index: idx}]);
                            chart.update();
                        } else {
                            const meta = chart.getDatasetMeta(0);
                            const arc = meta.data[idx];
                            if (arc) {
                                if (chart.updateHoverStyle) chart.updateHoverStyle([arc], null, true);
                                if (!arc._popped) {
                                    arc._model.outerRadius += 10;
                                    arc._view.outerRadius += 10;
                                    arc._popped = true;
                                }
                                chart.draw();
                            }
                        }
                        
                        legendItems.forEach((l, i) => {
                            l.style.opacity = i === idx ? '1' : '0.4';
                        });
                    });
                    item.addEventListener('mouseleave', function() {
                        const chart = comp.leaveDoughnutChartInstance;
                        if (!chart) return;
                        if (!chart.options) chart.options = {};
                        chart.options.hoveredIndex = null;
                        chart.options.isLegendHover = false;
                        
                        if (chart.setActiveElements) {
                            chart.setActiveElements([]);
                            chart.update();
                        } else {
                            const meta = chart.getDatasetMeta(0);
                            if (meta.data) {
                                meta.data.forEach(arc => {
                                    if (arc._popped) {
                                        arc._model.outerRadius -= 10;
                                        arc._view.outerRadius -= 10;
                                        arc._popped = false;
                                    }
                                });
                            }
                            if (chart.updateHoverStyle) chart.updateHoverStyle(meta.data, null, false);
                            chart.draw();
                        }
                        
                        legendItems.forEach(l => {
                            l.style.opacity = '1';
                        });
                    });
                });
            }
        }
    }
    async update_join_resign_trends() {
        let [dFrom, dTo] = this.getDateRange();
        const colors = ['#10b981', '#ef4444', '#1B5298', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#eab308', '#d946ef'];
        const data = await this.orm.call('hr.employee', 'join_resign_trends', [], { date_from: dFrom, date_to: dTo });
        if (data) {
            const labels = data[0].values.map(d => d.l_month.substring(0, 3)); // Use short month names
            const datasets = data.map((dataset, index) => {
                const isJoin = dataset.name.toLowerCase().includes('join');
                const isResign = dataset.name.toLowerCase().includes('resign');
                const lineColor = isJoin ? '#10b981' : (isResign ? '#ef4444' : colors[index % colors.length]);
                const labelName = isJoin ? 'Joined' : (isResign ? 'Resigned' : dataset.name);
                
                return {
                    label: labelName,
                    data: dataset.values.map(d => d.count),
                    borderColor: lineColor,
                    backgroundColor: '#ffffff',
                    fill: false,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointBorderColor: lineColor,
                    pointHoverRadius: 6
                };
            });
            let canvas_ctx = document.getElementById('lineChart');
        if (!canvas_ctx) return;
        if (this.lineChartInstance) {
            this.lineChartInstance.destroy();
        }
        const ctx = canvas_ctx.getContext('2d');
            this.lineChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false } // Chart.js 3+
                    },
                    legend: { display: false }, // Chart.js 2
                    scales: {
                        xAxes: [{
                            display: true,
                            gridLines: { display: false, drawBorder: false },
                            ticks: { fontColor: '#94a3b8', fontSize: 12 }
                        }],
                        yAxes: [{
                            display: true,
                            ticks: { beginAtZero: true, display: false },
                            gridLines: { color: '#f1f5f9', borderDash: [5, 5], drawBorder: false, drawTicks: false }
                        }],
                        x: {
                            display: true,
                            grid: { display: false, drawBorder: false },
                            ticks: {
                                color: '#94a3b8',
                                font: { size: 12 }
                            },
                            border: { display: false }
                        },
                        y: {
                            display: true,
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9',
                                borderDash: [5, 5],
                                drawBorder: false,
                                tickLength: 0
                            },
                            ticks: { display: false },
                            border: { display: false }
                        }
                    }
                }
            });

            // Generate custom legend
            const legendContainer = document.getElementById('joinResignLegend');
            if (legendContainer) {
                let legendHTML = '';
                datasets.forEach(ds => {
                    legendHTML += `
                        <div style="display: flex; align-items: center;">
                            <span style="width: 12px; height: 3px; background-color: ${ds.borderColor}; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
                            <span>${ds.label}</span>
                        </div>
                    `;
                });
                legendContainer.innerHTML = legendHTML;
            }
        }
    }
    async update_monthly_attrition() {
        let [dFrom, dTo] = this.getDateRange();
        const colors = ['#10b981', '#1B5298', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#eab308', '#d946ef'];
        const data = await this.orm.call('hr.employee', 'get_attrition_rate', [], { date_from: dFrom, date_to: dTo });
        if (data && data.length > 0) {
            // Reverse the data to show oldest month on the left, newest on the right
            data.reverse();
            
            // Get the most recent attrition rate
            const latestAttrition = data[data.length - 1].attrition_rate;
            const avgAttrition = (data.reduce((a, b) => a + b.attrition_rate, 0) / data.length).toFixed(1);
            
            // Update badges
            const latestMonth = data[data.length - 1].month.substring(0, 3);
            const attrTextEl = document.getElementById('attritionRateText');
            if (attrTextEl) attrTextEl.innerText = `${latestMonth} Attrition: ${latestAttrition}%`;
            
            const avgAttrTextEl = document.getElementById('avgAttritionRateText');
            if (avgAttrTextEl) avgAttrTextEl.innerText = `Avg ${avgAttrition}%`;

            const labels = data.map(d => d.month.substring(0, 3)); // short month
            const attritionData = data.map(d => d.attrition_rate);
            
            let canvas_ctx = document.getElementById('attritionRateChart');
        if (!canvas_ctx) return;
        if (this.attritionRateChartInstance) {
            this.attritionRateChartInstance.destroy();
        }
        const ctx = canvas_ctx.getContext('2d');
            this.attritionRateChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Attrition Rate',
                        data: attritionData,
                        borderColor: colors[0],
                        backgroundColor: '#ffffff',
                        fill: false,
                        cubicInterpolationMode: 'monotone',
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointBorderColor: colors[0],
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    legend: { display: false },
                    scales: {
                        xAxes: [{
                            display: true,
                            gridLines: { display: false, drawBorder: false },
                            ticks: { fontColor: '#94a3b8', fontSize: 12 }
                        }],
                        yAxes: [{
                            display: true,
                            ticks: { beginAtZero: true, display: false },
                            gridLines: { color: '#f1f5f9', borderDash: [5, 5], drawBorder: false, drawTicks: false }
                        }],
                        x: {
                            display: true,
                            grid: { display: false, drawBorder: false },
                            ticks: { color: '#94a3b8', font: { size: 12 } },
                            border: { display: false }
                        },
                        y: {
                            display: true,
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9',
                                borderDash: [5, 5],
                                drawBorder: false,
                                tickLength: 0
                            },
                            ticks: { display: false },
                            border: { display: false }
                        }
                    }
                }
            });

            const legendContainer = document.getElementById('attritionLegend');
            if (legendContainer) {
                legendContainer.innerHTML = `
                    <div style="display: flex; align-items: center;">
                        <span style="width: 12px; height: 3px; background-color: ${colors[0]}; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
                        <span>Attrition Rate</span>
                    </div>
                `;
            }
        }
    }
    async update_leave_trend() {
        let [dFrom, dTo] = this.getDateRange();
        const data = await this.orm.call('hr.employee', 'employee_attendance_trend', [], { date_from: dFrom, date_to: dTo });
        if (data) {
            const labels = data.map(d => d.l_month);
            const leaveData = data.map(d => d.attendance);
            let canvas_ctx = document.getElementById('leaveTrendChart');
        if (!canvas_ctx) return;
        if (this.leaveTrendChartInstance) {
            this.leaveTrendChartInstance.destroy();
        }
        const ctx = canvas_ctx.getContext('2d');
            
            // Create vibrant gradient fill matching reference
            const gradient = ctx.createLinearGradient(0, 0, 0, 250);
            gradient.addColorStop(0, 'rgba(27, 82, 152, 0.4)');
            gradient.addColorStop(1, 'rgba(27, 82, 152, 0.0)');

            this.leaveTrendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Attendance',
                        data: leaveData,
                        backgroundColor: gradient,
                        borderColor: '#1B5298',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#1B5298',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 7,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            bottom: 24
                        }
                    },
                    legend: { display: false },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `Attendance: ${context.raw}`;
                                }
                            }
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            gridLines: { display: false, drawBorder: false },
                            ticks: { fontColor: '#94a3b8', fontSize: 12 }
                        }],
                        yAxes: [{
                            display: true,
                            ticks: { beginAtZero: true, display: false },
                            gridLines: { color: '#f1f5f9', borderDash: [5, 5], drawBorder: false, drawTicks: false }
                        }],
                        x: {
                            display: true,
                            grid: { display: false, drawBorder: false },
                            ticks: {
                                color: '#94a3b8',
                                font: { size: 12 }
                            },
                            border: { display: false }
                        },
                        y: {
                            display: true,
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9',
                                borderDash: [5, 5],
                                drawBorder: false,
                                tickLength: 0
                            },
                            ticks: {
                                display: false
                            },
                            border: { display: false }
                        }
                    }
                }
            });
        }
    }

    async render_employee_skill() {
        let [dFrom, dTo] = this.getDateRange();
        const colors = ['#8b5cf6', '#1B5298', '#10b981', '#f59e0b', '#ef4444', '#6366f1', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#eab308', '#d946ef'];
        const data = await this.orm.call('hr.employee', 'get_employee_skill', [], { date_from: dFrom, date_to: dTo });
        if (data) {
            const labels = data.map(d => d.skills);
            const skillData = data.map(d => d.progress);
            const canvas = document.getElementById('skillChart');
            if (!canvas) return;
            if (this.skillChartInstance) {
                this.skillChartInstance.destroy();
            }
            const ctx = canvas.getContext('2d');
            this.skillChartInstance = new Chart(ctx, {
                type: 'polarArea',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Skill ',
                        data: skillData,
                        backgroundColor: colors,
                        borderColor: ['white'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `Skill: ${context.raw}`;
                                }
                            }
                        },
                        legend: {
                            display: true,
                            position: 'right',
                            labels: {
                                color: 'black'
                            }
                        }
                    },
                   scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
            });
        }
    }
    // EVENT METHODS
    updateTimer() {
        if (this.state.login_employee && this.state.login_employee.attendance_state === 'checked_in' && this.state.login_employee.last_check_in) {
            let checkInDate = new Date(this.state.login_employee.last_check_in.replace(' ', 'T') + 'Z');
            let now = new Date();
            let diffMs = now - checkInDate;
            if (diffMs > 0) {
                let diffSecs = Math.floor(diffMs / 1000);
                let hours = Math.floor(diffSecs / 3600);
                let mins = Math.floor((diffSecs % 3600) / 60);
                let secs = diffSecs % 60;
                this.state.checkin_time_str = 
                    String(hours).padStart(2, '0') + ':' + 
                    String(mins).padStart(2, '0') + ':' + 
                    String(secs).padStart(2, '0');
                
                // Format "Since 09:02 AM today"
                let cHours = checkInDate.getHours();
                let cMins = String(checkInDate.getMinutes()).padStart(2, '0');
                let ampm = cHours >= 12 ? 'PM' : 'AM';
                cHours = cHours % 12;
                cHours = cHours ? cHours : 12;
                this.state.checkin_since_str = `Since ${String(cHours).padStart(2, '0')}:${cMins} ${ampm} today`;
                this.state.checkin_hm_str = `${hours}h ${mins}m`;
            } else {
                this.state.checkin_time_str = '00:00:00';
                this.state.checkin_since_str = 'Tap to start your day';
                this.state.checkin_hm_str = '0h 0m';
            }
        } else {
            this.state.checkin_time_str = '00:00:00';
            this.state.checkin_since_str = 'Tap to start your day';
            this.state.checkin_hm_str = '0h 0m';
        }
    }

    export_dashboard_pdf(ev) {
        window.print();
    }

    add_attendance() {
        this.action.doAction({
            name: _t("Attendances"),
            type: 'ir.actions.act_window',
            res_model: 'hr.attendance',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }
    add_leave() {
        this.action.doAction({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }
    add_leave() {
        this.action.doAction({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }

    add_expense() {
        this.action.doAction({
            name: _t("Expense"),
            type: 'ir.actions.act_window',
            res_model: 'hr.expense',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }
    leaves_to_approve() {
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state','in',['confirm','validate1']]];
        if (dFrom) domain.push(['request_date_from', '>=', dFrom]);
        if (dTo) domain.push(['request_date_from', '<=', dTo]);
        this.action.doAction({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
    leave_allocations_to_approve() {
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state','in',['confirm', 'validate1']]];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Leave Allocation Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave.allocation',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: domain,
            target: 'current'
        })
    }
    job_applications_to_approve(){
        let [dFrom, dTo] = this.getDateRange();
        let domain = [];
        if (dFrom) domain.push(['create_date', '>=', dFrom]);
        if (dTo) domain.push(['create_date', '<=', dTo + ' 23:59:59']);
        this.action.doAction({
            name: _t("Applications"),
            type: 'ir.actions.act_window',
            res_model: 'hr.applicant',
            view_mode: 'tree,kanban,form,pivot,graph,calendar',
            views: [[false, 'list'],[false, 'kanban'],[false, 'form'],
                    [false, 'pivot'],[false, 'graph'],[false, 'calendar']],
            domain: domain,
            context: {},
            target: 'current'
        })
    }
    leaves_request_today() {
        var date = new Date();
        this.action.doAction({
            name: _t("Leaves Today"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['date_from','<=', date], ['date_to', '>=', date], ['state','=','validate']],
            target: 'current'
        })
    }
    leaves_request_month() {
        var date = new Date();
        var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        var fday = firstDay.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        this.action.doAction({
            name: _t("This Month Leaves"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['date_from','>', fday],['state','=','validate'],['date_from','<', lday]],
            target: 'current'
        })
    }
    hr_payslip() {
        let domain = [];
        if (!this.state.is_manager) {
            domain.push(['employee_id','=', this.state.login_employee.id]);
        }
        let [dFrom, dTo] = this.getDateRange();
        if (dFrom) {
            domain.push(['date_to', '>=', dFrom]);
        }
        if (dTo) {
            domain.push(['date_from', '<=', dTo]);
        }
        this.action.doAction({
            name: _t("Employee Payslips"),
            type: 'ir.actions.act_window',
            res_model: 'hr.payslip',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: domain,
            target: 'current'
        });
    }
   async hr_contract() {
        console.log("this:", this)
        if (true) {

            // Call the Python function to get the view ID
            const view_id = await this.orm.call(
                'hr.version',
                'get_hr_version_list_view_id',
                []
            );
            this.action.doAction({
                name: _t("Contracts"),
                type: 'ir.actions.act_window',
                res_model: 'hr.version',
                view_mode: 'tree,form,graph,pivot',
                views: [
                    [view_id, 'list'],
                    [false, 'graph'],
                    [false, 'pivot'],
                ],
                context: {},
                domain: (function() {
                    let [dFrom, dTo] = this.getDateRange();
                    var t = new Date();
                    var today = t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0');
                    var filter_start = dTo || today;
                    var filter_end = dFrom || today;
                    
                    var dom = ['&', ['date_start', '<=', filter_start], '|', ['date_end', '=', false], ['date_end', '>=', filter_end]];
                    if (!this.state.is_manager) {
                        dom.unshift('&'); // Add another AND for the employee_id
                        dom.push(['employee_id', '=', this.state.login_employee.id]);
                    }
                    return dom;
                }).bind(this)(),
                target: 'current'
            });
        }
   }

    hr_timesheets() {
        let [dFrom, dTo] = this.getDateRange();
        let domainStr = `[('project_id', '!=', False)`;
        if (!this.state.is_manager) {
            domainStr += `, ('employee_id', '=', ${this.state.login_employee.id})`;
            domainStr += `, ('task_id.user_ids', 'in', ${user.userId})`;
        }
        if (dFrom) {
            domainStr += `, ('date', '>=', '${dFrom}')`;
        }
        if (dTo) {
            domainStr += `, ('date', '<=', '${dTo}')`;
        }
        domainStr += `]`;
        this.action.doAction({
            name: _t("Timesheets"),
            type: 'ir.actions.act_window',
            res_model: 'account.analytic.line',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            context: {},
            domain: domainStr,
            target: 'current'
        })
    }
    employee_broad_factor() {
        let [dFrom, dTo] = this.getDateRange();
        let domain = [['state', 'in', ['validate']]];
        
        if (dFrom) {
            domain.push(['date_from', '>=', dFrom]);
        }
        if (dTo) {
            domain.push(['date_to', '<=', dTo]);
        } else {
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();
            var todayStr = yyyy + '-' + mm + '-' + dd;
            domain.push(['date_to', '<=', todayStr]);
        }

        if (!this.state.is_manager) {
            domain.push(['employee_id', '=', this.state.login_employee.id]);
        }
        this.action.doAction({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: domain,
            target: 'current',
            context:{'order':'duration_display'}
        })
    }
    async attendance_sign_in_out() {
        try {
            var result = await this.orm.call('hr.employee', 'attendance_manual', [[this.state.login_employee.id]]);
            if (result) {
                if (this.state.login_employee['attendance_state'] == 'checked_out') {
                    this.state.login_employee['attendance_state'] = 'checked_in';
                    this.state.login_employee['last_check_in'] = new Date().toISOString().replace('T', ' ').substring(0, 19);
                    this.env.bus.trigger('signin_signout', { mode: "checked_in" });
                    this.showCustomToast(_t("Successfully Checked In").toString(), "success");
                } else {
                    if (this.state.login_employee['attendance_state'] == 'checked_in') {
                        this.state.login_employee['attendance_state'] = 'checked_out';
                        this.env.bus.trigger('signin_signout', { mode: false });
                        this.showCustomToast(_t("Successfully Checked Out").toString(), "success");
                    }
                }
                this.updateTimer();
            }
        } catch (e) {
            // We MUST re-throw the error. If we swallow it, Odoo will not
            // show the Validation Error dialog to the user.
            // This will result in an "Uncaught (in promise)" red error in the console,
            // but that is completely normal and expected in Odoo.
            throw e;
        }
    }

    // --- Profile Dropdown Actions ---
    toggleNotificationsDropdown() {
        this.state.show_notifications_dropdown = !this.state.show_notifications_dropdown;
        if (this.state.show_notifications_dropdown) {
            this.state.show_profile_dropdown = false; // close the other dropdown
        }
    }
    closeNotificationsDropdown() {
        this.state.show_notifications_dropdown = false;
    }
    toggleProfileDropdown() {
        this.state.show_profile_dropdown = !this.state.show_profile_dropdown;
        if (this.state.show_profile_dropdown) {
            this.state.show_notifications_dropdown = false; // close the other dropdown
        }
    }
    
    closeProfileDropdown() {
        this.state.show_profile_dropdown = false;
    }
    
    action_my_profile() {
        this.closeProfileDropdown();
        if (this.state.login_employee && this.state.login_employee.id) {
            this.action.doAction({
                type: 'ir.actions.act_window',
                name: _t('My Profile'),
                res_model: 'hr.employee',
                res_id: this.state.login_employee.id,
                views: [[false, 'form']],
                target: 'current'
            });
        }
    }
    
    action_my_payslips() {
        this.closeProfileDropdown();
        if (this.state.login_employee && this.state.login_employee.id) {
            this.action.doAction({
                type: 'ir.actions.act_window',
                name: _t('My Payslips'),
                res_model: 'hr.payslip',
                views: [[false, 'list'], [false, 'form']],
                domain: [['employee_id', '=', this.state.login_employee.id]],
                target: 'current'
            });
        }
    }
    
    action_preferences() {
        this.closeProfileDropdown();
        this.action.doAction('base.action_res_users_my');
    }
    
    action_sign_out() {
        window.location.href = '/web/session/logout';
    }
    
    // --- Date Filter Dropdown Actions ---
    toggleDateDropdown() {
        this.state.show_date_dropdown = !this.state.show_date_dropdown;
        if (this.state.show_date_dropdown) {
            this.state.date_dropdown_view = 'list';
        }
    }
    
    closeDateDropdown() {
        this.state.show_date_dropdown = false;
        this.state.date_dropdown_view = 'list';
    }
    
    setDateFilter(range) {
        if (range === 'custom_trigger') {
            this.state.date_dropdown_view = 'custom';
            return;
        }
        this.state.date_range = range;
        localStorage.setItem('hrms_dashboard_date_range', range);
        this.closeDateDropdown();
        this.fetch_data();
    }
    
    applyCustomDateFilter() {
        if (!this.state.custom_date_from || !this.state.custom_date_to) {
            return; // Simple validation
        }
        this.state.date_range = 'custom';
        localStorage.setItem('hrms_dashboard_date_range', 'custom');
        localStorage.setItem('hrms_dashboard_custom_from', this.state.custom_date_from);
        localStorage.setItem('hrms_dashboard_custom_to', this.state.custom_date_to);
        this.closeDateDropdown();
        this.fetch_data();
    }
    
    backToDateList() {
        this.state.date_dropdown_view = 'list';
    }

    getDateRange() {
        let fromDate = null;
        let toDate = null;
        let now = new Date();
        
        const formatDate = (date) => {
            const yyyy = date.getFullYear();
            const mm = String(date.getMonth() + 1).padStart(2, '0');
            const dd = String(date.getDate()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd}`;
        };
        
        if (this.state.date_range === 'today') {
            fromDate = formatDate(now);
            toDate = formatDate(now);
        } else if (this.state.date_range === 'week') {
            let first = now.getDate() - now.getDay();
            let last = first + 6;
            let d1 = new Date(new Date().setDate(first));
            let d2 = new Date(new Date().setDate(last));
            fromDate = formatDate(d1);
            toDate = formatDate(d2);
        } else if (this.state.date_range === 'month') {
            fromDate = formatDate(new Date(now.getFullYear(), now.getMonth(), 1));
            toDate = formatDate(new Date(now.getFullYear(), now.getMonth() + 1, 0));
        } else if (this.state.date_range === 'quarter') {
            let quarter = Math.floor((now.getMonth() / 3));
            fromDate = formatDate(new Date(now.getFullYear(), quarter * 3, 1));
            toDate = formatDate(new Date(now.getFullYear(), quarter * 3 + 3, 0));
        } else if (this.state.date_range === 'year') {
            fromDate = formatDate(new Date(now.getFullYear(), 0, 1));
            toDate = formatDate(new Date(now.getFullYear(), 11, 31));
        } else if (this.state.date_range === 'custom') {
            fromDate = this.state.custom_date_from;
            toDate = this.state.custom_date_to;
        }
        return [fromDate, toDate];
    }
    
    async fetch_data() {
        let [dFrom, dTo] = this.getDateRange();
        var empDetails = await this.orm.call('hr.employee', 'get_user_employee_details', [], { date_from: dFrom, date_to: dTo })
        if ( empDetails ){
            this.state.login_employee = empDetails[0];
        }
        
        // Fetch Open HRMS Requests
        this.state.open_hrms_requests = await this.orm.call('hr.employee', 'get_open_hrms_requests', [], { date_from: dFrom, date_to: dTo });
        
        var res = await this.orm.call('hr.employee', 'get_upcoming', [], { date_from: dFrom, date_to: dTo })
        if ( res ) {
            // Process Upcoming Events
            if (res['event'] && res['event'].length > 0) {
                const eventMonthNames = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
                this.state.upcoming_events = res['event'].slice(0, 4).map((e, index) => {
                let dateObj = new Date(e.date_begin.replace(' ', 'T') + 'Z');
                let monthStr = eventMonthNames[dateObj.getMonth()];
                let dayStr = String(dateObj.getDate()).padStart(2, '0');
                let yearStr = dateObj.getFullYear();
                
                let hours = dateObj.getHours();
                let minutes = String(dateObj.getMinutes()).padStart(2, '0');
                let ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12;
                let timeStr = hours + ':' + minutes + ' ' + ampm;
                
                const colors = ['#1B5298', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
                let iconColor = colors[index % colors.length];

                return {
                    ...e,
                    event_month: monthStr,
                    event_day: dayStr,
                    event_year: yearStr,
                    event_time: timeStr,
                    icon_color: iconColor
                };
                });
            } else {
                this.state.upcoming_events = [];
            }
            
            // Process Announcements
            if (res['announcement'] && res['announcement'].length > 0) {
                const annIds = res['announcement'].map(a => a.id);
                let annDetails = await this.orm.searchRead('hr.announcement', [['id', 'in', annIds]], ['id', 'create_date', 'create_uid']);
                let annMap = {};
                annDetails.forEach(d => annMap[d.id] = d);
                
                let now = new Date();
                
                this.state.announcements = res['announcement'].map(a => {
                let detail = annMap[a.id];
                let author = detail && detail.create_uid ? detail.create_uid[1] : 'HR Team';
                // Clean author name if it's a long internal name
                if (author && author.includes('OdooBot')) author = 'System';
                else if (author && author.includes('Administrator')) author = 'HR Team';
                
                let cDate = detail && detail.create_date ? new Date(detail.create_date + 'Z') : new Date(a.date_start);
                
                let diffMs = now - cDate;
                let diffMins = Math.floor(diffMs / 60000);
                let diffHours = Math.floor(diffMs / 3600000);
                let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                
                let timeAgo = '';
                if (diffMins < 60) {
                    timeAgo = diffMins <= 0 ? 'Just now' : `${diffMins}m ago`;
                } else if (diffHours < 24) {
                    timeAgo = `${diffHours}h ago`;
                } else if (diffDays === 1) {
                    timeAgo = 'Yesterday';
                } else {
                    timeAgo = `${diffDays} days ago`;
                }
                
                return {
                    ...a,
                    author: author,
                    time_ago: timeAgo
                };
                });
            } else {
                this.state.announcements = [];
            }
            
            // Process Birthdays
            if (res['birthday'] && res['birthday'].length > 0) {
                const bdayIds = res['birthday'].map(b => b.id);
                const bdayColors = ['#1B5298', '#ec4899', '#0ea5e9', '#8b5cf6', '#14b8a6', '#f59e0b'];
                const bdayMonthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                
                // Department is now provided by the backend 'get_upcoming'
                let deptMap = {};
                res['birthday'].forEach(d => deptMap[d.id] = d.department_id ? d.department_id[1] : 'Employee');
                
                this.state.employee_birthday = res['birthday'].map((b, i) => {
                let initials = b.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                let color = bdayColors[i % bdayColors.length];
                
                let dateStr = '';
                if (b.is_birthday) {
                    dateStr = 'Today';
                } else if (b.days === 1) {
                    dateStr = 'Tomorrow';
                } else {
                    let dateObj = new Date(b.birthday);
                    dateStr = bdayMonthNames[dateObj.getMonth()] + ' ' + String(dateObj.getDate()).padStart(2, '0');
                }
                
                return {
                    ...b,
                    initials: initials,
                    color: color,
                    display_date: dateStr,
                    department: deptMap[b.id]
                };
                });
            } else {
                this.state.employee_birthday = [];
            }
            
            // Fetch HR Reminders
            let reminderData = [];
            if (this.state.open_hrms_requests && this.state.open_hrms_requests['hr_reminder']) {
                try {
                    reminderData = await rpc('/hr_reminder/all_reminder');
                } catch (error) {
                    // Silently ignore or just print a clean message without stack trace
                }
            }
            
            // Fetch Personal To-Dos (project.task)
            let todoDomain = [['user_ids', 'in', user.userId], ['project_id', '=', false], ['state', 'not in', ['1_done', '1_canceled']], '|', ['personal_stage_type_id', '=', false], ['personal_stage_type_id.fold', '=', false]];
            if (dFrom) {
                todoDomain.push(['date_deadline', '>=', dFrom]);
            }
            if (dTo) {
                todoDomain.push(['date_deadline', '<=', dTo]);
            }
            let todoData = await this.orm.searchRead(
                'project.task',
                todoDomain,
                ['id', 'name', 'date_deadline', 'state'],
                { limit: 5, order: 'date_deadline ASC' }
            );
            
            let combined = [];
            
            if (reminderData && reminderData.length > 0) {
                reminderData.forEach(rem => {
                combined.push({
                    type: 'reminder',
                    id: rem.id,
                    title: rem.name || 'Reminder',
                    date_deadline: new Date().toISOString().split('T')[0], // Always "Today" for active reminders
                    is_done: false
                });
                });
            }
            
            if (todoData && todoData.length > 0) {
                todoData.forEach(todo => {
                combined.push({
                    type: 'todo',
                    id: todo.id,
                    title: todo.name || 'To-do',
                    date_deadline: todo.date_deadline,
                    is_done: false
                });
                });
            }
            
            // Sort chronologically
            combined.sort((a, b) => {
                let dateA = a.date_deadline ? new Date(a.date_deadline) : new Date(8640000000000000);
                let dateB = b.date_deadline ? new Date(b.date_deadline) : new Date(8640000000000000);
                return dateA - dateB;
            });
            
            // Limit to 4 items initially
            combined = combined.slice(0, 4);
            
            let todayMs = new Date();
            todayMs.setHours(0,0,0,0);
            
            const monthNamesShort = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            
            this.state.activities = combined.map(item => {
                let dateStr = '';
                let badgeClass = 'badge-gray';
                
                if (item.date_deadline) {
                let deadline = new Date(item.date_deadline);
                let deadlineMs = new Date(item.date_deadline);
                deadlineMs.setHours(0,0,0,0);
                
                if (deadlineMs.getTime() === todayMs.getTime()) {
                    dateStr = 'Today';
                    badgeClass = 'badge-yellow';
                } else if (deadlineMs.getTime() < todayMs.getTime()) {
                    dateStr = 'Overdue';
                    badgeClass = 'badge-red';
                } else {
                    dateStr = monthNamesShort[deadline.getMonth()] + ' ' + String(deadline.getDate()).padStart(2, '0');
                    badgeClass = 'badge-gray';
                }
                } else {
                dateStr = 'No date';
                badgeClass = 'badge-gray';
                }
                
                return {
                ...item,
                date_str: dateStr,
                badge_class: badgeClass
                };
            });
        }
        var projectTaskDetails = await this.orm.call('hr.employee', 'get_employee_project_tasks', [], { date_from: dFrom, date_to: dTo })
        if (projectTaskDetails) {
            this.state.login_employee['project_task_lines'] = projectTaskDetails;
        }
        if (this.state.is_manager) {
            var pendingLeaves = await this.orm.searchRead('hr.leave', [['state', 'in', ['confirm', 'validate1']]], ['employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days']);
            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const colors = ['#14b8a6', '#ef4444', '#10b981', '#f59e0b', '#1B5298', '#8b5cf6'];
            
            this.state.pending_approvals = pendingLeaves.map((l, i) => {
                let empName = l.employee_id ? l.employee_id[1] : 'Unknown';
                let initials = empName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                let color = colors[i % colors.length];
                
                let fromDate = new Date(l.request_date_from);
                let toDate = new Date(l.request_date_to);
                let fromStr = monthNames[fromDate.getMonth()] + ' ' + String(fromDate.getDate()).padStart(2, '0');
                let toStr = monthNames[toDate.getMonth()] + ' ' + String(toDate.getDate()).padStart(2, '0');
                
                let type = l.holiday_status_id ? l.holiday_status_id[1] : 'Leave';
                
                return {
                id: l.id,
                name: empName,
                initials: initials,
                color: color,
                subtitle: `${type} · ${fromStr}-${toStr} · ${l.number_of_days}d`
                };
            });
            
            // Fetch Expiring Documents
            let todayStr = new Date().toISOString().split('T')[0];
            let docsDomain = [['expiry_date', '!=', false]];
            let idDomain = [['id_expiry_date', '!=', false]];
            let passDomain = [['passport_expiration_date', '!=', false]];

            if (dFrom) {
                docsDomain.push(['expiry_date', '>=', dFrom]);
                idDomain.push(['id_expiry_date', '>=', dFrom]);
                passDomain.push(['passport_expiration_date', '>=', dFrom]);
            } else {
                docsDomain.push(['expiry_date', '>=', todayStr]);
                idDomain.push(['id_expiry_date', '>=', todayStr]);
                passDomain.push(['passport_expiration_date', '>=', todayStr]);
            }
            if (dTo) {
                docsDomain.push(['expiry_date', '<=', dTo]);
                idDomain.push(['id_expiry_date', '<=', dTo]);
                passDomain.push(['passport_expiration_date', '<=', dTo]);
            }
            
            let expiringDocs = [];
            try {
                expiringDocs = await this.orm.searchRead(
                    'hr.employee.document', 
                    docsDomain, 
                    ['employee_ref_id', 'document_type_id', 'expiry_date'],
                    { limit: 4, order: 'expiry_date ASC' }
                );
            } catch (e) {
                // If hr.employee.document module is missing
            }

            let idDocs = [];
            let passDocs = [];
            try {
                idDocs = await this.orm.searchRead(
                    'hr.employee',
                    idDomain,
                    ['name', 'id_expiry_date'],
                    { limit: 4, order: 'id_expiry_date ASC' }
                );
                passDocs = await this.orm.searchRead(
                    'hr.employee',
                    passDomain,
                    ['name', 'passport_expiration_date'],
                    { limit: 4, order: 'passport_expiration_date ASC' }
                );
            } catch (e) {
                // If hr_employee_updation is missing
            }

            let combinedDocs = [];
            expiringDocs.forEach(doc => {
                combinedDocs.push({
                    id: doc.id,
                    real_id: doc.id,
                    is_employee_doc: false,
                    employee_ref_id: doc.employee_ref_id,
                    document_type_id: doc.document_type_id,
                    expiry_date: doc.expiry_date
                });
            });
            idDocs.forEach(doc => {
                combinedDocs.push({
                    id: 'emp_id_' + doc.id,
                    real_id: doc.id,
                    is_employee_doc: true,
                    employee_ref_id: [doc.id, doc.name || 'Unknown'],
                    document_type_id: [0, 'Identity'],
                    expiry_date: doc.id_expiry_date
                });
            });
            passDocs.forEach(doc => {
                combinedDocs.push({
                    id: 'emp_pass_' + doc.id,
                    real_id: doc.id,
                    is_employee_doc: true,
                    employee_ref_id: [doc.id, doc.name || 'Unknown'],
                    document_type_id: [0, 'Passport'],
                    expiry_date: doc.passport_expiration_date
                });
            });

            combinedDocs.sort((a, b) => new Date(a.expiry_date) - new Date(b.expiry_date));
            combinedDocs = combinedDocs.slice(0, 4);
            
            let urgentCount = 0;
            this.state.expiring_documents = combinedDocs.map((doc, i) => {
                let empName = doc.employee_ref_id ? doc.employee_ref_id[1] : 'Unknown';
                let initials = empName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                let typeName = doc.document_type_id ? doc.document_type_id[1] : 'Document';
                
                let expDate = new Date(doc.expiry_date);
                let today = new Date();
                // Strip time for accurate day calc
                expDate.setHours(0,0,0,0);
                today.setHours(0,0,0,0);
                
                let diffTime = Math.abs(expDate - today);
                let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                let isUrgent = diffDays <= 14;
                if (isUrgent) {
                urgentCount++;
                }
                
                return {
                id: doc.id,
                name: empName,
                initials: initials,
                type: typeName,
                days_left: diffDays,
                is_urgent: isUrgent,
                is_employee_doc: doc.is_employee_doc,
                color: colors[i % colors.length]
                };
            });
            this.state.urgent_count = urgentCount;
        }
        this.render_graphs();
    }
}
registry.category("actions").add("hr_dashboard", HrDashboard)

patch(ActivityMenu.prototype, {
    setup() {
        super.setup();
        var self = this
        onMounted(() => {
            this.env.bus.addEventListener('signin_signout', ({
                detail
            }) => {
                if (detail.mode == 'checked_in') {
                    self.state.checkedIn = detail.mode
                } else {
                    self.state.checkedIn = false
                }
            })
        })
    },
})
