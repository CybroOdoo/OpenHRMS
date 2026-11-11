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
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrFlightTicket(models.Model):
    """Model representing flight tickets for employees."""
    _name = 'hr.flight.ticket'
    _description = 'HR Flight Ticket'

    name = fields.Char(string='Sequence No', readonly=True,
                       default=lambda self: _('New'),
                       copy=False,
                       help="Sequence number of Flight Ticket")
    employee_id = fields.Many2one('hr.leave', string='Employee',
                                  required=True, help="Name of the employee")
    ticket_type = fields.Selection(
        [('one', 'One Way'), ('round', 'Round Trip')],
        string='Ticket Type', default='round', help="Select the ticket type")
    depart_from = fields.Char(string='Departure', required=True,
                              help="Specify the departure place.")
    destination = fields.Char(string='Destination', required=True,
                              help="Specify the destination place.")
    date_start = fields.Date(string='Start Date', required=True,
                             help="Start date of the travel.")
    date_return = fields.Date(string='Return Date', help="Return date ")
    ticket_class = fields.Selection([('economy', 'Economy'),
                                     ('premium_economy', 'Premium Economy'),
                                     ('business', 'Business'),
                                     ('first_class', 'First Class')],
                                    string='Class',
                                    help="Select the ticket class")
    ticket_fare = fields.Float(string='Ticket Fare',
                               help="Give the ticket fare")
    flight_details = fields.Text(string='Flight Details',
                                 help="Flight details of the employee.")
    return_flight_details = fields.Text(string='Return Flight Details',
                                        help="Details of return flight ")
    state = fields.Selection([('booked', 'Booked'),
                              ('confirmed', 'Confirmed'),
                              ('started', 'Started'),
                              ('completed', 'Completed'),
                              ('canceled', 'Canceled')], string='Status',
                             default='booked',
                             help='States of the flight ticket. ')
    invoice_id = fields.Many2one('account.move', string='Invoice',
                                 help="Invoice of the employee")
    leave_id = fields.Many2one('hr.leave', string='Leave',
                               help="Leave of the employee.")
    company_id = fields.Many2one('res.company', 'Company',
                                 help="Company of the employee.",
                                 default=lambda self: self.env.user.company_id)

    @api.model_create_multi
    def create(self, vals_list):
        """Function declared for creating sequence Number for Flight Ticket"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.flight.ticket') or _('New')
        return super().create(vals_list)

    @api.constrains('date_start', 'date_return')
    def check_valid_date(self):
        """Constraint method 'check_valid_date' for the model, validating
         the consistency of flight ticket dates."""
        if self.filtered(
                lambda c: c.date_return and c.date_start > c.date_return):
            raise ValidationError(
                _('Flight travelling start date must be less than flight'
                  ' return date.'))

    def action_confirm_ticket(self):
        """This method confirms the flight ticket and generates an
         invoice for the ticket fare."""
        product_id = self.env['product.product'].search(
            [("name", "=", "Flight Ticket")], limit=1)
        if self.ticket_fare <= 0:
            raise UserError(_('Please add ticket fare.'))
        expense_account_id = self.env['ir.config_parameter'].sudo().get_int('hr_vacation_mngmt.expense_id')
        if not expense_account_id:
            raw_param = self.env['ir.config_parameter'].sudo().get_str('hr_vacation_mngmt.expense_id')
            if raw_param and raw_param.isdigit():
                expense_account_id = int(raw_param)
        if not expense_account_id:
            raise UserError(
                _('Please select expense account for the flight tickets.'))
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'purchase'),
             ('company_id', '=', self.company_id.id)], limit=1)
        partner = self.env.ref('hr_vacation_mngmt.res_partner_data_airlines')
        date_due = fields.Date.context_today(self)
        inv_vals = {
            'move_type': 'in_invoice',
            'journal_id': journal_id.id if journal_id else False,
            'invoice_date': fields.Date.context_today(self),
            'invoice_date_due': date_due,
            'partner_id': partner.id,
            'state': 'draft',
            'invoice_line_ids': [fields.Command.create({
                'name': 'Flight Ticket',
                'price_unit': self.ticket_fare,
                'quantity': 1.0,
                'account_id': expense_account_id,
                'product_id': product_id.id if product_id else False,
            })],
        }
        inv_id = self.env['account.move'].create(inv_vals)
        self.write({'state': 'confirmed', 'invoice_id': inv_id.id})

    def action_cancel_ticket(self):
        """This method cancels the flight ticket,
        updating its state to 'canceled'. If the ticket is in the 'booked'
        state, it is directly marked as 'canceled'. If the ticket is in the
        'confirmed' state, it checks the associated invoice's state."""
        if self.state == 'booked':
            self.write({'state': 'canceled'})
        elif self.state == 'confirmed':
            if self.invoice_id and self.invoice_id.state == 'draft':
                self.write({'state': 'canceled'})
            elif self.invoice_id and self.invoice_id.state in ('posted', 'open'):
                self.invoice_id.button_cancel()
                self.write({'state': 'canceled'})
            else:
                self.write({'state': 'canceled'})

    @api.model
    def run_update_ticket_status(self):
        """This model method is designed to be scheduled and automatically
         updates the state of flight tickets based on their current status
         and relevant date conditions."""
        today = fields.Date.today()
        run_out_tickets = self.search(
            [('state', 'in', ['confirmed', 'started']),
             ('date_return', '<=', today)])
        confirmed_tickets = self.search(
            [('state', '=', 'confirmed'), ('date_start', '<=', today),
             ('date_return', '>', today)])
        run_out_tickets.write({'state': 'completed'})
        confirmed_tickets.write({'state': 'started'})

    def action_view_invoice(self):
        """This method opens the view for the associated invoice of the
         flight ticket."""
        return {
            'name': _('Flight Ticket Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'type':'in_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
        }

    def action_book_ticket(self):
        """It returns an action to close the current window."""
        return {
            'type': 'ir.actions.act_window_close'
        }
