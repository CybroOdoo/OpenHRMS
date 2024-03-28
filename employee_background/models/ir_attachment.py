# -*- coding: utf-8 -*-
#############################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
###############################################################################
from collections import defaultdict
from odoo import api, models, _
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    """Inherits the model Ir Attachment and extends to change functionality
    of the method check to download the attached file from the user portal."""
    _inherit = 'ir.attachment'

    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred
        mode """
        if self.env.is_superuser():
            return True
        if not (self.env.is_admin() or self.env.user.has_group(
                'base.group_user') or self.env.user.has_group(
            'base.group_portal')):
            raise AccessError(
                _("Sorry, you are not allowed to access this document."))
        model_ids = defaultdict(set)
        if self:
            self.env['ir.attachment'].flush_recordset(
                ['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute(
                'SELECT res_model, res_id, create_uid, public, res_field FROM ir_attachment WHERE id IN %s',
                [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
                if not self.env.is_system() and res_field:
                    raise AccessError(
                        _("Sorry, you are not allowed to access this document."))
                if public and mode == 'read':
                    continue
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])
        for res_model, res_ids in model_ids.items():
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(
                    res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                continue
            records = self.env[res_model].browse(res_ids).exists()
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)
