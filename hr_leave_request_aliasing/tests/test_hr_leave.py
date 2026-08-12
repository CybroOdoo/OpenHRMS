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
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrLeaveAliasing(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.env['ir.config_parameter'].sudo().set_param('hr_holidays.alias_prefix', 'Leave')
        cls.env['ir.config_parameter'].sudo().set_param('hr_holidays.alias_domain', 'testdomain.com')
        
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee Aliasing',
            'work_email': 'employee@testdomain.com',
        })
        
        cls.leave_type = cls.env['hr.leave.type'].create({
            'name': 'Test Unpaid Leave',
            'requires_allocation': False,
            'company_id': False,
        })

    def test_message_new_valid_leave_two_dates(self):
        """Test incoming email with valid prefix, domain, and two dates creates a leave."""
        msg_dict = {
            'subject': 'Leave request for summer',
            'email_from': 'employee@testdomain.com',
            'body': 'I would like to take leave from 15/07/2026 to 17/07/2026 for personal reasons.',
        }
        
        leave = self.env['hr.leave'].message_new(msg_dict)
        
        self.assertEqual(leave.employee_id.id, self.employee.id)
        self.assertEqual(leave.holiday_status_id.requires_allocation, False)
        
        self.assertEqual(leave.request_date_from.strftime('%d/%m/%Y'), '15/07/2026')
        self.assertEqual(leave.request_date_to.strftime('%d/%m/%Y'), '17/07/2026')
        self.assertEqual(leave.name, 'Leave request for summer')

    def test_message_new_valid_leave_one_date(self):
        """Test incoming email with valid prefix, domain, and one date creates a single day leave."""
        msg_dict = {
            'subject': 'Leave request for tomorrow',
            'email_from': 'employee@testdomain.com',
            'body': 'I am taking a single day off on 20/08/2026.',
        }
        
        leave = self.env['hr.leave'].message_new(msg_dict)
        
        self.assertEqual(leave.request_date_from.strftime('%d/%m/%Y'), '20/08/2026')
        self.assertEqual(leave.request_date_to.strftime('%d/%m/%Y'), '20/08/2026')

    def test_message_new_invalid_prefix(self):
        """Test incoming email with invalid subject prefix skips custom logic."""
        msg_dict = {
            'subject': 'Vacation request', # Does not contain 'Leave'
            'email_from': 'employee@testdomain.com',
            'body': 'I want leave from 15/07/2026 to 17/07/2026.',
        }
        
        with self.assertRaises(Exception):
            self.env['hr.leave'].message_new(msg_dict)

    def test_message_new_invalid_domain(self):
        """Test incoming email with invalid domain skips custom logic."""
        msg_dict = {
            'subject': 'Leave request',
            'email_from': 'employee@wrongdomain.com', # Does not contain 'testdomain.com'
            'body': 'I want leave from 15/07/2026 to 17/07/2026.',
        }
        
        with self.assertRaises(Exception):
            self.env['hr.leave'].message_new(msg_dict)

    def test_message_new_no_dates(self):
        """Test incoming email with no dates skips setting custom date fields."""
        msg_dict = {
            'subject': 'Leave request',
            'email_from': 'employee@testdomain.com',
            'body': 'I want leave, but I will decide the dates later.',
        }
        
        with self.assertRaises(Exception):
            self.env['hr.leave'].message_new(msg_dict)
