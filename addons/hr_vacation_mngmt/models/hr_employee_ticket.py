# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrFlightTicket(models.Model):
    _name = 'hr.flight.ticket'

    name = fields.Char()
    employee_id = fields.Many2one('hr.leave', string='Employee', required=True, help="Employee")
    ticket_type = fields.Selection([('one', 'One Way'), ('round', 'Round Trip')], string='Ticket Type', default='round', help="Select the ticket type")
    depart_from = fields.Char(string='Departure', required=True, help="Departure")
    destination = fields.Char(string='Destination', required=True, help="Destination")
    date_start = fields.Date(string='Start Date', required=True, help="Start date")
    date_return = fields.Date(string='Return Date', help="Return date")
    ticket_class = fields.Selection([('economy', 'Economy'),
                                     ('premium_economy', 'Premium Economy'),
                                     ('business', 'Business'),
                                     ('first_class', 'First Class')], string='Class', help="Select the ticket class")
    ticket_fare = fields.Float(string='Ticket Fare', help="Give the ticket fare")
    flight_details = fields.Text(string='Flight Details', help="Flight details")
    return_flight_details = fields.Text(string='Return Flight Details', help="return flight details")
    state = fields.Selection([('booked', 'Booked'), ('confirmed', 'Confirmed'), ('started', 'Started'),
                              ('completed', 'Completed'), ('canceled', 'Canceled')], string='Status', default='booked')
    invoice_id = fields.Many2one('account.move', string='Invoice', help="Invoice")
    leave_id = fields.Many2one('hr.leave', string='Leave', help="Leave")
    company_id = fields.Many2one('res.company', 'Company', help="Company", default=lambda self: self.env.user.company_id)

    def name_get(self):
        res = []
        for ticket in self:
            res.append((ticket.id, _("Flight ticket for %s on %s to %s") % (
                ticket.employee_id.name, ticket.date_start, ticket.destination)))
        return res

    @api.constrains('date_start', 'date_return')
    def check_valid_date(self):
        if self.filtered(lambda c: c.date_return and c.date_start > c.date_return):
            raise ValidationError(_('Flight travelling start date must be less than flight return date.'))

    def book_ticket(self):
        return {'type': 'ir.actions.act_window_close'}

    def confirm_ticket(self):
        product_id = self.env['product.product'].search([("name", "=", "Flight Ticket")])
        if self.ticket_fare <= 0:
            raise UserError(_('Please add ticket fare.'))
        inv_obj = self.env['account.move']
        expense_account = self.env['ir.config_parameter'].sudo().get_param('travel_expense_account')
        if not expense_account:
            raise UserError(_('Please select expense account for the flight tickets.'))
        domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id),
        ]
        journal_id = self.env['account.journal'].search(domain, limit=1)
        partner = self.env.ref('hr_vacation_mngmt.air_lines_partner')
        if not partner.property_payment_term_id:
            date_due = fields.Date.context_today(self)
        else:
            pterm = partner.property_payment_term_id
            pterm_list = \
                pterm.with_context(currency_id=self.env.user.company_id.id).compute(
                    value=1, date_ref=fields.Date.context_today(self))[0]
            date_due = max(line[0] for line in pterm_list)
        inv_id = self.env['account.move'].create({
            'name': '/',
            'invoice_origin': 'Flight Ticket',
            'move_type': 'in_invoice',
            'journal_id': journal_id.id,
            # 'invoice_payment_term_id': partner.property_payment_term_id.id,
            'invoice_date_due': date_due,
            'ref': False,
            'partner_id': partner.id,
            # 'invoice_partner_bank_id': partner.property_account_payable_id.id,
            'state': 'draft',
            'invoice_line_ids': [(0, 0, {
                'name': 'Flight Ticket',
                'price_unit': self.ticket_fare,
                'quantity': 1.0,
                'account_id': int(expense_account),
                'product_id': product_id.id,
            })],
        })
        # inv_id.action_invoice_open()
        self.write({'state': 'confirmed', 'invoice_id': inv_id.id})

    def cancel_ticket(self):
        if self.state == 'booked':
            self.write({'state': 'canceled'})
        elif self.state == 'confirmed':
            if self.invoice_id and self.invoice_id.state == 'draft':
                self.write({'state': 'canceled'})
            if self.invoice_id and self.invoice_id.state == 'open':
                self.invoice_id.action_invoice_cancel()
                self.write({'state': 'canceled'})

    @api.model
    def run_update_ticket_status(self):
        run_out_tickets = self.search([('state', 'in', ['confirmed', 'started']),
                                       ('date_return', '<=', datetime.now())])
        confirmed_tickets = self.search([('state', '=', 'confirmed'), ('date_start', '<=', datetime.now()),
                                         ('date_return', '>', datetime.now())])
        for ticket in run_out_tickets:
            ticket.write({'state': 'completed'})
        for ticket in confirmed_tickets:
            ticket.write({'state': 'started'})

    def action_view_invoice(self):
        return {
            'name': _('Flight Ticket Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'type':'in_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
        }
