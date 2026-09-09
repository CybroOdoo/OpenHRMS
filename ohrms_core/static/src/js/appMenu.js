/** @odoo-module */
import { NavBar } from "@web/webclient/navbar/navbar";
import { registry } from "@web/core/registry";
const { fuzzyLookup } = require('@web/core/utils/search');
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { onMounted, Component, useRef, useState } from "@odoo/owl";
import { routerBus } from "@web/core/browser/router";
const commandProviderRegistry = registry.category("command_provider");
import { patch } from "@web/core/utils/patch";
import { ActivityMenu } from "@mail/core/web/activity_menu";

patch(ActivityMenu.prototype, {
    openActivityGroup(group, filter = "all", newWindow) {
        // Fix UX misclick issue: if user clicks a 0-count filter (e.g., clicking the 'Future' area by mistake 
        // because it aligns with the mouse cursor), fallback to 'all' so they still get relevant Late/Today records.
        if (filter === "overdue" && group.overdue_count === 0) filter = "all";
        if (filter === "today" && group.today_count === 0) filter = "all";
        if (filter === "upcoming_all" && group.planned_count === 0) filter = "all";
        
        return super.openActivityGroup(group, filter, newWindow);
    }
});

patch(NavBar.prototype, {
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * @override
     */
     setup() {
        super.setup();
        this.search_input = useRef("search-input")
        this._search_def = new $.Deferred();
        let { apps, menuItems } = computeAppsAndMenuItems(this.menuService.getMenuAsTree("root"));
        this._apps = apps;
        this._searchableMenus = menuItems;
        this.state = useState({
            results : [],
            isSearchOpen: false,
            activeIndex: 0,
        });

        // Patch Odoo's global action service to treat the App Launcher as a fresh context
        if (this.env.services.action && !this.env.services.action.doAction._isOhrmsPatched) {
            const originalDoAction = this.env.services.action.doAction;
            this.env.services.action.doAction = async function (actionRequest, options = {}) {
                if (document.body.classList.contains('app-launcher-open') || sessionStorage.getItem('app_launcher_open') === 'true') {
                    // Force clearing breadcrumbs when executing actions from the App Launcher
                    options.clearBreadcrumbs = true;
                    // Prevent Odoo from restoring an old search state (like 'Future Activities') from a previous session
                    sessionStorage.removeItem('current_action');
                    sessionStorage.removeItem('current_state');
                }
                return originalDoAction.apply(this, [actionRequest, options]);
            };
            this.env.services.action.doAction._isOhrmsPatched = true;
        }

        // Intercept typing, Ctrl+K and Escape when App Launcher is visible
        window.addEventListener('keydown', (ev) => {
            const fullscreenMenu = document.querySelector('.dropdown-menu.fullscreen-menu.show');
            if (fullscreenMenu) {
                if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') {
                    ev.preventDefault();
                    ev.stopPropagation();
                    this.openCustomSearch(ev);
                } else if (ev.key === 'Escape' && this.state.isSearchOpen) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    this.closeCustomSearch(ev);
                } else if (!this.state.isSearchOpen && ev.key.length === 1 && !ev.ctrlKey && !ev.metaKey && !ev.altKey) {
                    if (ev.target.tagName !== 'INPUT' && ev.target.tagName !== 'TEXTAREA') {
                        ev.preventDefault();
                        ev.stopPropagation();
                        this.openCustomSearch(ev, ev.key);
                    }
                }
            }
        }, { capture: true });

        onMounted(() => {
            if (sessionStorage.getItem('app_launcher_open') === 'true') {
                const menuEl = document.querySelector(".dropdown-menu.fullscreen-menu");
                if (menuEl) {
                    menuEl.classList.add("show");
                    const navbar = document.querySelector('.o_main_navbar');
                    if (navbar) navbar.classList.add('app-launcher-open');
                    document.body.classList.add('app-launcher-open');
                }
            }
        });

        // Ensure App Launcher closes when navigating via Systray or other non-App Launcher links.
        // We use a MutationObserver on document.body to detect when Odoo's ActionManager or DialogContainer
        // loads a new view. This reliably catches all full-page redirects and popup dialogs (like SMS/Email failures).
        let isInitialLoad = true;
        setTimeout(() => isInitialLoad = false, 1500);

        const actionObserver = new MutationObserver((mutations) => {
            if (isInitialLoad) return; // Ignore initial DOM rendering
            const fullscreenMenu = document.querySelector(".dropdown-menu.fullscreen-menu.show");
            if (!fullscreenMenu) return; // Only process if App Launcher is open
            
            for (let m of mutations) {
                if (m.addedNodes.length > 0) {
                    const target = m.target;
                    if (target.classList && (target.classList.contains('o_action_manager') || target.classList.contains('o_dialog_container'))) {
                        fullscreenMenu.classList.remove("show");
                        sessionStorage.setItem('app_launcher_open', 'false');
                        const navbar = document.querySelector('.o_main_navbar');
                        if (navbar) navbar.classList.remove('app-launcher-open');
                        document.body.classList.remove('app-launcher-open');
                        return;
                    }
                }
            }
        });
        actionObserver.observe(document.body, { childList: true, subtree: true });

        // Robust fallback: Close App Launcher immediately if any actionable item is clicked anywhere.
        // Odoo 17/19 Systray dropdowns are Popovers attached to document.body, so we can't restrict by .o_menu_systray.
        document.addEventListener('click', (ev) => {
            const fullscreenMenu = document.querySelector(".dropdown-menu.fullscreen-menu.show");
            if (fullscreenMenu) {
                const isAction = ev.target.closest('.dropdown-item, .list-group-item, .btn-link, .o-mail-NotificationItem, .o-mail-ActivityGroup');
                const inMessagingMenu = ev.target.closest('.o-mail-MessagingMenu');
                const inChatWindow = ev.target.closest('.o-mail-ChatWindow');
                const inReminderMenu = ev.target.closest('.reminder-dropdown');
                
                // If the click is an action but it's inside the Messaging menu, Chat Window, OR Reminder Menu, 
                // DO NOT close the App Launcher!
                if (isAction && !inMessagingMenu && !inChatWindow && !inReminderMenu) {
                    fullscreenMenu.classList.remove("show");
                    sessionStorage.setItem('app_launcher_open', 'false');
                    const navbar = document.querySelector('.o_main_navbar');
                    if (navbar) navbar.classList.remove('app-launcher-open');
                    document.body.classList.remove('app-launcher-open');
                }
            }

            // --- APP TRANSITION LOADING OVERLAY ---
            // Instantly clear the old app view when clicking a top nav entry or app launcher item to prevent the old view from "flashing".
            const isAppNavigation = ev.target.closest('.o_app') || 
                                   (ev.target.closest('.o_nav_entry') && !ev.target.closest('.dropdown-toggle')) || 
                                   ev.target.closest('.o_menu_brand');
            
            if (isAppNavigation) {
                // Ignore middle clicks or clicks with modifiers (which open new tabs)
                if (ev.button === 1 || ev.ctrlKey || ev.metaKey || ev.shiftKey || (ev.target.tagName === 'A' && ev.target.target === '_blank')) {
                    return;
                }
                
                const actionManager = document.querySelector('.o_action_manager');
                const oldContent = document.querySelector('.o_content');
                if (actionManager && !document.getElementById('ohrms-global-loading-overlay')) {
                    const overlay = document.createElement('div');
                    overlay.id = 'ohrms-global-loading-overlay';
                    overlay.style.position = 'absolute';
                    overlay.style.top = '0';
                    overlay.style.left = '0';
                    overlay.style.width = '100%';
                    overlay.style.height = '100%';
                    overlay.style.backgroundColor = '#F8FAFC'; // Soft white background to match theme
                    overlay.style.zIndex = '5'; // Keep below the top navbar (which is usually z-index 10 or 1030)
                    overlay.style.display = 'flex';
                    overlay.style.alignItems = 'center';
                    overlay.style.justifyContent = 'center';
                    overlay.innerHTML = '<i class="fa fa-circle-o-notch fa-spin fa-3x fa-fw" style="color: #1B5298;"></i>';
                    
                    // Odoo's ActionManager completely destroys and replaces its child DOM when the new view is ready.
                    // By appending our overlay to the top-level view wrapper (actionManager.firstElementChild), 
                    // we cover BOTH the data area AND the old control panel (search bar, buttons).
                    const targetToMask = actionManager.firstElementChild;
                    if (targetToMask) {
                        // Ensure relative positioning so the absolute overlay is contained within this element
                        const originalPosition = window.getComputedStyle(targetToMask).position;
                        if (originalPosition === 'static') {
                            targetToMask.style.position = 'relative';
                        }
                        targetToMask.appendChild(overlay);
                    }
                }
            }
        }, { capture: true });
    },

    _onMenuClick(ev) {
        ev.preventDefault();
        const liEl = ev.currentTarget.closest("li");
        const menuEl = liEl.querySelector(".dropdown-menu");
        
        // Prevent Bootstrap from natively closing the dropdown when clicking outside (e.g. on Chat icon)
        ev.currentTarget.setAttribute('data-bs-auto-close', 'false');
        
        menuEl.classList.toggle("show");
        const isShow = menuEl.classList.contains("show");
        sessionStorage.setItem('app_launcher_open', isShow);
        const navbar = document.querySelector('.o_main_navbar');
        if (navbar) navbar.classList.toggle('app-launcher-open', isShow);
        document.body.classList.toggle('app-launcher-open', isShow);
    },

    _closeFullMenu(ev) {
        const dropdownMenu = ev.currentTarget.closest(".dropdown-menu");
        if (dropdownMenu) {
            dropdownMenu.classList.remove("show");
            sessionStorage.setItem('app_launcher_open', 'false');
            const navbar = document.querySelector('.o_main_navbar');
            if (navbar) navbar.classList.remove('app-launcher-open');
            document.body.classList.remove('app-launcher-open');
        }
    },

    openCustomSearch(ev, initialQuery = "") {
        if (ev) ev.preventDefault();
        this.state.isSearchOpen = true;
        this.state.activeIndex = 0;
        this._searchMenus();
        // Focus and clear the modal search input after it renders
        setTimeout(() => {
            if (this.search_input.el) {
                this.search_input.el.value = typeof initialQuery === 'string' ? initialQuery : "";
                this.search_input.el.focus();
                if (typeof initialQuery === 'string' && initialQuery.length > 0) {
                    this._searchMenusSchedule();
                }
            }
        }, 50);
    },

    closeCustomSearch(ev) {
        this.state.isSearchOpen = false;
        // If a link was clicked, close the main App Launcher as well
        if (ev && ev.currentTarget && ev.currentTarget.tagName === 'A') {
            const dropdownMenu = document.querySelector(".dropdown-menu.fullscreen-menu.show");
            if (dropdownMenu) {
                dropdownMenu.classList.remove("show");
                sessionStorage.setItem('app_launcher_open', 'false');
                const navbar = document.querySelector('.o_main_navbar');
                if (navbar) navbar.classList.remove('app-launcher-open');
                document.body.classList.remove('app-launcher-open');
            }
        }
    },

    closeCustomSearchIfOutside(ev) {
        if (ev.target.classList.contains('custom-search-overlay')) {
            this.closeCustomSearch();
        }
    },

    onSearchKeyDown(ev) {
        if (!this.state.isSearchOpen || !this.state.results.length) return;

        if (ev.key === 'ArrowDown') {
            ev.preventDefault();
            this.state.activeIndex = Math.min(this.state.activeIndex + 1, this.state.results.length - 1);
            this._scrollToActiveItem();
        } else if (ev.key === 'ArrowUp') {
            ev.preventDefault();
            this.state.activeIndex = Math.max(this.state.activeIndex - 1, 0);
            this._scrollToActiveItem();
        } else if (ev.key === 'Enter') {
            ev.preventDefault();
            const selected = this.state.results[this.state.activeIndex];
            if (selected) {
                this.state.isSearchOpen = false;
                const dropdownMenu = document.querySelector(".dropdown-menu.fullscreen-menu.show");
                if (dropdownMenu) {
                    dropdownMenu.classList.remove("show");
                    sessionStorage.setItem('app_launcher_open', 'false');
                    const navbar = document.querySelector('.o_main_navbar');
                    if (navbar) navbar.classList.remove('app-launcher-open');
                    document.body.classList.remove('app-launcher-open');
                }
                
                const menu = this.menuService.getMenu(selected.id);
                if (menu) {
                    this.menuService.selectMenu(menu);
                }
            }
        }
    },

    _scrollToActiveItem() {
        setTimeout(() => {
            const container = document.querySelector('.custom-search-results');
            const activeEl = document.querySelector('.custom-search-item.active');
            if (container && activeEl) {
                activeEl.scrollIntoView({ block: 'nearest' });
            }
        }, 10);
    },

    _searchMenusSchedule() {
        this._search_def.reject();
        this._search_def = $.Deferred();
        setTimeout(this._search_def.resolve.bind(this._search_def), 50);
        this._search_def.done(this._searchMenus.bind(this));
    },
    
    _searchMenus() {
        var query = this.search_input.el ? this.search_input.el.value : "";
        var results = [];
        
        if (query === "") {
            // Show all apps by default
            this._apps.forEach((menu) => {
                results.push({
                    category: "apps",
                    name: menu.label,
                    actionID: menu.actionID,
                    id: menu.id,
                    webIconData: menu.webIconData ? menu.webIconData.split(',')[1] : null,
                });
            });
            this.state.results = results;
            this.state.activeIndex = 0;
            return;
        }

        fuzzyLookup(query, this._apps, (menu) => menu.label)
        .forEach((menu) => {
            results.push({
                category: "apps",
                name: menu.label,
                actionID: menu.actionID,
                id: menu.id,
                webIconData: menu.webIconData ? menu.webIconData.split(',')[1] : null,
            });
        });
        fuzzyLookup(query, this._searchableMenus, (menu) =>
            (menu.parents + " / " + menu.label).split("/").reverse().join("/"))
        .forEach((menu) => {
            results.push({
                category: "menu_items",
                name: menu.parents + " / " + menu.label,
                actionID: menu.actionID,
                id: menu.id,
            });
        });
        this.state.results = results;
        this.state.activeIndex = 0;
    }
});
