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
from odoo import http
from odoo.addons.survey.controllers import main
from odoo.http import request


class Survey(main.Survey):
    """Inherits the class survey to super the controller"""

    @http.route('/survey/start/<string:survey_token>', type='http',
                auth='public', website=True)
    def survey_start(self, survey_token, answer_token=None, email=False,
                     **post):
        """Inherits the method survey_start to check whether the survey
        appraisal is cancelled, done or has not started"""
        res = super(
            Survey, self).survey_start(
            survey_token=survey_token, answer_token=answer_token, email=email, **post)
        access_data = self._get_access_data(survey_token, answer_token,
                                            ensure_token=False)
        if access_data.get('answer_sudo').appraisal_id:
            if access_data.get('answer_sudo').appraisal_id.stage_id.name == "Cancel":
                return request.render("oh_appraisal.appraisal_canceled",
                                      {'survey': access_data.get('survey_sudo')})
            elif access_data.get('answer_sudo').appraisal_id.stage_id.name == "Done":
                return request.render("oh_appraisal.appraisal_done",
                                      {'survey': access_data.get(
                                          'survey_sudo')})
            elif access_data.get('answer_sudo').appraisal_id.stage_id.name == "To Start":
                return request.render("oh_appraisal.appraisal_draft",
                                      {'survey': access_data.get(
                                          'survey_sudo')})
        return res
