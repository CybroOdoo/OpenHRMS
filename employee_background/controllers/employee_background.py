# -*- coding: utf-8 -*-
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
import base64
from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager
from odoo.exceptions import AccessError, UserError
from odoo.http import request


class UserPortal(CustomerPortal):
    """Creates the class Customer Portal to manage the controllers related to
    this module"""

    def _prepare_home_portal_values(self, counters):
        """Inherit the method _prepare_home_portal_values to add the
        verification_count into the values"""
        values = super()._prepare_home_portal_values(counters)
        if 'verification_count' in counters:
            partner = request.env.user.partner_id
            employee_records = request.env[
                'employee.verification'].sudo().search(
                ['&', ('state', '=', 'assign'), ('agency_id', '=', partner.id)])
            verification_count = len(employee_records)
            values['verification_count'] = verification_count
        return values

    @http.route(['/my/records', '/my/quotes/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_records(self, page=1, date_begin=None, date_end=None,
                          sortby=None):
        """Method portal_my_records to return the employee verification records
        assigned for the current agency"""
        partner = request.env.user.partner_id
        employee_records = request.env['employee.verification'].sudo().search(
            ['&', ('state', '=', 'assign'), ('agency_id', '=', partner.id)])
        verification_count = request.env[
            'employee.verification'].sudo().search_count(
            ['&', ('state', '=', 'assign'), ('agency_id', '=', partner.id)])
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=verification_count,
            page=page,
            step=self._items_per_page)
        values = {
            'date': date_begin,
            'records': employee_records.sudo(),
            'page_name': 'employee',
            'pager': pager,
            'default_url': '/my/quotes',
            'sortby': sortby,
        }
        return request.render("employee_background.portal_my_records", values)

    @http.route(['/my/details/<int:order>'], type='http', auth="public",
                website=True)
    def portal_record_page(self, order=None):
        """Method portal_record_page to return the current employee
        verification record"""
        try:
            data = request.env['employee.verification'].sudo().browse(order)
        except AccessError:
            return request.redirect('/my')
        values = {
            'page_name': 'employee_details',
            'records': data
        }
        return request.render("employee_background.portal_record_page", values)

    @http.route('/test/path', type='http', auth="public", website=True,
                csrf=False)
    def portal_order_report(self, **kw):
        """Method portal_order_report is the functionality to process when the
        agency has completed the verification of the employee"""
        employee = request.env['employee.verification'].sudo().browse(
            kw['employee_token'])
        if kw['description'] or kw.get('attachment', False):
            if kw['description']:
                employee.description_by_agency = kw['description']
            if kw.get('attachment', False):
                attachments = request.env['ir.attachment']
                name = kw.get('attachment').filename
                file = kw.get('attachment')
                attachment = file.read()
                attachment_id = attachments.sudo().create({
                    'name': name,
                    'type': 'binary',
                    'datas': base64.b64encode(attachment),
                })
                employee.agency_attachment_ids = [
                    fields.Command.link(attachment_id.id)]
            employee.state = 'submit'
            values = {
                'page_name': 'employee_submit'
            }
            return request.render("employee_background.portal_record_completed",
                                  values)
        raise UserError(
            _("You need to Enter description or attach "
              "a file before submit."))
