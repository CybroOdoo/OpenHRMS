# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
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
###############################################################################
from datetime import date, timedelta
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestEmployeeDocument(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.checklist_entry = cls.env['employee.checklist'].create({
            'name': 'Education Certificate',
            'document_type': 'entry',
        })

    def test_employee_checklist_display_name(self):
        """Test computed display name for checklist items."""
        checklist_entry = self.env['employee.checklist'].create({
            'name': 'Visa Entry',
            'document_type': 'entry',
        })
        self.assertEqual(checklist_entry.display_name, 'Visa Entry - en')

        checklist_exit = self.env['employee.checklist'].create({
            'name': 'Clearance Exit',
            'document_type': 'exit',
        })
        self.assertEqual(checklist_exit.display_name, 'Clearance Exit - ex')

        checklist_other = self.env['employee.checklist'].create({
            'name': 'Other Certificate',
            'document_type': 'other',
        })
        self.assertEqual(
            checklist_other.display_name, 'Other Certificate - ot')

    def test_hr_employee_document_count_and_view(self):
        """Test document_expiry_count compute and action_document_view."""
        employee = self.env['hr.employee'].create({'name': 'Alice Smith'})

        # Initially, document count should be 0
        self.assertEqual(employee.document_expiry_count, 0)

        # Create employee documents
        self.env['hr.employee.document'].create({
            'name': 'DOC-ALICE-1',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
        })
        self.env['hr.employee.document'].create({
            'name': 'DOC-ALICE-2',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
        })

        # Recompute and verify count
        employee._compute_document_expiry_count()
        self.assertEqual(employee.document_expiry_count, 2)

        # Test action_document_view
        action = employee.action_document_view()
        self.assertEqual(action['name'], 'Checklist Documents')
        self.assertEqual(action['res_model'], 'hr.employee.document')
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['context']['default_employee_id'], employee.id)
        self.assertIn(('employee_id', '=', employee.id), action['domain'])

    def test_hr_employee_document_onchange_expiry(self):
        """Test document expiry onchange warning."""
        # Test when expiry date is in the future
        doc = self.env['hr.employee.document'].new({
            'name': 'DOC12345',
            'document_id': self.checklist_entry.id,
            'expiry_date': date.today() + timedelta(days=10),
        })
        res = doc._onchange_expiry_date()
        self.assertFalse(
            res, "There should be no warning for future expiry date.")

        # Test when expiry date is in the past
        doc_expired = self.env['hr.employee.document'].new({
            'name': 'DOC12346',
            'document_id': self.checklist_entry.id,
            'expiry_date': date.today() - timedelta(days=5),
        })
        res_expired = doc_expired._onchange_expiry_date()
        self.assertTrue(
            res_expired, "There should be a warning for past expiry date.")
        self.assertIn('warning', res_expired)
        self.assertEqual(res_expired['warning']['title'], 'Document Expired')
        self.assertEqual(
            res_expired['warning']['message'],
            'Your document has already expired.',
        )

    def test_mail_reminder(self):
        """Test mail reminder logic for expiring documents."""
        # Create an employee with a work email
        employee = self.env['hr.employee'].create({
            'name': 'John Doe',
            'work_email': 'john.doe@example.com',
        })

        # Document expiring within the next 8 days (e.g., 5 days from now)
        self.env['hr.employee.document'].create({
            'name': 'DOC-EXPIRING',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
            'expiry_date': date.today() + timedelta(days=5),
        })

        # Document expiring far in the future (e.g., 15 days from now)
        self.env['hr.employee.document'].create({
            'name': 'DOC-SAFE',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
            'expiry_date': date.today() + timedelta(days=15),
        })

        # Document without expiry date
        self.env['hr.employee.document'].create({
            'name': 'DOC-NO-EXPIRY',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
            'expiry_date': False,
        })

        # Run mail reminder
        self.env['hr.employee.document'].mail_reminder()

        # Find the emails sent for employee
        mails = self.env['mail.mail'].search(
            [('email_to', '=', 'john.doe@example.com')])

        # We expect exactly 1 mail to be generated (for DOC-EXPIRING)
        self.assertEqual(
            len(mails), 1, "Only one reminder email should have been sent.")

        # Verify email contents
        self.assertIn("DOC-EXPIRING", mails[0].subject)
        self.assertIn("John Doe", mails[0].body_html)

    def test_ir_attachment_relationship(self):
        """Test relation between hr.employee.document and ir.attachment."""
        employee = self.env['hr.employee'].create({'name': 'Bob Jones'})
        doc = self.env['hr.employee.document'].create({
            'name': 'DOC-BOB',
            'document_id': self.checklist_entry.id,
            'employee_id': employee.id,
        })
        attachment = self.env['ir.attachment'].create({
            'name': 'test_attachment.pdf',
            'datas': b'dGVzdF9kYXRh',  # Base64 data for 'test_data'
        })

        # Link attachment to document
        doc.write({'doc_attachment_ids': [(4, attachment.id)]})

        # Verify bi-directional link
        self.assertIn(attachment, doc.doc_attachment_ids)
        self.assertIn(doc, attachment.doc_attach_ids)

    def test_multi_company_rule(self):
        """Test multi-company isolation on hr.employee.document."""
        company_a = self.env['res.company'].create({'name': 'Company A'})
        company_b = self.env['res.company'].create({'name': 'Company B'})

        user_a = new_test_user(
            self.env,
            login='user_comp_a',
            groups='base.group_user,hr.group_hr_user',
            company_id=company_a.id,
            company_ids=[company_a.id],
        )

        employee_a = self.env['hr.employee'].create({
            'name': 'Employee A',
            'company_id': company_a.id,
        })
        employee_b = self.env['hr.employee'].create({
            'name': 'Employee B',
            'company_id': company_b.id,
        })

        doc_a = self.env['hr.employee.document'].create({
            'name': 'DOC-COMP-A',
            'document_id': self.checklist_entry.id,
            'employee_id': employee_a.id,
        })
        doc_b = self.env['hr.employee.document'].create({
            'name': 'DOC-COMP-B',
            'document_id': self.checklist_entry.id,
            'employee_id': employee_b.id,
        })

        self.assertEqual(doc_a.company_id, company_a)
        self.assertEqual(doc_b.company_id, company_b)

        # Query documents with user_a (belonging to Company A only)
        docs_a = self.env['hr.employee.document'].with_user(user_a).search(
            [('id', 'in', [doc_a.id, doc_b.id])]
        )
        self.assertIn(doc_a, docs_a)
        self.assertNotIn(doc_b, docs_a)

    def test_employee_own_document_rule(self):
        """Test record rule: standard employee only sees own documents."""
        emp_user = new_test_user(
            self.env,
            login='std_emp_user',
            groups='base.group_user',
        )
        emp_other = new_test_user(
            self.env,
            login='std_emp_other',
            groups='base.group_user',
        )
        officer_user = new_test_user(
            self.env,
            login='hr_officer_user',
            groups='base.group_user,hr.group_hr_user',
        )

        emp_record = self.env['hr.employee'].create({
            'name': 'Employee User',
            'user_id': emp_user.id,
        })
        other_record = self.env['hr.employee'].create({
            'name': 'Employee Other',
            'user_id': emp_other.id,
        })
        no_user_record = self.env['hr.employee'].create({
            'name': 'Employee No User',
            'user_id': False,
        })

        doc_own = self.env['hr.employee.document'].create({
            'name': 'DOC-OWN',
            'document_id': self.checklist_entry.id,
            'employee_id': emp_record.id,
        })
        doc_other = self.env['hr.employee.document'].create({
            'name': 'DOC-OTHER',
            'document_id': self.checklist_entry.id,
            'employee_id': other_record.id,
        })
        doc_no_user = self.env['hr.employee.document'].create({
            'name': 'DOC-NO-USER',
            'document_id': self.checklist_entry.id,
            'employee_id': no_user_record.id,
        })

        all_doc_ids = [doc_own.id, doc_other.id, doc_no_user.id]

        # Regular user only sees own document; cannot see unlinked docs
        docs_user = self.env['hr.employee.document'].with_user(
            emp_user).search([('id', 'in', all_doc_ids)])
        self.assertIn(doc_own, docs_user)
        self.assertNotIn(doc_other, docs_user)
        self.assertNotIn(doc_no_user, docs_user)

        # Regular user cannot read or write document of unlinked employee
        with self.assertRaises(AccessError):
            doc_no_user.with_user(emp_user).read(['name'])
        with self.assertRaises(AccessError):
            doc_no_user.with_user(emp_user).write({
                'description': 'Forbidden',
            })

        # Regular user cannot create document for unlinked employee
        with self.assertRaises(AccessError):
            self.env['hr.employee.document'].with_user(emp_user).create({
                'name': 'DOC-FORBIDDEN',
                'document_id': self.checklist_entry.id,
                'employee_id': no_user_record.id,
            })

        # HR Officer sees all documents including unlinked employees
        docs_officer = self.env['hr.employee.document'].with_user(
            officer_user).search([('id', 'in', all_doc_ids)])
        self.assertIn(doc_own, docs_officer)
        self.assertIn(doc_other, docs_officer)
        self.assertIn(doc_no_user, docs_officer)

        # HR Officer can manage documents for unlinked employee
        doc_officer_created = self.env['hr.employee.document'].with_user(
            officer_user).create({
                'name': 'DOC-OFFICER-CREATED',
                'document_id': self.checklist_entry.id,
                'employee_id': no_user_record.id,
            })
        self.assertTrue(doc_officer_created)
        doc_no_user.with_user(officer_user).write({
            'description': 'Updated by officer',
        })
        self.assertEqual(doc_no_user.description, 'Updated by officer')
