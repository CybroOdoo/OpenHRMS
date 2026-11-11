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
        res = super().survey_start(
            survey_token=survey_token, answer_token=answer_token, email=email,
            **post)
        access_data = self._get_access_data(survey_token, answer_token,
                                            ensure_token=False)
        answer_sudo = access_data.get('answer_sudo')
        if answer_sudo and answer_sudo.appraisal_id:
            stage_name = answer_sudo.appraisal_id.stage_id.name
            if stage_name == "Cancel":
                return request.render("oh_appraisal.appraisal_canceled",
                                      {'survey': access_data.get('survey_sudo')})
            elif stage_name == "Done":
                return request.render("oh_appraisal.appraisal_done",
                                      {'survey': access_data.get('survey_sudo')})
            elif stage_name == "To Start":
                return request.render("oh_appraisal.appraisal_draft",
                                      {'survey': access_data.get('survey_sudo')})
        return res
