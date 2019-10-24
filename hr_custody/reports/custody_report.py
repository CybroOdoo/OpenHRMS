# -*- coding: utf-8 -*-
from odoo import models, fields, tools


class CustodyHistory(models.Model):
    _name = "report.custody"
    _description = "Custody Analysis"
    _auto = False

    name = fields.Char(string='Code')
    date_request = fields.Date(string='Requested Date')
    employee = fields.Many2one('hr.employee', string='Employee')
    purpose = fields.Char(string='Reason')
    custody_name = fields.Many2one('custody.property', string='Property Name')
    return_date = fields.Date(string='Return Date')
    renew_date = fields.Date(string='Renewal Return Date')
    renew_return_date = fields.Boolean(string='Renewal Return Date')
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting For Approval'), ('approved', 'Approved'),
                              ('returned', 'Returned'), ('rejected', 'Refused')], string='Status')

    _order = 'name desc'

    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.name as name,
                    t.date_request as date_request,
                    t.employee as employee,
                    t.purpose as purpose,
                    t.custody_name as custody_name,
                    t.return_date as return_date,
                    t.renew_date as renew_date,
                    t.renew_return_date as renew_return_date,
                    t.state as state
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    name,
                    date_request,
                    employee,
                    purpose,
                    custody_name,
                    return_date,
                    renew_date,
                    renew_return_date,
                    state
        """
        return group_by_str

    def init(self):
        tools.sql.drop_view_if_exists(self._cr, 'report_custody')
        self._cr.execute("""
            CREATE view report_custody as
              %s
              FROM hr_custody t
                %s
        """ % (self._select(), self._group_by()))
