# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ranjith R(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
from odoo import api, fields, models


class HrRooms(models.Model):
    """Used to create room for company"""
    _name = "hr.rooms"
    _description = "Room"

    name = fields.Char(string="Room Number", readonly=True, copy=False,
                       default="New", help="Name of room")
    category = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string="Category", help="Category of Room",
        required=True)
    street = fields.Char(string="Street", help="Street where room is situated")
    street_near = fields.Char(string="Near by Street",
                              help="Near by Street where room is situated")
    zip = fields.Char(string="Zip", help="Zip of where room is situated",
                      change_default=True)
    city = fields.Char(string="City", help="City where room is situated")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               help="State where room is situated")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict',
                                 help="Country where room is situated")
    country_code = fields.Char(string="Country Code", related='country_id.code',
                               help="Field to fill country code")
    capacity = fields.Integer(string="Capacity", required=True, default="1",
                              help="Give the capacity of room here")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 help="Company of record belongs",
                                 default=lambda
                                     self: self.env.user.company_id.id)
    camp_id = fields.Many2one('hr.camps', string="Camp", required=True,
                              help="Camp on which the room")
    employee_ids = fields.One2many('hr.employee',
                                   'room_id', string="Employees",
                                   readonly=True,
                                   help="Employees on this room ")
    occupied = fields.Integer(string="Occupied",
                              compute="_compute_occupied_number_room",
                              help="Number of employees in the room ")
    available = fields.Integer(string="Available",
                               help="Number of vacancy in room")
    state = fields.Selection(
        [('available', 'Available'),
         ('not_available', 'Not Available')], string="State",
        default="not_available", help="State of room")

    @api.model
    def create(self, vals):
        """Function return sequence number for record"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.rooms') or 'New'
            return super(HrRooms, self).create(vals)

    def _compute_occupied_number_room(self):
        """ Function compute occupied bed in room """
        for room in self:
            room.occupied = self.env['hr.employee'].search_count(
                [('room_id', '=', room.id)])
            room.available = room.capacity - room.occupied

    def action_create_room(self):
        """Function to create a room and do the
           necessary functions like calculating capacity and occupied bed"""
        self.write({'state': 'available'})
        rooms = self.search([('camp_id', '=', self.camp_id.id)])
        self.camp_id.capacity = sum(rooms.mapped('capacity'))
        self.camp_id.occupied = sum(rooms.mapped('occupied'))
        self.camp_id.available = self.camp_id.capacity - self.camp_id.occupied
