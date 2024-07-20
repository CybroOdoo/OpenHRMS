/** @odoo-module **/
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { onMounted, Component, useRef } from "@odoo/owl";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";
const actionRegistry = registry.category("actions");
export class PayrollDashboard extends Component{
//
   setup(){
       this.effect = useService("effect");
       this.user = useService("user")
       this.action = useService("action");
       this.orm = useService("orm");
       this.emp_graph = useRef("expense_graph")
       this.leave_graph = useRef("leave_graph")
       this.leave_trend = useRef("leave_trend")
       this.payslips_graph = useRef("payslips_graph")
       this.contracts_graph = useRef("contracts_graph")
       this.time_off_graph = useRef("time_off_graph")
       this.state = useState({
        is_manager: false,
        dashboards_templates: ['PayrollManagerDashboard','EmployeeDetails', 'ManagerLeaveDashboard','PayrollChart'],
        login_employee: [],
        })
   onWillStart(async () => {
        this.isHrManager = await this.user.hasGroup("hr.group_hr_manager");
        this.state.login_employee = {}
        if ( await this.orm.call('hr.employee', 'check_user_group', []) ) {
            this.state.is_manager = true
        }
        else {
            this.state.is_manager = false
        }
        var empDetails = await this.orm.call('hr.employee', 'get_user_employee_info', [])
        if ( empDetails ){
            this.state.login_employee = empDetails[0]
        }
    });
         onMounted(() => {
            this.title = 'Dashboard'
            this.render_graphs();
        });
   }
   render_graphs(){
        var self = this;
        if (this.state.login_employee){
            self.render_expense_graph();
            self.render_leave_graph();
            self.update_leave_trend();
            self.render_employee_payslips_graph();
            self.render_employee_contracts_graph();
            self.render_employee_time_off_graph();
        }
    }

    async render_employee_time_off_graph(){
     /**
     * Render the employee time off graph.
     */
        var self = this;
        var w = 200;
        var h = 200;
        var r = h/2;
        var elem = self.time_off_graph.el
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var data = await this.orm.call('hr.leave', 'get_employee_time_off', [])
        if (data){
            var segColor = {};
            var vis = d3.select(elem).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
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
            var legend = d3.select(elem).append("table").attr('class','legend');
            // create one row per segment.
            var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");
            // create the first column for each segment.
            tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                .attr("width", '16').attr("height", '16')
                .attr("fill",function(d, i){ return color(i) });
            // create the second column for each segment.
            tr.append("td").attr("style","font-weight: bold;").text(function(d){ return d.label;});
            // create the third column for each segment.
            tr.append("td").attr("class",'legendFreq').attr("style","border: 5px solid transparent; font-weight: bold;")
                .text(function(d){ return d.value;});
        }
    }
    async render_employee_contracts_graph(){
    /**
     * Render the employee contracts graph.
     */
        var self = this;
        var w = 200;
        var h = 200;
        var r = h/2;
        var elem = self.contracts_graph.el
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var data = await this.orm.call('hr.contract', 'get_employee_contract', [])
        if(data){
            var segColor = {};
            var vis = d3.select(elem).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
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
            var legend = d3.select(elem).append("table").attr('class','legend');
            // create one row per segment.
            var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");
            // create the first column for each segment.
            tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                .attr("width", '16').attr("height", '16')
                .attr("fill",function(d, i){ return color(i) });
            // create the second column for each segment.
            tr.append("td").attr("style","font-weight: bold;").text(function(d){ return d.label;});
            // create the third column for each segment.
            tr.append("td").attr("class",'legendFreq').attr("style","border: 5px solid transparent; font-weight: bold;")
                .text(function(d){ return d.value;});
        }
    }
      async render_employee_payslips_graph(){
       /**
     * Render the Employee payslips graph.
     */
        var self = this;
        var w = 200;
        var h = 200;
        var r = h/2;
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var data = await this.orm.call('hr.payslip', 'get_employee_payslips', [])
        if(data){
            var segColor = {};
            var elem = self.payslips_graph.el
            var vis = d3.select(elem).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
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
            var legend = d3.select(elem).append("table").attr('class','legend');
            // create one row per segment.
            var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");
            // create the first column for each segment.
            tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                .attr("width", '16').attr("height", '16')
                .attr("fill",function(d, i){ return color(i) });
            // create the second column for each segment.
            tr.append("td").attr("style","font-weight: bold;").text(function(d){ return d.label;});
            // create the third column for each segment.
            tr.append("td").attr("class",'legendFreq')
                .text(function(d){ return d.value;});
        }
    }

   async render_leave_graph(){
        var self = this;
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var data = await this.orm.call('hr.employee', 'get_department_leave', [])
        if (data) {
            var fData = data[0];
            var dept = data[1];
            var barColor = '#ff618a';
            var id = self.leave_graph.el
            // compute total for each state.
            fData.forEach(function(d){
                var total = 0;
                for (var dpt in dept){
                    total += d.leave[dept[dpt]];
                }
                d.total=total;
            });
            // function to handle histogram.
            function histoGram (fD) {
                var hG = {},    hGDim = {t: 60, r: 0, b: 30, l: 0};
                hGDim.w = 350 - hGDim.l - hGDim.r;
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
            var hG = histoGram(sF); // create the histogram.
            var pC = pieChart(tF); // create the pie-chart.
            var leg = legend(tF);  // create the legend.
        }
    }

     async update_leave_trend(){
        var self = this;
        var data = await this.orm.call('hr.employee', 'employee_leave_trend', [])
        if (data) {
            var elem = self.leave_trend.el
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
            var svg = d3.select(elem).append("svg")
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
        }
    }

    async render_expense_graph(){
    /**
     * Render the expense graph.
     * This function retrieves employee expense data and renders it as a graph using D3.js.
     * The graph displays the monthly expenses of employees.
     */
        var self = this;
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var data = await this.orm.call('hr.expense', 'get_employee_expense', [])
        var elem = self.emp_graph.el
            if(data){
                data.forEach(function(d) {
                  d.values.forEach(function(d) {
                    d.l_month = d.l_month;
                    d.count = +d.count;
                  });
                });
                var margin = {top: 30, right: 10, bottom: 30, left: 30},
                    width = 400 - margin.left - margin.right,
                    height = 250 - margin.top - margin.bottom
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
                x.domain(data[0].values.map(function(d) { return d.l_month; }));
                y.domain([0, d3.max(data[0].values, d => d.count)])
                var svg = d3.select(elem).append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
                // Add the X Axis
                svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);
                // Add the Y Axis
                svg.append("g")
                    .attr("class", "y axis")
                    .call(yAxis);
                var line = d3.svg.line()
                    .x(function(d) {return x(d.l_month); })
                    .y(function(d) {return y(d.count); });
                let lines = svg.append('g')
                  .attr('class', 'lines');
                lines.selectAll('.line-group')
                    .data(data).enter()
                    .append('g')
                    .attr('class', 'line-group')
                    .append('path')
                    .attr('class', 'line')
                    .attr('d', function(d) { return line(d.values); })
                    .style('stroke', (d, i) => color(i));
                lines.selectAll("circle-group")
                    .data(data).enter()
                    .append("g")
                    .selectAll("circle")
                    .data(function(d) { return d.values;}).enter()
                    .append("g")
                    .attr("class", "circle")
                    .append("circle")
                    .attr("cx", function(d) { return x(d.l_month)})
                    .attr("cy", function(d) { return y(d.count)})
                    .attr("r", 3);
            }
    }

    payslips_click() {
    /*
     * Open the Payslips window.
     */

    this.action.doAction({
        name: _t("Employee Payslips"),
        type: 'ir.actions.act_window',
        res_model: 'hr.payslip',
        view_mode: 'tree,form,calendar',
        views: [[false, 'list'],[false, 'form']],
        context: {"create": false},
        domain : this.state.is_manager == true ? [] : [['employee_id','=', this.state.login_employee.id]]
    });

    }


    hr_attendance() {
    /*
     * Open the Attendance window.
     */
    this.action.doAction({
        name: _t("Employee Attendances"),
        type: 'ir.actions.act_window',
        res_model: 'hr.attendance',
        view_mode: 'tree',
        views: [[false, 'list'],],
        context: {"create": false},
        domain : this.state.is_manager == true ? [] : [['employee_id','=', this.state.login_employee.id]]
    });

    }
    contracts_click() {
    /*
     * Open the Contract window.
     */
    this.action.doAction({
        name: _t("Employee Contracts"),
        type: 'ir.actions.act_window',
        res_model: 'hr.contract',
        view_mode: 'tree',
        views: [[false, 'list'],],
        context: {"create": false},
        domain : this.state.is_manager == true ? [] : [['employee_id','=', this.state.login_employee.id]]
    });

    }

    salary_click() {
    /*
     * Open the Contract window.
     */
    this.action.doAction({
        name: _t("Salary Rules"),
        type: 'ir.actions.act_window',
        res_model: 'hr.salary.rule',
        view_mode: 'tree',
        views: [[false, 'list'],],
        context: {"create": false},
    });

    }
    salary_structure_click() {
    /*
     * Open the Contract window.
     */
    this.action.doAction({
        name: _t("Salary Structures"),
        type: 'ir.actions.act_window',
        res_model: 'hr.payroll.structure',
        view_mode: 'tree',
        views: [[false, 'list'],],
        context: {"create": false},
    });

    }
        leaves_to_approve() {
        this.action.doAction({
            name: _t("Leave Request"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['confirm','validate1']]],
            target: 'current'
        });
    }

}
actionRegistry.add("payroll_dashboard", PayrollDashboard)
PayrollDashboard.template = 'hr_payroll_dashboard.PayrollDashboardMain';

