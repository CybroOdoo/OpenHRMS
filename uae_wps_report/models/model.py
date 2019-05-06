# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(string="Employee Card Number", size=14, required=True)
    salary_card_number = fields.Char(string="Salary Card Number/Account Number", size=16, required=True)
    agent_id = fields.Many2one('res.bank', string="Agent/Bank", required=True)

    @api.multi
    def write(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if len(vals['salary_card_number']) < 16:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).write(vals)

    @api.model
    def create(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if len(vals['salary_card_number']) < 16:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).create(vals)


class Bank(models.Model):
    _inherit = 'res.bank'

    routing_code = fields.Char(string="Routing Code", size=9, required=True)

    @api.multi
    def write(self, vals):
        if 'routing_code' in vals.keys():
            vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).write(vals)

    @api.model
    def create(self, vals):
        vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).create(vals)


class Company(models.Model):
    _inherit = 'res.company'

    employer_id = fields.Char(string="Employer ID")

    def write(self, vals):
        if 'company_registry' in vals.keys():
            vals['company_registry'] = vals['company_registry'].zfill(13)
        if 'employer_id' in vals.keys():
            vals['employer_id'] = vals['employer_id'].zfill(13)
        return super(Company, self).write(vals)

    def create(self, vals):
        vals['company_registry'] = vals['company_registry'].zfill(13)
        if 'employer_id' in vals.keys():
            vals['employer_id'] = vals['employer_id'].zfill(13)
        return super(Company, self).create(vals)
