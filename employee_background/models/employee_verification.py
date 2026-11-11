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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EmployeeVerification(models.Model):
    """Creates the model Employee Verification"""
    _name = 'employee.verification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Verification"
    _rec_name = 'name'
    _rec_names_search = ('name', 'employee_id.name')

    # -------------------------------------------------------------------------
    # FIELDS DECLARATION
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        help="Verification Reference",
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('assign', 'Assigned'),
            ('submit', 'Verification Completed'),
        ],
        string='Status',
        default='draft',
        help="State for the Employee Verification",
    )
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        help='You can choose the employee for background verification',
    )
    agency_id = fields.Many2one(
        'res.partner',
        domain=[('verification_agent', '=', True)],
        help='You can choose a Verification Agent',
    )
    assigned_id = fields.Many2one(
        'res.users',
        string='Assigned By',
        readonly=True,
        default=lambda self: self.env.uid,
        help="Assigned Login User",
    )
    assigned_date = fields.Date(
        readonly=True,
        default=fields.Date.context_today,
        help="Record Assigned Date",
    )
    expected_date = fields.Date(
        help='Expected date of completion of background verification',
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        help="Company of the current record",
    )
    resume_ids = fields.Many2many(
        'ir.attachment',
        string="Resume of Applicant",
        help='You can attach the copy of your document',
        copy=False,
    )
    agency_attachment_ids = fields.Many2many(
        'ir.attachment',
        'agency_attachments_rel',
        'verification',
        'attachment',
        help='Attachment from the agency',
        copy=False,
        readonly=True,
    )
    description_by_agency = fields.Char(
        string='Description',
        readonly=True,
        help="Description by agency",
    )

    # Related Employee Address Fields
    address_id = fields.Many2one(
        related='employee_id.address_id',
        string='Work Address',
        readonly=False,
        help="Work address of the employee",
    )
    private_street = fields.Char(
        related='employee_id.private_street',
        string='Private Street',
        readonly=False,
        help="Private street address of the employee",
    )
    private_street2 = fields.Char(
        related='employee_id.private_street2',
        string='Private Street2',
        readonly=False,
        help="Private street2 address of the employee",
    )
    private_city = fields.Char(
        related='employee_id.private_city',
        string='Private City',
        readonly=False,
        help="Private city of the employee",
    )
    private_state_id = fields.Many2one(
        related='employee_id.private_state_id',
        string='Private State',
        readonly=False,
        help="Private state of the employee",
    )
    private_zip = fields.Char(
        related='employee_id.private_zip',
        string='Private Zip',
        readonly=False,
        help="Private zip of the employee",
    )
    private_country_id = fields.Many2one(
        related='employee_id.private_country_id',
        string='Private Country',
        readonly=False,
        help="Private country of the employee",
    )

    # Computed Candidate Address Fields
    candidate_street = fields.Char(
        string='Street',
        compute='_compute_candidate_address_display',
    )
    candidate_street2 = fields.Char(
        string='Street 2',
        compute='_compute_candidate_address_display',
    )
    candidate_city = fields.Char(
        string='City',
        compute='_compute_candidate_address_display',
    )
    candidate_state_id = fields.Many2one(
        'res.country.state',
        string='State',
        compute='_compute_candidate_address_display',
    )
    candidate_zip = fields.Char(
        string='Zip',
        compute='_compute_candidate_address_display',
    )
    candidate_country_id = fields.Many2one(
        'res.country',
        string='Country',
        compute='_compute_candidate_address_display',
    )
    has_candidate_address = fields.Boolean(
        compute='_compute_candidate_address_display',
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends(
        'employee_id.private_street',
        'employee_id.private_street2',
        'employee_id.private_city',
        'employee_id.private_state_id',
        'employee_id.private_zip',
        'employee_id.private_country_id',
        'address_id',
        'address_id.street',
        'address_id.city',
    )
    def _compute_candidate_address_display(self):
        """Compute candidate address display values from either the employee's
        private address or fallback to their work address."""
        for rec in self:
            emp = rec.sudo().employee_id
            if emp and (emp.private_street or emp.private_city):
                rec.candidate_street = emp.private_street
                rec.candidate_street2 = emp.private_street2
                rec.candidate_city = emp.private_city
                rec.candidate_state_id = emp.private_state_id
                rec.candidate_zip = emp.private_zip
                rec.candidate_country_id = emp.private_country_id
                rec.has_candidate_address = True
            elif rec.address_id and (rec.address_id.street or rec.address_id.city):
                rec.candidate_street = rec.address_id.street
                rec.candidate_street2 = rec.address_id.street2
                rec.candidate_city = rec.address_id.city
                rec.candidate_state_id = rec.address_id.state_id
                rec.candidate_zip = rec.address_id.zip
                rec.candidate_country_id = rec.address_id.country_id
                rec.has_candidate_address = True
            else:
                rec.candidate_street = False
                rec.candidate_street2 = False
                rec.candidate_city = False
                rec.candidate_state_id = False
                rec.candidate_zip = False
                rec.candidate_country_id = False
                rec.has_candidate_address = False

    # -------------------------------------------------------------------------
    # CONSTRAINS METHODS
    # -------------------------------------------------------------------------
    @api.constrains('expected_date', 'assigned_date')
    def onchange_expected_date(self):
        """Validate that the expected completion date is greater than or equal
        to the assigned date."""
        for record in self:
            if record.expected_date and record.assigned_date and (record.assigned_date > record.expected_date):
                raise ValidationError(self.env._("The expected date should be in the future compared to the assigned date."))

    # -------------------------------------------------------------------------
    # CRUD METHODS
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Supering the create method of the model Employee Verification and
        also adding verification_id into the vals for creating the record."""
        for vals in vals_list:
            seq = self.env['ir.sequence'].next_by_code('employee.verification') or '/'
            vals['name'] = seq
        return super().create(vals_list)

    def _check_can_unlink(self):
        """Prevent deleting records that are not in draft state."""
        for record in self:
            if record.state != 'draft':
                raise UserError(self.env._('You cannot delete the verification created.'))

    def unlink(self):
        """Supering the unlink method of the model Employee Verification."""
        self._check_can_unlink()
        return super().unlink()

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_assign_statusbar(self):
        """Method action_assign_statusbar will assign the verification
        of the contact to an agency and mail to agency."""
        if self.agency_id:
            if self.has_candidate_address or self.resume_ids:
                for file in self.resume_ids:
                    file.public = True
                self.state = 'assign'
                template = self.env.ref('employee_background.assign_agency_email_template')
                template.send_mail(self.id, force_send=True)
            else:
                raise UserError(
                    self.env._("There should be at least address or resume of the employee."))
        else:
            raise UserError(
                self.env._("Agency is not assigned. Please select one of the Agency."))
