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


class HrAllocationTransfer(models.Model):
    """ Classes to allocate or transfer room for employees"""
    _name = "hr.allocation.transfer"
    _description = "Room Transfer or Allocation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "sequence_number"

    sequence_number = fields.Char(string="Sequence Number", readonly=True,
                                  copy=False, default="New",
                                  help="Sequence number of record")
    employee_id = fields.Many2one('hr.employee',
                                  string="Select Employee", required=True,
                                  help="Choose employee for allocation of room")
    type = fields.Selection(
        [('transfer', 'Transfer'), ('allocation', 'Allocation')],
        default="allocation", string="Type", help="Type of allocation")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done')],
        default="draft", string="State", tracking=True,
        help="State of the allocation request")
    room_id = fields.Many2one('hr.rooms', string="Select Room",
                              required=True, tracking=True,
                              help="Room available to allocate")
    room_balance = fields.Integer(string="Available Space in this Room",
                                  related="room_id.available",
                                  help="Number of room available ")
    camp_id = fields.Many2one('hr.camps',
                              string="Select Camp for Allocation",
                              required=True, domain="[('available','>',0)]",
                              help="Camp where the allocation are created ")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, default=lambda
            self: self.env.user.company_id.id,
                                 help="Company of the record belongs to")
    date = fields.Date(string="Date", help="Date of allocation")
    room_ids = fields.Many2many('hr.rooms', string="Rooms",
                                compute="_compute_rooms",
                                help="Rooms under the selected camp")

    @api.model
    def create(self, vals):
        """ Function return sequence number for record"""
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code(
                'hr.allocation.transfer') or 'New'
            return super(HrAllocationTransfer, self).create(vals)

    @api.depends('camp_id')
    def _compute_rooms(self):
        """Function to find the rooms under the camp"""
        for rec in self:
            rec.write({'room_ids': [
                (6, 0, self.env['hr.rooms'].search(
                    [('camp_id', '=', self.camp_id.id),
                     ('state', '=', 'available')]).ids)]})

    def action_confirm(self):
        """Function to confirm the allocation and used to valuate type"""
        if not self.employee_id.room_id:
            self.write({'type': 'allocation'})
        else:
            self.write({'type': 'transfer'})
        self.write({'state': 'confirm'})

    def action_done(self):
        """Function to  convert  the allocation tage to done
         and change room and camp stage if it is not available"""
        if self.type == "transfer":
            self.employee_id.room_id.occupied = self.employee_id. \
                                                    room_id.occupied - 1
        self.employee_id.room_id = self.room_id.id
        if self.room_id.occupied == self.room_id.capacity:
            self.room_id.write(({'state': 'not_available'}))
        self.write({'state': 'done'})
