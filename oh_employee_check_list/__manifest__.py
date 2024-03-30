# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
{
    "name": "Open HRMS Employee Checklist",
    "version": "16.0.1.0.0",
    "summary": """Manages Employee's Entry & Exit Process""",
    "description": "This module is used to remembering the employee's"
    " entry and exit progress.",
    "live_test_url": "https://youtu.be/KV_Jb_9AGqU",
    "category": "Generic Modules/Human Resources",
    "author": "Cybrosys Techno solutions,Open HRMS",
    "company": "Cybrosys Techno Solutions",
    "website": "https://www.cybrosys.com",
    "depends": ["base", "oh_employee_documents_expiry", "mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/employee_checklist_data.xml",
        "data/hr_plan_activity_type_data.xml",
        "views/hr_employee_views.xml",
        "views/employee_checklist_views.xml",
        "views/hr_employee_document_views.xml",
        "views/mail_activity_views.xml",
    ],
    "images": ["static/description/banner.gif"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
