# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrAnnouncementCategory(models.Model):
    """ Model representing Announcement Categories """
    _name = 'hr.announcement.category'
    _description = 'HR Announcement Category'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index", default=0)


class HrAnnouncement(models.Model):
    """ Model representing the HR Announcements"""
    _name = 'hr.announcement'
    _description = 'HR Announcement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Code No:',
                       help="Sequence of Announcement")
    announcement_reason = fields.Text(string='Title', required=True,
                                      help="Announcement subject")
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'Waiting For Approval'),
                   ('approved', 'Approved'), ('rejected', 'Refused'),
                   ('expired', 'Expired')],
        string='Status', default='draft', help="State of announcement.",
        tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    category_id = fields.Many2one('hr.announcement.category', string="Category")
    requested_date = fields.Date(string='Requested Date',
                                 default=fields.Datetime.now().
                                 strftime('%Y-%m-%d'),
                                 help="Create date of record")
    attachment_id = fields.Many2many(
        'ir.attachment', 'doc_warning_rel', 'doc_id', 'attach_id4',
        string="Attachment", help='Attach copy of your document')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Login user Company")
    is_announcement = fields.Boolean(string='Is general Announcement?',
                                     help="Enable, if this is a "
                                          "General Announcement")
    announcement_type = fields.Selection(
        [('employee', 'By Employee'), ('department', 'By Department'),
         ('job_position', 'By Job Position')], string="Announcement Type",
        help="By Employee: Announcement intended for specific Employees.\n"
             "By Department: Announcement intended for Employees in "
             "specific Departments.\n"
             "By Job Position: Announcement intended for Employees "
             "who are having specific Job Positions")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_announcements',
                                    'announcement', 'employee',
                                    string='Employees',
                                    help="Employees who want to see "
                                         "this announcement")
    department_ids = fields.Many2many('hr.department',
                                      'hr_department_announcements',
                                      'announcement', 'department',
                                      string='Departments',
                                      help="Department which can see "
                                           "this announcement")
    position_ids = fields.Many2many('hr.job', 'hr_job_position_announcements',
                                    'announcement', 'job_position',
                                    string='Job Positions',
                                    help="Position of the employee "
                                         "who is authorized "
                                         "to view this announcements.")
    announcement = fields.Html(string='Letter', help="Announcement message")
    date_start = fields.Date(string='Start Date', default=fields.Date.today(),
                             required=True, help="Start date of announcement")
    date_end = fields.Date(string='End Date', default=fields.Date.today(),
                           required=True, help="End date of announcement")
    acknowledged_employee_ids = fields.Many2many(
        'hr.employee', 'announcement_employee_ack_rel',
        'announcement_id', 'employee_id',
        string='Acknowledged Employees')
    has_acknowledged = fields.Boolean(
        string="Has Acknowledged", compute='_compute_has_acknowledged')

    def _compute_has_acknowledged(self):
        for record in self:
            if self.env.user.employee_id in record.acknowledged_employee_ids:
                record.has_acknowledged = True
            else:
                record.has_acknowledged = False

    def action_acknowledge(self):
        self.ensure_one()
        if self.env.user.employee_id:
            self.sudo().write({'acknowledged_employee_ids': [(4, self.env.user.employee_id.id)]})

    @api.constrains('date_start', 'date_end')
    def _check_date_start(self):
        """ Raise validation error when start date is greater than end date or in the past """
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise ValidationError(_("The Start Date must be earlier than the End Date."))
            if record.state in ['draft', 'to_approve'] and record.date_start and record.date_start < fields.Date.today():
                raise ValidationError(_("The Start Date cannot be set in the past."))

    @api.onchange('date_start', 'date_end')
    def _onchange_date_start(self):
        """ Provide instant UI validation when the user selects a date """
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise ValidationError(_("The Start Date must be earlier than the End Date."))
        if self.state in ['draft', 'to_approve'] and self.date_start and self.date_start < fields.Date.today():
            raise ValidationError(_("The Start Date cannot be set in the past."))

    @api.model
    def create(self, vals_list):
        """ Create method for HrAnnouncement model, adding sequence
        number to announcements. """

        # Ensure we always have a list of dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('is_announcement'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.announcement.general')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.announcement')

        return super(HrAnnouncement, self).create(vals_list)

    def write(self, vals):
        """ Override write to handle sequence regeneration if is_announcement changes """
        res = super(HrAnnouncement, self).write(vals)
        if 'is_announcement' in vals:
            for record in self:
                if record.state == 'draft':
                    if record.is_announcement:
                        new_name = self.env['ir.sequence'].next_by_code('hr.announcement.general')
                    else:
                        new_name = self.env['ir.sequence'].next_by_code('hr.announcement')
                    # Use a direct SQL update or sudo().write to avoid recursion if needed, 
                    # but simple write on another field is fine since 'is_announcement' is not in the new vals
                    super(HrAnnouncement, record).write({'name': new_name})
        return res

    def action_reject_announcement(self):
        """ Refuse button action """
        self.state = 'rejected'

    def action_approve_announcement(self):
        """ Approve button action and send email """
        self.state = 'approved'
        for announcement in self:
            template = self.env.ref('hr_reward_warning.mail_template_hr_announcement', raise_if_not_found=False)
            if template:
                # Get the targeted employees' emails
                employees = self.env['hr.employee']
                if announcement.is_announcement:
                    employees = self.env['hr.employee'].search([('company_id', '=', announcement.company_id.id)])
                elif announcement.announcement_type == 'employee':
                    employees = announcement.employee_ids
                elif announcement.announcement_type == 'department':
                    employees = self.env['hr.employee'].search([('department_id', 'in', announcement.department_ids.ids)])
                elif announcement.announcement_type == 'job_position':
                    employees = self.env['hr.employee'].search([('job_id', 'in', announcement.position_ids.ids)])

                email_values = {}
                if announcement.attachment_id:
                    email_values['attachment_ids'] = [(6, 0, announcement.attachment_id.ids)]
                    
                partner_ids = employees.mapped('work_contact_id').ids
                if not partner_ids:
                    partner_ids = employees.mapped('user_id.partner_id').ids
                    
                # Collect raw emails for any employee that somehow doesn't have a linked partner
                valid_emails = [emp.work_email for emp in employees if emp.work_email and not emp.work_contact_id and not emp.user_id]
                
                if partner_ids or valid_emails:
                    if partner_ids:
                        email_values['recipient_ids'] = [(6, 0, partner_ids)]
                    if valid_emails:
                        email_values['email_to'] = ','.join(valid_emails)
                        
                    template.send_mail(
                        announcement.id, 
                        force_send=True,
                        email_values=email_values
                    )
    def action_sent_announcement(self):
        """ 'Send For Approval' button action"""
        self.state = 'to_approve'

    def get_expiry_state(self):
        """
        Expire announcements based on their End date, triggered by a
        scheduled cron job.
        """
        announcements = self.search([('state', '!=', 'rejected')])
        for announcement in announcements:
            if announcement.date_end < fields.Date.today():
                announcement.write({
                    'state': 'expired'
                })

    @api.model
    def get_active_announcements(self):
        today = fields.Date.context_today(self)
        
        # Record rules will automatically filter announcements the user is not allowed to see
        announcements = self.search([
            ('state', '=', 'approved'),
            ('date_start', '<=', today),
            ('date_end', '>=', today)
        ], order='priority desc, date_start desc')
        
        # Filter out those not targeted at the user, and those already acknowledged
        result = []
        
        user_emps = self.env.user.employee_id
        user_emp_id = user_emps[0].id if user_emps else False
        user_emp_dept_id = user_emps[0].department_id.id if user_emps and user_emps[0].department_id else False
        user_emp_job_id = user_emps[0].job_id.id if user_emps and user_emps[0].job_id else False
        
        for a in announcements:
            # 1. Targeting Check
            is_targeted = False
            if a.is_announcement:
                is_targeted = True
            elif user_emp_id:
                if a.announcement_type == 'employee' and user_emp_id in a.employee_ids.ids:
                    is_targeted = True
                elif a.announcement_type == 'department' and user_emp_dept_id and user_emp_dept_id in a.department_ids.ids:
                    is_targeted = True
                elif a.announcement_type == 'job_position' and user_emp_job_id and user_emp_job_id in a.position_ids.ids:
                    is_targeted = True
            
            # 2. Acknowledgment Check
            if is_targeted:
                if not user_emp_id or user_emp_id not in a.acknowledged_employee_ids.ids:
                    result.append({
                        'id': a.id,
                        'title': str(a.announcement_reason) if a.announcement_reason else 'Announcement',
                        'date': str(a.date_start) if a.date_start else '',
                        'category': str(a.category_id.name) if a.category_id else 'General',
                    })
        
        return result
