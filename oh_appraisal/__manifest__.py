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
{
    'name': "Open HRMS Employee Appraisal",
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Roll out appraisal plans and get the best of your 
    workforce""",
    'description': """This app is a powerful and versatile tool that can help 
    organizations improve their employee appraisal process and boost employee 
    performance.""",
    'live_test_url': 'https://www.youtube.com/watch?v=cw4Bs8-SXdY&feature=youtu.be',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'survey'],
    'data': [
        'security/oh_appraisal_groups.xml',
        'security/hr_appraisal_security.xml',
        'security/ir.model.access.csv',
        'views/appraisal_templates.xml',
        'views/survey_user_input_views.xml',
        'views/hr_appraisal_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [
        'data/hr_employee_demo.xml',
        'data/hr_appraisal_stages_demo.xml',
        'data/hr_appraisal_demo.xml'
    ],
    'images': ["static/description/banner.jpg"],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
}
