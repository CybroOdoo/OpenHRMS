# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models


class Settings(models.TransientModel):
    """Inheriting config settings to add menu order management"""
    _inherit = 'res.config.settings'

    order_menu = fields.Boolean(default=False, string='Order Menu Alphabets',
                                help="Order the menus in alphabetic order")

    @api.model
    def get_values(self):
        """ Get values for fields in the settings
         and assign the value to the fields"""
        res = super(Settings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        order_menu = params.get_bool('order_menu', default=False)
        res.update(
            order_menu=order_menu,
        )
        return res

    def set_values(self):
        """ save values in  the settings fields"""
        super(Settings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_bool(
            "order_menu", self.order_menu)
        self._update_menu_order(self.order_menu)

    @api.onchange('order_menu')
    def onchange_order_menu(self):
        """Change order of menus"""
        self._update_menu_order(self.order_menu)
        return False

    def _update_menu_order(self, order_alphabetical):
        """Change order of root menus alphabetically or revert to original order"""
        menus = self.env['ir.ui.menu'].sudo().search([
            ('parent_id', '=', False),
            ('name', 'not in', ('Apps', 'Settings', 'Dashboard')),
        ])
        if order_alphabetical:
            sorted_menus = menus.sorted(key=lambda m: (m.name or '').lower())
            sqno = 1
            for menu in sorted_menus:
                if not menu.order_changed:
                    menu.recent_menu_sequence = menu.sequence
                    menu.order_changed = True
                menu.sequence = sqno
                sqno += 1
        else:
            for menu in menus:
                if menu.order_changed:
                    if menu.recent_menu_sequence:
                        menu.sequence = menu.recent_menu_sequence
                    menu.recent_menu_sequence = 0
                    menu.order_changed = False
