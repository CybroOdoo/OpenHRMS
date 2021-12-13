# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
{
    'name': 'Open HRMS Biometric Device Integration',
    'version': '15.0.1.0.0',
    'summary': """Integrating Biometric Device With HR Attendance (Face + Thumb)""",
    'description': 'This module integrates Odoo with the biometric device(Model: ZKteco uFace 202)',
    'category': 'Generic Modules/Human Resources',
     'live_test_url': 'https://youtu.be/RHSHHU7nzTo',
    'author': 'Cybrosys Techno Solutions, Mostafa Shokiel,Open HRMS',
    'live_test_url': 'https://youtu.be/RHSHHU7nzTo',
    'company': 'Cybrosys Techno Solutions',
    'website': "http://www.openhrms.com",
    'depends': ['base_setup', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_machine_view.xml',
        'views/zk_machine_attendance_view.xml',
        'data/download_data.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
