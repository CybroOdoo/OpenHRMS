odoo.define('hrms_dashboard.Dashboard', function (require) {
"use strict";
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var session = require('web.session');
var rpc = require('web.rpc');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var session = require('web.session');
var _t = core._t;
var QWeb = core.qweb;

var HrDashboard = Widget.extend(ControlPanelMixin, {
    template: "HrDashboardMain",
    events: {
        'click .hr_leave_request_approve': 'leaves_to_approve',
        'click .hr_leave_allocations_approve': 'leave_allocations_to_approve',
        'click .hr_timesheets': 'hr_timesheets',
        'click .hr_job_application_approve': 'job_applications_to_approve',
//        'click .hr_payslip':'hr_payslip',
//        'click .hr_contract':'hr_contract',
        'click .hr_employee':'hr_employee',
        'click .leaves_request_month':'leaves_request_month',
        'click .leaves_request_today':'leaves_request_today',
        "click .o_hr_attendance_sign_in_out_icon": function() {
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            this.update_attendance();
        },
        'click #broad_factor_pdf': 'generate_broad_factor_report',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.login_employee = false;
        this.employee_birthday = [];
        this.action_id = context.id;
        this._super(parent,context);

    },

    start: function() {
        var self = this;
        for(var i in self.breadcrumbs){
            self.breadcrumbs[i].title = "Dashboard";
        }
        self.update_control_panel({breadcrumbs: self.breadcrumbs}, {clear: true});
        rpc.query({
            model: "hr.employee",
            method: "get_user_employee_details",
        })
        .then(function (result) {
            if(result){
                self.login_employee =  result[0];
                var manager_view = $('.o_hr_dashboard').html(QWeb.render('ManagerDashboard', {widget: self}));
                self.render_graph();
                self.render_leave_graph();
//                self.render_leave_broad_factor();
                $('.o_hr_dashboard').prepend(QWeb.render('LoginEmployeeDetails', {widget: self}));
                /*need to check user access levels*/
                session.user_has_group('hr.group_hr_manager').then(function(has_group){
                    if(has_group == false){
                        $('.employee_dashboard_main').css("display", "none");
                    }
                });

                /*Upcoming Birthdays*/
                var today = new Date().toJSON().slice(0,10).replace(/-/g,'/');
                rpc.query({
                    model: "hr.employee",
                    method: "search_read",
                    args: [
                        [['birthday', '!=', false]],
                        ['name', 'birthday','image', 'job_id']
                    ],
                })
                .then(function (res) {
                    for (var i = 0; i < res.length; i++) {
                        var bday_dt = new Date(res[i]['birthday']);
                        var bday_month = bday_dt.getMonth();
                        var bday_day = bday_dt.getDate();
                        var today_dt = new Date( today);
                        var today_month = today_dt.getMonth();
                        var today_day = today_dt.getDate();
                        var day = new Date();
                        var next_day = new Date(day.setDate(day.getDate() + 7));
                        var next_week = next_day.toJSON().slice(0,10).replace(/-/g,'/');
                        var bday_date = bday_dt.toJSON().slice(0,10).replace(/-/g,'/');
                        if (bday_month == today_month  && bday_day >= today_day && next_week >= bday_date){
                            self.employee_birthday.push(res[i]);
                            var flag = 1;
                        }
                    }
                        if (flag !=1){
                            self.employee_birthday = false;
                        }
                    $('.o_hr_dashboard').append(QWeb.render('EmployeeDashboard', {widget: self}));
                    self.update_leave_trend();
                });

             }
            else{
                $('.o_hr_dashboard').prepend(QWeb.render('EmployeeWarning', {widget: self}));
                return;
            }
        });
    },

    generate_broad_factor_report: function(){
        this.do_action({
            type: 'ir.actions.report',
            report_type: 'qweb-pdf',
            report_name: 'hrms_dashboard.report_broadfactor/1'
        });
    },

    update_attendance: function () {
        var self = this;
        this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.login_employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
            })
            .then(function(result) {
                var action_client = {
                    type: "ir.actions.client",
                    tag: 'hr_dashboard',
                };
                self.do_action(action_client);
            });
    },

    on_reverse_breadcrumb: function() {
        this.update_control_panel({clear: true});
        web_client.do_push_state({action: this.action_id});
    },

    hr_payslip: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Employee Payslips"),
            type: 'ir.actions.act_window',
            res_model: 'hr.payslip',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['employee_id','=', this.login_employee.id]],
            target: 'current'
        }, options)
    },

    hr_contract: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'hr.contract',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['employee_id','=', this.login_employee.id]],
            target: 'current'
        }, options)
    },

    leaves_request_month: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var date = new Date();
        var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        var fday = firstDay.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        this.do_action({
            name: _t("This Month Leaves"),
            type: 'ir.actions.act_window',
            res_model: 'hr.holidays',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['date_from','>', fday],['state','=','validate'],['date_from','<', lday], ['type','=','remove']],
            target: 'current'
        }, options)
    },

    leaves_request_today: function(e) {
        var self = this;
        var date = new Date();
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Leaves Today"),
            type: 'ir.actions.act_window',
            res_model: 'hr.holidays',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','=','remove'], ['date_from','<=', date], ['date_to', '>=', date], ['state','=','validate']],
            target: 'current'
        }, options)
    },
    leaves_to_approve: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.holidays',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','=','remove'], ['state','in',['confirm','validate1']]],
            target: 'current'
        }, options)
    },
    leave_allocations_to_approve: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Leave Allocation Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.holidays',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','=','add'],['state','in',['confirm', 'validate1']]],
            target: 'current'
        }, options)
    },

    hr_timesheets: function(e) {
         var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Timesheets"),
            type: 'ir.actions.act_window',
            res_model: 'account.analytic.line',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'], [false, 'form']],
            context: {
                'search_default_month': true,
            },
            domain: [['employee_id','=', this.login_employee.id]],
            target: 'current'
        }, options)
    },
    job_applications_to_approve: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Applications"),
            type: 'ir.actions.act_window',
            res_model: 'hr.applicant',
            view_mode: 'tree,kanban,form,pivot,graph,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'kanban'],[false, 'form'],
                    [false, 'pivot'],[false, 'graph'],[false, 'calendar']],
            context: {},
            target: 'current'
        }, options)
    },

    render_leave_broad_factor:function(){
        var self = this;
        var elem = this.$('.leave_broad_factor');
        var w = 600;
        var h = 300;

        rpc.query({
            model: "hr.employee",
            method: "get_broad_factor",
        }).then(function (dataset) {
            var data = dataset;
            var margin = {top: 10, right: 20, bottom: 50, left: 40},
                width = 1000 - margin.left - margin.right,
                height = 300 - margin.top - margin.bottom;

            var formatPercent = d3.format("0");
            var x = d3.scale.ordinal()
                .rangeRoundBands([0, width], .1);

            var y = d3.scale.linear()
                .range([height, 0]);

            var xAxis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left")
                .tickFormat(formatPercent);


            var svg = d3.select(elem[0]).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            x.domain(data.map(function(d) { return d.name; }));
            y.domain([0, d3.max(data, function(d) { return d.broad_factor; })]);

            svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
            .attr("y", 0)
            .attr("x", 9)
            .attr("dy", ".35em")
            .attr("transform", "rotate(20)")
            .style("text-anchor", "start");

            svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Leave Broad Factor");

            svg.selectAll(".bar")
                .data(data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d.name); })
                .attr("width", x.rangeBand())
                .attr("y", function(d) { return y(d.broad_factor); })
                .attr("height", function(d) { return height - y(d.broad_factor); })
                .attr("fill", function(d) {return "#934da5";})
                .on("mouseover", function() { tooltip.style("display", null); })
                .on("mouseout", function() { tooltip.style("display", "none");})
                .on("mousemove", function(d) {
                    var xPosition = d3.mouse(this)[0] - 15;
                    var yPosition = d3.mouse(this)[1] - 25;
                    tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
                    tooltip.select("text").text(d.broad_factor);
                });

                var tooltip = svg.append("g")
                  .attr("class", "tooltip")
                  .style("display", "none");

                tooltip.append("rect")
                  .attr("width", 30)
                  .attr("height", 20)
                  .attr("fill", "black")
                  .style("opacity", 0.5);

                tooltip.append("text")
                  .attr("x", 15)
                  .attr("dy", "1.2em")
                  .style("text-anchor", "middle")
                  .attr("font-size", "12px")
                  .attr("font-weight", "bold");
        });
    },

    render_graph:function(){
        var self = this;
        var w = 200;
        var h = 200;
        var r = h/2;
        var elem = this.$('.emp_graph');
//        var colors = ['#ff8762', '#5ebade', '#b298e1', '#70cac1', '#cf2030'];
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        rpc.query({
            model: "hr.employee",
            method: "get_dept_employee",
        }).then(function (data) {
            var segColor = {};
            var vis = d3.select(elem[0]).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
            var pie = d3.layout.pie().value(function(d){return d.value;});
            var arc = d3.svg.arc().outerRadius(r);
            var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
            arcs.append("svg:path")
                .attr("fill", function(d, i){
                    return color(i);
                })
                .attr("d", function (d) {
                    return arc(d);
                });

            var legend = d3.select(elem[0]).append("table").attr('class','legend');

            // create one row per segment.
            var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

            // create the first column for each segment.
            tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                .attr("width", '16').attr("height", '16')
                .attr("fill",function(d, i){ return color(i) });

            // create the second column for each segment.
            tr.append("td").text(function(d){ return d.label;});

            // create the third column for each segment.
            tr.append("td").attr("class",'legendFreq')
                .text(function(d){ return d.value;});



        });

    },

    render_leave_graph:function(){
        var self = this;
//        var color = d3.scale.category10();
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        rpc.query({
                model: "hr.employee",
                method: "get_department_leave",
            }).then(function (data) {
                var fData = data[0];
                var dept = data[1];
                var id = self.$('.leave_graph')[0];
                var barColor = '#ff618a';
                // compute total for each state.
                fData.forEach(function(d){
                    var total = 0;
                    for (var dpt in dept){
                        total += d.leave[dept[dpt]];
                    }
                d.total=total;
                });

                // function to handle histogram.
                function histoGram(fD){
                    var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
                    hGDim.w = 350 - hGDim.l - hGDim.r,
                    hGDim.h = 200 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                            .domain(fD.map(function(d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                            .domain([0, d3.max(fD, function(d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                            .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function(d) { return x(d[0]); })
                        .attr("y", function(d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function(d) { return hGDim.h - y(d[1]); })
                        .attr('fill',barColor)
                        .on("mouseover",mouseover)// mouseover is defined below.
                        .on("mouseout",mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function(d){ return d3.format(",")(d[1])})
                        .attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
                        .attr("y", function(d) { return y(d[1])-5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d){  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function(s){ return s.l_month == d[0];})[0],
                            nD = d3.keys(st.leave).map(function(s){ return {type:s, leave:st.leave[s]};});

                        // call update functions of pie-chart and legend.
                        pC.update(nD);
                        leg.update(nD);
                    }

                    function mouseout(d){    // utility function to be called on mouseout.
                        // reset the pie-chart and legend.
                        pC.update(tF);
                        leg.update(tF);
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function(nD, color){
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function(d) {return y(d[1]); })
                            .attr("height", function(d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function(d){ return d3.format(",")(d[1])})
                            .attr("y", function(d) {return y(d[1])-5; });
                    }
                    return hG;
                }

                // function to handle pieChart.
                function pieChart(pD){
                    var pC ={},    pieDim ={w:250, h: 250};
                    pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

                    // create svg for pie chart.
                    var piesvg = d3.select(id).append("svg")
                        .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
                        .attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");

                    // create function to draw the arcs of the pie slices.
                    var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

                    // create a function to compute the pie slice angles.
                    var pie = d3.layout.pie().sort(null).value(function(d) { return d.leave; });

                    // Draw the pie slices.
                    piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
                        .each(function(d) { this._current = d; })
                        .attr("fill", function(d, i){return color(i);})
                        .on("mouseover",mouseover).on("mouseout",mouseout);

                    // create function to update pie-chart. This will be used by histogram.
                    pC.update = function(nD){
                        piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                            .attrTween("d", arcTween);
                    }
                    // Utility function to be called on mouseover a pie slice.
                    function mouseover(d, i){
                        // call the update function of histogram with new data.
                        hG.update(fData.map(function(v){
                            return [v.l_month,v.leave[d.data.type]];}),color(i));
                    }
                    //Utility function to be called on mouseout a pie slice.
                    function mouseout(d){
                        // call the update function of histogram with all data.
                        hG.update(fData.map(function(v){
                            return [v.l_month,v.total];}), barColor);
                    }
                    // Animating the pie-slice requiring a custom function which specifies
                    // how the intermediate paths should be drawn.
                    function arcTween(a) {
                        var i = d3.interpolate(this._current, a);
                        this._current = i(0);
                        return function(t) { return arc(i(t));    };
                    }
                    return pC;
                }

                // function to handle legend.
                function legend(lD){
                    var leg = {};

                    // create table for legend.
                    var legend = d3.select(id).append("table").attr('class','legend');

                    // create one row per segment.
                    var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

                    // create the first column for each segment.
                    tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                        .attr("width", '16').attr("height", '16')
                        .attr("fill", function(d, i){return color(i);})

                    // create the second column for each segment.
                    tr.append("td").text(function(d){ return d.type;});

                    // create the third column for each segment.
                    tr.append("td").attr("class",'legendFreq')
                        .text(function(d){ return d.l_month;});

                    // create the fourth column for each segment.
                    tr.append("td").attr("class",'legendPerc')
                        .text(function(d){ return getLegend(d,lD);});

                    // Utility function to be used to update the legend.
                    leg.update = function(nD){
                        // update the data attached to the row elements.
                        var l = legend.select("tbody").selectAll("tr").data(nD);

                        // update the frequencies.
                        l.select(".legendFreq").text(function(d){ return d3.format(",")(d.leave);});

                        // update the percentage column.
                        l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});
                    }

                    function getLegend(d,aD){ // Utility function to compute percentage.
                        var perc = (d.leave/d3.sum(aD.map(function(v){ return v.leave; })));
                        if (isNaN(perc)){
                            return d3.format("%")(0);
                            }
                        else{
                            return d3.format("%")(d.leave/d3.sum(aD.map(function(v){ return v.leave; })));
                            }
                    }

                    return leg;
                }
                // calculate total frequency by segment for all state.
                var tF = dept.map(function(d){
                    return {type:d, leave: d3.sum(fData.map(function(t){ return t.leave[d];}))};
                });

                // calculate total frequency by state for all segment.
                var sF = fData.map(function(d){return [d.l_month,d.total];});

                var hG = histoGram(sF), // create the histogram.
                    pC = pieChart(tF), // create the pie-chart.
                    leg= legend(tF);  // create the legend.
        });
    },

    update_leave_trend: function(){
        var self = this;
        rpc.query({
            model: "hr.employee",
            method: "employee_leave_trend",
        }).then(function (data) {
            var elem = self.$('.leave_trend');
            var margin = {top: 30, right: 20, bottom: 30, left: 80},
                width = 500 - margin.left - margin.right,
                height = 250 - margin.top - margin.bottom;

            // Set the ranges
            var x = d3.scale.ordinal()
                .rangeRoundBands([0, width], 1);

            var y = d3.scale.linear()
                .range([height, 0]);

            // Define the axes
            var xAxis = d3.svg.axis().scale(x)
                .orient("bottom");

            var yAxis = d3.svg.axis().scale(y)
                .orient("left").ticks(5);

            var valueline = d3.svg.line()
                .x(function(d) { return x(d.l_month); })
                .y(function(d) { return y(d.leave); });


            var svg = d3.select(elem[0]).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            x.domain(data.map(function(d) { return d.l_month; }));
            y.domain([0, d3.max(data, function(d) { return d.leave; })]);

            // Add the X Axis
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            // Add the Y Axis
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            svg.append("path")
                .attr("class", "line")
                .attr("d", valueline(data));

            // Add the scatterplot
            svg.selectAll("dot")
                .data(data)
                .enter().append("circle")
                .attr("r", 3)
                .attr("cx", function(d) { return x(d.l_month); })
                .attr("cy", function(d) { return y(d.leave); })
//                .on('mouseover', function() { d3.select(this).transition().duration(500).ease("elastic").attr('r', 3 * 2) })
//                .on('mouseout', function() { d3.select(this).transition().duration(500).ease("in-out").attr('r', 3) });
                .on("mouseover", function() { tooltip.style("display", null);
                    d3.select(this).transition().duration(500).ease("elastic").attr('r', 3 * 2)
                 })
                .on("mouseout", function() { tooltip.style("display", "none");
                    d3.select(this).transition().duration(500).ease("in-out").attr('r', 3)
                })
                .on("mousemove", function(d) {
                    var xPosition = d3.mouse(this)[0] - 15;
                    var yPosition = d3.mouse(this)[1] - 25;
                    tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
                    tooltip.select("text").text(d.leave);
                });

            var tooltip = svg.append("g")
                  .attr("class", "tooltip")
                  .style("display", "none");

                tooltip.append("rect")
                  .attr("width", 30)
                  .attr("height", 20)
                  .attr("fill", "black")
                  .style("opacity", 0.5);

                tooltip.append("text")
                  .attr("x", 15)
                  .attr("dy", "1.2em")
                  .style("text-anchor", "middle")
                  .attr("font-size", "12px")
                  .attr("font-weight", "bold");

        });
    },


});

core.action_registry.add('hr_dashboard', HrDashboard);

return HrDashboard;

});
