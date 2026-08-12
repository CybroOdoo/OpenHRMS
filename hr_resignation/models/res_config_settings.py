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
from odoo import fields, models

class ResCompany(models.Model):
    """
    Inherits the res.company model to add configuration fields for the HR Resignation module.
    """
    _inherit = 'res.company'

    enable_manager_approval = fields.Boolean(string="Enable Manager Approval for Resignation", default=True)
    clearance_template_id = fields.Many2one('hr.clearance.template', string="Default Clearance Template")

class ResConfigSettings(models.TransientModel):
    """
    Inherits the res.config.settings model to expose company-level HR Resignation configurations
    in the general settings interface.
    """
    _inherit = 'res.config.settings'

    enable_manager_approval = fields.Boolean(
        related='company_id.enable_manager_approval',
        readonly=False,
        string="Enable Manager Approval"
    )
    clearance_template_id = fields.Many2one(
        related='company_id.clearance_template_id',
        readonly=False,
        string="Default Clearance Template"
    )
