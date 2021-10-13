# -*- coding: utf-8 -*-

{
    'name': 'Odoo15 Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://www.youtube.com/watch?v=Ykni1o8VBlc&feature=youtu.be',
    'summary': """
          Generic Payroll system Integrated with Accounting,Expense Encoding,Payment Encoding,Company Contribution Management
    """,
    'description': """Odoo15 Payroll Accounting,Odoo15 Payroll,Odoo 15,Payroll Accounting,Accounting""",
    'version': '15.0.1.0.0',
    'author': 'Odoo SA,Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['hr_payroll_community', 'account'],
    'images': ['static/description/banner.png'],
    'data': ['views/hr_payroll_account_views.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    'demo': ['data/hr_payroll_account_demo.xml'],
    'license': 'AGPL-3',
}
