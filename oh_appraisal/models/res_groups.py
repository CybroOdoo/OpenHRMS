# -*- coding: utf-8 -*-
#############################################################################
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
#############################################################################
from odoo import models


class ResGroups(models.Model):
    """Inherit res.groups to manage appraisal user group settings."""
    _inherit = 'res.groups'

    def _get_light_group_xmlids(self):
        """Extend the list of light group XML IDs to include the appraisal employee group."""
        return (
            *super()._get_light_group_xmlids(),
            'oh_appraisal.oh_appraisal_group_employee',
        )
