odoo.define('hr_reminder.reminder_topbar', function (require) {
"use strict";

var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var QWeb = core.qweb;
var ajax = require('web.ajax');

var reminder_menu = Widget.extend({
    template:'reminder_menu',

    events: {
        "click .dropdown-toggle": "on_click_reminder",
        "click .detail-client-address-country": "reminder_active",
    },

    willStart: function(){
            var self = this;
            self.all_reminder = [];
            return this._super()
            .then(function() {
             var def1 = ajax.jsonRpc("/hr_reminder/all_reminder", 'call',{}
//             ajax.jsonRpc("/hr_reminder/all_reminder", 'call',{}
            ).then(function(all_reminder){
            self.all_reminder = all_reminder
            console.log('CLICK Reminder')
            console.log(all_reminder)
            console.log(self.all_reminder)
//            self.$('.o_mail_navbar_dropdown_top').append(QWeb.render('reminder_menu',{
//                widget: self
//            }));
//           return $.when(def1);
            });
        });
            },


    on_click_reminder: function (event) {
        var self = this
        self.all_reminder = []
//        event.stopPropagation();
//        event.preventDefault();
         ajax.jsonRpc("/hr_reminder/all_reminder", 'call',{}
        ).then(function(all_reminder){
        self.all_reminder = all_reminder
        console.log('CLICK Reminder')
        console.log(all_reminder)
        console.log(self.all_reminder)
        self.$('.o_mail_navbar_dropdown_top').html(QWeb.render('reminder_menu',{
                values: self.all_reminder,
                widget: self

            }));
        });
        },


    reminder_active: function(){
        var self = this;
//        event.stopPropagation();
//        event.preventDefault();
        var value =$("#reminder_select").val();
        ajax.jsonRpc("/hr_reminder/reminder_active", 'call',{'reminder_name':value}
        ).then(function(reminder){
            self.reminder = reminder
            console.log('reminder on click selection',self.reminder)
             for (var i=0;i<1;i++){
                    var model = self.reminder[i]
                    console.log('reminder[0]',self.reminder[i])
                    var date = self.reminder[i+1]
                   console.log('reminder[1]',self.reminder[i+1])

                    console.log("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDd",date,new Date())
                    if (self.reminder[i+2] == 'today'){

                        return self.do_action({
                             type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'list',
//                            domain: [[date, '=', new Date()]],
                            domain: [[date, '=', new Date()]],
                            views: [[false, 'list']],
                            target: 'new',})
                        }

                    else if (self.reminder[i+2] == 'set_date'){
                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'list',
                            domain: [[date, '=', self.reminder[i+3]]],
                            views: [[false, 'list']],
                            target: 'new',
                            })
                        }

                    else if (self.reminder[i+2] == 'set_period'){
                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'list',
                            domain: [[date, '<', self.reminder[i+5]],[date, '>', self.reminder[i+4]]],
                            views: [[false, 'list']],
                            target: 'new',
                            })
                            }

                        }

             });
        },
});

SystrayMenu.Items.push(reminder_menu);
});
