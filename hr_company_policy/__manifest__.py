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
    'name': 'OpenHRMS Company Policy',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage Company Policies',
    'description': 'OpenHRMS Company Policies, hrms, policies',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hrms_dashboard'],
    'data': [
            'security/ir.model.access.csv',
            'views/res_company_views.xml',
            'views/res_company_policy_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/hr_company_policy/static/src/js/company_policy.js',
            '/hr_company_policy/static/src/css/company_policy.css',
            '/hr_company_policy/static/src/xml/dashboard_view.xml'
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
