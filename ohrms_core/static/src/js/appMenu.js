odoo.define('ohrms_core.appMenu', function (require) {
    'use strict';

    var appsMenu = require("web.AppsMenu");
    var utils = require("web.utils");
    var core = require("web.core");

    function findNames (memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, findNames, memo);
        }
        return memo;
    }


    appsMenu.include({
        events: {
            "input .search-input input": "_searchMenusSchedule",
            "click .o-menu-search-result": "_searchResultChosen",
        },
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._activeApp = undefined;
            this._apps = _.map(menuData.children, function (appMenuData) {
                var webIcon = false;
                if (appMenuData.web_icon) {
                    webIcon = appMenuData.web_icon.replace(',', '/');
                }
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    webIcon: webIcon || '/base/static/description/icon.png',
                };
            });
            this._search_def = $.Deferred();
            this._searchableMenus = _.reduce(
                menuData.children,
                findNames,
                {}
            );
        },
        start: function () {
            this.$search_container = this.$(".search-container");
            this.$search_input = this.$(".search-input input");
            this.$search_results = this.$(".search-results");
            this.$app_menu = this.$(".app-menu");
            this.$dropdown_menu = this.$(".dropdown-menu");
            return this._super.apply(this, arguments);
        },
        _searchMenusSchedule: function () {
            this.$search_results.removeClass("o_hidden")
            this.$app_menu.addClass("o_hidden");
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 50);
            this._search_def.done(this._searchMenus.bind(this));
        },
        //search result will append to the view with class name '.search-results'
        _searchMenus: function () {
            var query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("has-results");
                this.$app_menu.removeClass("o_hidden");
                this.$search_results.empty();
                return;
            }
            var results = fuzzy.filter(
                query,
                _.keys(this._searchableMenus),
                {
                    pre: "<b>",
                    post: "</b>",
                }

            );
            this.$search_container.toggleClass(
                "has-results",
                Boolean(results.length)
            );
            this.$search_results.html(
                core.qweb.render(
                    "ohrms_core.SearchResults",
                    {
                        results: results,
                        widget: this,
                    }
                )
            );
        },
        //_menuInfo call from template ohrms_core.SearchResults to get element related to the key
        _menuInfo: function (key) {
            var original = this._searchableMenus[key];
            return _.extend({
                action_id: parseInt(original.action.split(',')[1], 10),
            }, original);
        },
        _searchResultChosen: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var $result = $(event.currentTarget),
                text = $result.text().trim(),
                data = $result.data(),
                suffix = ~text.indexOf("/") ? "/" : "";
            // Load the menu view
            this.trigger_up("menu_clicked", {
                action_id: data.actionId,
                id: data.menuId,
                previous_menu_id: data.parentId,
            });
            // Find app that owns the chosen menu
            var app = _.find(this._apps, function (_app) {
                return text.indexOf(_app.name + suffix) === 0;
            });
            this.$dropdown_menu.removeClass("show");
            this.$search_results.addClass("o_hidden");
            this.$app_menu.removeClass("o_hidden");
            this.$search_input.val('');
            // Update navbar menus
            core.bus.trigger("change_menu_section", app.menuID);
        },
    });
    return appsMenu;
});
