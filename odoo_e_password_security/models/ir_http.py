# -*- coding: utf-8 -*-
import requests

import odoo
from odoo import api, http, models
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.service import security
import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import logging

_logger = logging.getLogger(__name__)



#session tiemout
from odoo import api, models, tools

DELAY_KEY = "inactive_session_time_out_delay"
IGNORED_PATH_KEY = "inactive_session_time_out_ignored_url"


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    @tools.ormcache("self.env.cr.dbname")
    def _auth_timeout_get_parameter_delay(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                DELAY_KEY,
                7200,
            )
        )

    @api.model
    @tools.ormcache("self.env.cr.dbname")
    def _auth_timeout_get_parameter_ignored_urls(self):
        urls = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                IGNORED_PATH_KEY,
                "",
            )
        )
        return urls.split(",")

    def write(self, vals):
        res = super().write(vals)
        if DELAY_KEY == self.key or IGNORED_PATH_KEY == self.key:
            self.env.registry.clear_cache()
        return res





class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, endpoint):
        auth = 'none' if http.is_cors_preflight(request, endpoint) else endpoint.routing['auth']

        try:
            #session timeout
            if (request and request.session and request.session.uid and not request.env["res.users"].browse(request.session.uid)._is_public() ):
                request.env.user._auth_timeout_check()

            ##########################

            if request.session.uid is not None:
                user = request.env['res.users'].browse(request.session.uid)
                # if password has expired, logout and prepare for reset password
                if user._password_has_expired() and request.session.uid != 1:
                    user._revoke_all_devices()
                    user.action_expire_password()
                    request.session.logout(keep_db=True)
                    request.env = api.Environment(request.env.cr, None, request.session.context)

                # old authenticate process
                elif not security.check_session(request.session, request.env):
                    request.session.logout(keep_db=True)
                    request.env = api.Environment(request.env.cr, None, request.session.context)
            getattr(cls, f'_auth_method_{auth}')()
        except (AccessDenied, http.SessionExpiredException, werkzeug.exceptions.HTTPException):
            raise
        except Exception:
            _logger.info("Exception during request Authentication.", exc_info=True)
            raise AccessDenied()
