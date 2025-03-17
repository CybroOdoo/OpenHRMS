# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class OverTimeTypeRule(models.Model):
    """ Model to define rules associated with HR Overtime Types."""
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type',
                                   string='Over Time Type',
                                   help="Reference to the HR Overtime Type "
                                        "associated with this rule.")
    name = fields.Char('Name', required=True, help="Name of the overtime "
                                                   "rule.")
    from_hrs = fields.Float('From', required=True,
                            help="Start hour threshold for the overtime rule.")
    to_hrs = fields.Float('To', required=True,
                          help="End hour threshold for the overtime rule.")
    hrs_amount = fields.Float('Rate', required=True,
                              help="Rate of pay for the overtime rule.")
