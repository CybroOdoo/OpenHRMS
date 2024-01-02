# -*- coding: utf-8 -*-
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
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
###############################################################################
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class HrAppraisal(models.Model):
    """Create the model Appraisal"""
    _name = 'hr.appraisal'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _description = 'HR Appraisal'

    @api.model
    def _read_group_stage_ids(self, categories, domain, order):
        """ Read all the stages and display it in the kanban view,
        even if it is empty."""
        category_ids = categories._search([], order=order,
                                          access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    def _default_stage_id(self):
        """Setting default stage"""
        rec = self.env['hr.appraisal.stages'].search([], limit=1,
                                                     order='sequence ASC')
        return rec.id if rec else None

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help="Employee name")
    appraisal_deadline = fields.Date(string="Appraisal Deadline", required=True,
                                     help="Deadline date of the appraisal")
    final_interview = fields.Date(string="Final Interview",
                                  help="After sending survey link,you can"
                                       " schedule final interview date")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 help="Company name of the current record")
    hr_manager = fields.Boolean(string="Manager", default=False,
                                help="Whether the manager needs to "
                                     "attend survey")
    hr_emp = fields.Boolean(string="Employee", default=False,
                            help="Whether the employee needs to attend survey")
    hr_collaborator = fields.Boolean(string="Collaborators", default=False,
                                     help="To mention collaborators for"
                                          " the survey")
    hr_colleague = fields.Boolean(string="Colleague", default=False,
                                  help="To mention colleagues for the survey")
    hr_manager_ids = fields.Many2many('hr.employee', 'manager_appraisal_rel',
                                      string="Select Managers",
                                      help="Managers to attend survey")
    hr_colleague_ids = fields.Many2many('hr.employee',
                                        'colleagues_appraisal_rel',
                                        string="Select Colleagues",
                                        help="Colleagues to attend survey")
    hr_collaborator_ids = fields.Many2many('hr.employee',
                                           'collaborators_appraisal_rel',
                                           string="Select Collaborators",
                                           help="Collaborators to review")
    manager_survey_id = fields.Many2one('survey.survey',
                                        string="Select Managers Opinion Form",
                                        help="Survey to send to the manager")
    emp_survey_id = fields.Many2one('survey.survey',
                                    string="Select Appraisal Form",
                                    help="Survey to send to the employee")
    collaborator_survey_id = fields.Many2one('survey.survey',
                                             string="Select Collaborator "
                                                    "Opinion Form",
                                             help="Survey to send to the "
                                                  "collaborator")
    colleague_survey_id = fields.Many2one('survey.survey',
                                          string="Select Colleague "
                                                 "Opinion Form",
                                          help="Survey to send to the "
                                               "colleague")
    response_id = fields.Many2one('survey.user_input', string="Response",
                                  ondelete="set null", oldname="response",
                                  help="Response from the user input")
    final_evaluation = fields.Text(string="Final Evaluation",
                                   help="Final evaluation after the appraisal")
    app_period_from = fields.Datetime(string="From", required=True,
                                      readonly=True,
                                      default=fields.Datetime.now(),
                                      help="From Date")
    tot_comp_survey = fields.Integer(string="Count Answers",
                                     compute="_compute_completed_survey",
                                     help="Number of Answers")
    tot_sent_survey = fields.Integer(string="Count Sent Questions",
                                     help="Number of Sent Questions")
    creater_id = fields.Many2one('res.users', string="Created By",
                                 default=lambda self: self.env.uid,
                                 help="User created appraisal")
    stage_id = fields.Many2one('hr.appraisal.stages', string='Stage',
                               track_visibility='onchange', index=True,
                               default=lambda self: self._default_stage_id(),
                               group_expand='_read_group_stage_ids',
                               help="Stage of the appraisal")
    color = fields.Integer(string="Color Index", help="Color of the stage")
    check_sent = fields.Boolean(string="Check Sent Mail", copy=False,
                                help="Will be true when the appraisal started")
    check_draft = fields.Boolean(string="Check Draft", default=True, copy=False,
                                 help="Will be true when the appraisal in "
                                      "draft state")
    check_cancel = fields.Boolean(string="Check Cancel", copy=False,
                                  help="Will be true when the appraisal is "
                                       "canceled")
    check_done = fields.Boolean(string="Check Done", copy=False,
                                help="Will be true when the appraisal is done")

    @api.constrains('appraisal_deadline')
    def _check_appraisal_deadline(self):
        """Method _check_appraisal_deadline to check whether the appraisal
        deadline given is in the past"""
        if self.appraisal_deadline <= fields.date.today() or self.appraisal_deadline == fields.date.today:
            raise ValidationError(_("Appraisal deadline needs "
                                    "to be greater than today"))

    def action_done(self):
        """Method action_done to make the appraisal into done state"""
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 3)])
        self.stage_id = rec.id
        self.check_done = True
        self.check_draft = False

    def action_set_draft(self):
        """Method action_set_draft to make the appraisal into draft state"""
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 1)])
        self.stage_id = rec.id
        self.check_draft = True
        self.check_sent = False

    def action_cancel(self):
        """Method action_cancel to make the appraisal into canceled state"""
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 4)])
        self.stage_id = rec.id
        self.check_cancel = True
        self.check_draft = False

    def fetch_appraisal_reviewer(self):
        """Method fetch_appraisal_reviewer to fetch all the appraisal
        reviewers"""
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

    def action_start_appraisal(self):
        """ This function will start the appraisal by sending emails to the
        corresponding employees specified in the appraisal"""
        send_count = 0
        appraisal_reviewers_list = self.fetch_appraisal_reviewer()
        for appraisal_reviewers, survey_id in appraisal_reviewers_list:
            for reviewers in appraisal_reviewers:
                baseurl = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                response = survey_id._create_answer(survey_id=survey_id.id,
                                                    deadline=self.appraisal_deadline,
                                                    partner=reviewers.user_id.partner_id,
                                                    email=reviewers.work_email,
                                                    appraisal_id=self.ids[0])
                url = response.get_start_url()
                mail_content = "Dear " + reviewers.name + "," + "<br>Please fill out the following survey " \
                                                                "related to " + self.employee_id.name + "<br>Click here to access the survey.<br>" + \
                               baseurl + str(
                    url) + "<br>Post your response for the appraisal till : " \
                               + str(self.appraisal_deadline)
                values = {'model': 'hr.appraisal', 'res_id': self.ids[0],
                          'subject': survey_id.title,
                          'body_html': mail_content, 'parent_id': None,
                          'email_from': self.env.user.email or None,
                          'auto_delete': True, 'email_to': reviewers.work_email}
                result = self.env['mail.mail'].sudo().create(values)._send()
                if result is True:
                    send_count += 1
                    self.write({'tot_sent_survey': send_count})
                    rec = self.env['hr.appraisal.stages'].search(
                        [('sequence', '=', 2)])
                    self.stage_id = rec.id
                    self.check_sent = True
                    self.check_draft = False

    def action_get_answers(self):
        """ This function will return all the answers posted related to
        this appraisal."""
        tree_id = self.env['ir.model.data']._xmlid_to_res_id(
            'survey.survey_user_input_view_tree') or False
        form_id = self.env['ir.model.data']._xmlid_to_res_id(
            'survey.survey_user_input_view_form') or False
        return {
            'model': 'ir.actions.act_window',
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'view_mode': 'form,tree',
            'res_model': 'survey.user_input',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('state', '=', 'done'),
                       ('appraisal_id', '=', self.ids[0])],
        }

    def _compute_completed_survey(self):
        """Method _compute_completed_survey will compute the completed survey"""
        for rec in self:
            answers = self.env['survey.user_input'].search(
                [('state', '=', 'done'), ('appraisal_id', '=', rec.id)])
            rec.tot_comp_survey = len(answers)
