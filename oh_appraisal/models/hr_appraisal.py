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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrAppraisal(models.Model):
    """Model representing an Employee Appraisal."""
    _name = 'hr.appraisal'
    _inherit = 'mail.thread'
    _description = 'HR Appraisal'
    _rec_name = 'employee_id'

    # -------------------------------------------------------------------------
    # DEFAULT METHODS
    # -------------------------------------------------------------------------

    def _default_stage_id(self):
        """Retrieve the default initial stage for a newly created appraisal."""
        rec = self.env['hr.appraisal.stages'].search([], limit=1, order='sequence ASC')
        return rec.id if rec else None

    def _default_employee_id(self):
        """Set the default employee to the currently logged-in user's employee."""
        return self.env.user.employee_id.id or False

    # -------------------------------------------------------------------------
    # FIELDS DECLARATION
    # -------------------------------------------------------------------------

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        default=_default_employee_id,
        help="Employee undergoing the appraisal"
    )
    is_appraisal_manager = fields.Boolean(
        string="Is Appraisal Manager",
        compute="_compute_is_appraisal_manager",
        help="Technical field indicating if current user is an appraisal manager or HR officer"
    )
    employee_autocomplete_ids = fields.Many2many(
        'hr.employee',
        compute='_compute_employee_autocomplete',
        compute_sudo=True,
        string="Available Employees",
        help="Employees available for selection based on the user's access rights"
    )
    appraisal_deadline = fields.Date(
        string="Appraisal Deadline",
        required=True,
        help="Deadline date of the appraisal"
    )
    final_interview = fields.Date(
        string="Final Interview",
        help="Date scheduled for the final appraisal interview"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help="Company of the current appraisal record"
    )
    hr_manager = fields.Boolean(
        string="Manager",
        default=False,
        help="Whether the manager needs to attend the survey"
    )
    hr_emp = fields.Boolean(
        string="Employee",
        default=False,
        help="Whether the employee needs to attend the survey"
    )
    hr_collaborator = fields.Boolean(
        string="Collaborators",
        default=False,
        help="Whether collaborators need to attend the survey"
    )
    hr_colleague = fields.Boolean(
        string="Colleague",
        default=False,
        help="Whether colleagues need to attend the survey"
    )
    hr_manager_ids = fields.Many2many(
        'hr.employee',
        'manager_appraisal_rel',
        string="Select Managers",
        help="Managers selected to attend the appraisal survey"
    )
    hr_colleague_ids = fields.Many2many(
        'hr.employee',
        'colleagues_appraisal_rel',
        string="Select Colleagues",
        help="Colleagues selected to attend the appraisal survey"
    )
    hr_collaborator_ids = fields.Many2many(
        'hr.employee',
        'collaborators_appraisal_rel',
        string="Select Collaborators",
        help="Collaborators selected to review the employee"
    )
    manager_survey_id = fields.Many2one(
        'survey.survey',
        string="Select Managers Opinion Form",
        help="Survey template to send to the manager"
    )
    emp_survey_id = fields.Many2one(
        'survey.survey',
        string="Select Appraisal Form",
        help="Survey template to send to the employee"
    )
    collaborator_survey_id = fields.Many2one(
        'survey.survey',
        string="Select Collaborator Opinion Form",
        help="Survey template to send to the collaborator"
    )
    colleague_survey_id = fields.Many2one(
        'survey.survey',
        string="Select Colleague Opinion Form",
        help="Survey template to send to the colleague"
    )
    response_id = fields.Many2one(
        'survey.user_input',
        string="Response",
        ondelete="set null",
        help="User response received for the appraisal survey"
    )
    final_evaluation = fields.Text(
        string="Final Evaluation",
        help="Final evaluation notes recorded after the appraisal"
    )
    app_period_from = fields.Datetime(
        string="From",
        required=True,
        readonly=True,
        default=fields.Datetime.now,
        help="Appraisal period starting date"
    )
    tot_sent_survey = fields.Integer(
        string="Count Sent Questions",
        help="Number of sent survey invitations"
    )
    tot_comp_survey = fields.Integer(
        string="Count Answers",
        compute="_compute_completed_survey",
        help="Number of completed survey answers received"
    )
    creater_id = fields.Many2one(
        'res.users',
        string="Created By",
        default=lambda self: self.env.uid,
        help="User who created this appraisal"
    )
    stage_id = fields.Many2one(
        'hr.appraisal.stages',
        string='Stage',
        tracking=True,
        index=True,
        default=lambda self: self._default_stage_id(),
        group_expand='_read_group_stage_ids',
        help="Current stage of the appraisal process"
    )
    color = fields.Integer(string="Color Index", help="Color index for stage/kanban display")
    check_sent = fields.Boolean(
        string="Check Sent Mail",
        copy=False,
        help="Flag set to true when the appraisal has been started and emails sent"
    )
    check_draft = fields.Boolean(
        string="Check Draft",
        default=True,
        copy=False,
        help="Flag set to true when the appraisal is in draft stage"
    )
    check_cancel = fields.Boolean(
        string="Check Cancel",
        copy=False,
        help="Flag set to true when the appraisal has been cancelled"
    )
    check_done = fields.Boolean(
        string="Check Done",
        copy=False,
        help="Flag set to true when the appraisal is marked as done"
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    def _compute_is_appraisal_manager(self):
        """Determine whether the current user has appraisal manager or HR officer privileges."""
        is_manager = (
            self.env.user.has_group('oh_appraisal.oh_appraisal_group_manager') or
            self.env.user.has_group('hr.group_hr_user')
        )
        for rec in self:
            rec.is_appraisal_manager = is_manager

    @api.depends_context('uid')
    def _compute_employee_autocomplete(self):
        """Compute the selectable employees: only self for regular employees, all for managers."""
        is_manager = (
            self.env.user.has_group('oh_appraisal.oh_appraisal_group_manager') or
            self.env.user.has_group('hr.group_hr_user')
        )
        if is_manager:
            employees = self.env['hr.employee'].search([])
        else:
            employees = self.env.user.employee_id
        for rec in self:
            rec.employee_autocomplete_ids = employees

    def _compute_completed_survey(self):
        """Compute the total count of completed survey responses linked to this appraisal."""
        for rec in self:
            rec.tot_comp_survey = self.env['survey.user_input'].search_count(
                [('state', '=', 'done'), ('appraisal_id', '=', rec.id)]
            )

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------

    @api.constrains('appraisal_deadline')
    def _check_appraisal_deadline(self):
        """Validate that the appraisal deadline is not in the past."""
        today = fields.Date.today()
        for rec in self:
            if rec.appraisal_deadline and rec.appraisal_deadline <= today:
                raise ValidationError(_("Appraisal deadline needs to be greater than today"))

    @api.constrains('employee_id')
    def _check_employee_id(self):
        """Ensure that regular employees can only create or edit appraisals for themselves."""
        is_manager = (
            self.env.user.has_group('oh_appraisal.oh_appraisal_group_manager') or
            self.env.user.has_group('hr.group_hr_user')
        )
        if not is_manager:
            for rec in self:
                if rec.employee_id and self.env.user.employee_id and rec.employee_id != self.env.user.employee_id:
                    raise ValidationError(_("As an employee, you can only create appraisals for yourself."))

    # -------------------------------------------------------------------------
    # CRUD & ORM OVERRIDES
    # -------------------------------------------------------------------------

    @api.model
    def _read_group_stage_ids(self, categories, domain):
        """Read all stages to display all columns in the kanban view even if empty."""
        category_ids = categories._search([], order=categories._order)
        return categories.browse(category_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure the initial stage defaults to sequence 0 (draft)."""
        default_stage = self.env['hr.appraisal.stages'].search([('sequence', '=', 0)], limit=1)
        if default_stage:
            for vals in vals_list:
                if not vals.get('stage_id'):
                    vals['stage_id'] = default_stage.id
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # ACTION & BUSINESS METHODS
    # -------------------------------------------------------------------------

    def action_start_appraisal(self):
        """Start the appraisal by sending email invitations and survey links to reviewers."""
        self.ensure_one()
        send_count = 0
        appraisal_reviewers_list = self.fetch_appraisal_reviewer()
        baseurl = self.env['ir.config_parameter'].sudo().get_str('web.base.url')
        for appraisal_reviewers, survey_id in appraisal_reviewers_list:
            for reviewers in appraisal_reviewers:
                partner = reviewers.user_id.partner_id if reviewers.user_id else False
                response = survey_id.sudo()._create_answer(
                    survey_id=survey_id.id,
                    deadline=self.appraisal_deadline,
                    partner=partner,
                    email=reviewers.work_email,
                    appraisal_id=self.id
                )
                url = response.get_start_url()
                reviewer_name = reviewers.name or ''
                employee_name = self.employee_id.name or ''
                mail_content = (
                    f"Dear {reviewer_name},<br>"
                    f"Please fill out the following survey related to {employee_name}<br>"
                    f"Click here to access the survey.<br>{baseurl}{url}<br>"
                    f"Post your response for the appraisal till : {self.appraisal_deadline}"
                )
                values = {
                    'model': 'hr.appraisal',
                    'res_id': self.id,
                    'subject': survey_id.title,
                    'body_html': mail_content,
                    'parent_id': None,
                    'email_from': self.env.user.email or None,
                    'auto_delete': True,
                    'email_to': reviewers.work_email,
                }
                mail = self.env['mail.mail'].sudo().create(values)
                mail.send()
                send_count += 1

        self.write({'tot_sent_survey': send_count})
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 1)], limit=1)
        if rec:
            self.stage_id = rec.id
        self.check_sent = True
        self.check_draft = False

    def action_done(self):
        """Set the appraisal stage to Done."""
        self.ensure_one()
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 2)], limit=1)
        if rec:
            self.stage_id = rec.id
        self.check_done = True
        self.check_draft = False
        self.check_sent = False
        self.check_cancel = False

    def action_set_draft(self):
        """Reset the appraisal stage back to Draft (sequence 0)."""
        self.ensure_one()
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 0)], limit=1)
        if rec:
            self.stage_id = rec.id
        self.check_draft = True
        self.check_sent = False
        self.check_done = False
        self.check_cancel = False

    def action_cancel(self):
        """Set the appraisal stage to Cancelled (sequence 3)."""
        self.ensure_one()
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 3)], limit=1)
        if rec:
            self.stage_id = rec.id
        self.check_cancel = True
        self.check_draft = False
        self.check_sent = False
        self.check_done = False

    def action_get_answers(self):
        """Return an act_window action to view all completed survey answers for this appraisal."""
        self.ensure_one()
        tree_id = self.env['ir.model.data']._xmlid_to_res_id(
            'survey.survey_user_input_view_tree') or False
        form_id = self.env['ir.model.data']._xmlid_to_res_id(
            'survey.survey_user_input_view_form') or False
        return {
            'model': 'ir.actions.act_window',
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'survey.user_input',
            'views': [(tree_id, 'list'), (form_id, 'form')],
            'domain': [('state', '=', 'done'),
                       ('appraisal_id', '=', self.id)],
        }

    def fetch_appraisal_reviewer(self):
        """Gather all appraisal reviewers and their corresponding surveys based on configuration."""
        self.ensure_one()
        appraisal_reviewers = []
        if self.hr_manager and self.hr_manager_ids and self.manager_survey_id:
            appraisal_reviewers.append(
                (self.hr_manager_ids, self.manager_survey_id))
        if self.hr_emp and self.emp_survey_id:
            appraisal_reviewers.append((self.employee_id, self.emp_survey_id))
        if self.hr_collaborator and self.hr_collaborator_ids and self.collaborator_survey_id:
            appraisal_reviewers.append(
                (self.hr_collaborator_ids, self.collaborator_survey_id))
        if self.hr_colleague and self.hr_colleague_ids and self.colleague_survey_id:
            appraisal_reviewers.append(
                (self.hr_colleague_ids, self.colleague_survey_id))
        return appraisal_reviewers
