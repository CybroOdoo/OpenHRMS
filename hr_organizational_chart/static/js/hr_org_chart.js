var employee_data = [];

var nodeTemplate = function(data) {
      return `
        <span class="office">${data.office}</span>
        <div class="title">${data.name}</div>
        <div class="content">${data.title}</div>
      `;
    };

odoo.define("hr_org_chart_employee.hr_org_chart", function (require) {
  "use strict";

  var core = require('web.core');
  var session = require('web.session');
  var ajax = require('web.ajax');
  var Widget = require('web.Widget');
  var QWeb = core.qweb;
  var _t = core._t;
  var AbstractAction = require('web.AbstractAction');
  var _lt = core._lt;

  var OrgChartDepartment = AbstractAction.extend({
    events: {
        'click .nodes,.node': 'view_employee',
        },
    init: function(parent, context){
      this._super(parent, context);
        var self = this;
        if (context.tag == 'employee_organization_chart') {
            this._rpc({
            route: '/get/employees',
        }).then(function (result) {
            self._rpc({
                model: 'hr.organizational.chart',
                method: 'get_employee_data',
                args: [result],
            }, []).then(function(values){
                employee_data = values;
                self.render();
                self.href = window.location.href;
            });
            });
        }
    },
    willStart: function() {
      return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
      var self = this;
      return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var org_chart = QWeb.render('hr_organizational_chart.org_chart_template', {
            widget: self,
        });
        $(".o_control_panel").addClass("o_hidden");
        $(org_chart).prependTo(self.$el);
        return org_chart;
    },
    reload: function () {
      window.location.href = this.href;
    },
    view_employee: function(ev){
        if (ev.target.attributes[1]){
            var id = parseInt(ev.target.attributes[1].nodeValue)
            this.do_action({
            name: _t("Employee"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: id,
            view_mode: 'form',
            views: [[false, 'form']],
            })
        }
    },
  });



  core.action_registry.add('employee_organization_chart', OrgChartDepartment);
  window.reload()

  return OrgChartDepartment;


});