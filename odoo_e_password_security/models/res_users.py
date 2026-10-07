import re
import hashlib
from datetime import datetime, timedelta
from dateutil import tz
from markupsafe import Markup, escape
from markupsafe import Markup
import pytz
from odoo import _, api, fields, models, tools, http
from odoo.exceptions import UserError, ValidationError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging
from os import utime
from os.path import getmtime
from time import time

from odoo import api, http, models
from odoo.http import SessionExpiredException

_logger = logging.getLogger(__name__)




from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)


from odoo import http




from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessDenied, UserError
import logging

_logger = logging.getLogger(__name__)


    


def delta_now(**kwargs):
    return fields.Datetime.now() + timedelta(**kwargs)


class ResUsers(models.Model):
    _inherit = "res.users"

    password_write_date = fields.Datetime("Last password update", default=fields.Datetime.now, readonly=True)
    next_password_write_date = fields.Datetime("Next password update", compute="_compute_next_password_write_date")
    password_history_ids = fields.One2many(
        string="Password History",
        comodel_name="res.users.pass.history",
        inverse_name="user_id",
        readonly=True,
    )


    failed_login_attempts = fields.Integer(
        string="Failed Login Attempts",
        
        help="Number of consecutive failed login attempts"
    )
    last_failed_login = fields.Datetime(
        string="Last Failed Login",
        help="Timestamp of the last failed login attempt"
    )
    account_locked = fields.Boolean(
        string="Account Locked",
        default=False,
        help="Account is locked due to too many failed attempts"
    )
    locked_until = fields.Datetime(
        string="Locked Until",
        help="Account will be unlocked automatically at this time"
    )
    lockout_start_time = fields.Datetime(
        string="Lockout Start Time",
        help="When the current lockout period started"
    )
    is_locked = fields.Boolean()


   
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['password_write_date', 'next_password_write_date','failed_login_attempts']
   
    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS +  ['failed_login_attempts']


 
    def action_unlock_user(self):
        for user in self:
            user.sudo().write({
                    'failed_login_attempts': 0,
                    'account_locked': False
                })
            message = f"{user.name} Account is Unlocked"
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'type': 'rainbow_man',
                }
            }


   
  

    def _get_lockout_config(self):
        """Get lockout configuration from system parameters"""
        ICPSudo = self.env['ir.config_parameter'].sudo()
        max_attempts = int(ICPSudo.get_param('odoo_e_password_security.max_attempts', 5))
        lockout_duration = int(ICPSudo.get_param('odoo_e_password_security.lockout_duration', 30))
        reset_time = int(ICPSudo.get_param('odoo_e_password_security.reset_time', 60))  # Time to reset counter
        return max_attempts, 30, 60



    def _check_credentials(self, password, env):
        """Override to implement account lockout logic"""
        # First check if account is locked
        if self.account_locked:
            if self.locked_until and fields.Datetime.now() < self.locked_until:
                raise AccessDenied(_("Your account has been temporarily locked due to multiple failed login attempts. Please try again later."))
            else:
                # Auto-unlock if lockout period has expired
                self._unlock_user_account()

        try:
            # Call parent method to verify credentials
            result = super(ResUsers, self)._check_credentials(password, env)
            
            # Reset failed attempts on successful login
            if self.failed_login_attempts > 0:
                self.sudo().write({
                    'failed_login_attempts': 0,
                    'last_failed_login': False
                })
                _logger.info(f"Successful login for user {self.login}, reset failed attempts counter")
            
            return result
            
        except AccessDenied as e:
            # Handle failed login attempt
            self._handle_failed_login()
            raise e


    def _handle_failed_login(self):
        """Handle failed login attempt and implement lockout logic"""
        max_attempts, lockout_duration, reset_time = self._get_lockout_config()
        now = fields.Datetime.now()
        
        # Check if we should reset the counter (if last attempt was long ago)
        if (self.last_failed_login and 
            (now - self.last_failed_login).total_seconds() > (reset_time * 60)):
            failed_attempts = 1
        else:
            failed_attempts = self.failed_login_attempts + 1
        
        vals = {
            'failed_login_attempts': failed_attempts,
            'last_failed_login': now
        }
        
        # Lock account if max attempts reached
        if failed_attempts >= max_attempts:
            lockout_until = now + timedelta(minutes=lockout_duration)
            vals.update({
                'account_locked': True,
                'locked_until': lockout_until,
                'lockout_start_time': now
            })
            
            _logger.warning(
                f"Account locked for user '{self.login}' "
                f"after {failed_attempts} failed login attempts. "
                f"Locked until: {lockout_until}"
            )
            
            # Optional: Send notification email
        else:
            remaining_attempts = max_attempts - failed_attempts
            _logger.info(
                f"Failed login attempt for user '{self.login}'. "
                f"Attempts: {failed_attempts}/{max_attempts}. "
                f"Remaining: {remaining_attempts}"
            )
        
        self.sudo().write(vals)
        self.env.cr.commit()


    


    #session timeout
    @api.model
    def _auth_timeout_get_ignored_urls(self):
        """Pluggable method for calculating ignored urls
        Defaults to stored config param
        """
        params = self.env["ir.config_parameter"]
        return params._auth_timeout_get_parameter_ignored_urls()

    @api.model
    def _auth_timeout_deadline_calculate(self):
        """Pluggable method for calculating timeout deadline
        Defaults to current time minus delay using delay stored as config
        param.
        """
        params = self.env["ir.config_parameter"]
        delay = params._auth_timeout_get_parameter_delay()
        if delay <= 0:
            return False
        return time() - delay

    @api.model
    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    @api.model
    def _auth_timeout_check(self):
        """Perform session timeout validation and expire if needed."""

        if not http.request:
            return

        session = http.request.session

        # Calculate deadline
        deadline = self._auth_timeout_deadline_calculate()

        # Check if past deadline
        expired = False
        if deadline is not False:
            path = http.root.session_store.get_session_filename(session.sid)
            try:
                expired = getmtime(path) < deadline
            except OSError:
                _logger.exception(
                    "Exception reading session file modified time.",
                )
                # Force expire the session. Will be resolved with new session.
                expired = True

        # Try to terminate the session
        terminated = False
        if expired:
            terminated = self._auth_timeout_session_terminate(session)

        # If session terminated, all done
        if terminated:
            return SessionExpiredException("Session expired")

        # Else, conditionally update session modified and access times
        ignored_urls = self._auth_timeout_get_ignored_urls()

        if http.request.httprequest.path not in ignored_urls:
            if "path" not in locals():
                path = http.root.session_store.get_session_filename(
                    session.sid,
                )
            try:
                utime(path, None)
            except OSError:
                _logger.exception(
                    "Exception updating session file access/modified times.",
                )

    ###############################################################



    
    
    def write(self, vals):
        if vals.get("password"):
            server_time = datetime.now(pytz.UTC)
            vals["password_write_date"] = fields.Datetime.to_string(server_time)
            for user in self:
                
                old_password_hash = user._get_old_password_hash()  # Odoo already stores hashed password
                new_password_hash = hashlib.sha256(vals["password"].encode()).hexdigest()

                self.env['user.password.log'].create({
                    'user_id': user.id,
                    'changed_by': self.env.user.id,
                    'old_password_hash': old_password_hash,
                    'new_password_hash': new_password_hash,
                    'change_date': vals["password_write_date"]
                })

        return super(ResUsers, self).write(vals)

    def _get_old_password_hash(self):
        password_log = self.env['user.password.log'].search([
            ('user_id', '=', self.id)], limit=1, order='change_date desc')
        
        if password_log:
            return password_log.new_password_hash  # This is the last known password hash
        else:
            return ""    
    
        

    def action_send_password_expire(self, user_ids=[]):
        params = self.env["ir.config_parameter"].sudo()
        password_expiration = int(params.get_param('auth_password_policy.password_expiration'))
        days_before = int(params.get_param('auth_password_policy.day_alert_expire'))

        if password_expiration <= 0:
            return

        if user_ids:
            all_users = self.env['res.users'].sudo().search([('id', 'in', user_ids)])
        else:
            all_users = self.env['res.users'].sudo().search([])

        for rec in all_users:
            if rec.notification_type != 'inbox':
                delta_days = (rec.next_password_write_date - datetime.today()).days
                if delta_days <= days_before: #This condition is checking if the number of days (delta_days) is less than or equal to days_before (which we calculated earlier). If this condition is true, it means the time has come to send a password expiry alert.
                    rec._send_notification_password_expire(delta_days)

    def _send_notification_password_expire(self, delta_days):
        for rec in self:
            rec.action_expire_password()
            body = self.env['mail.render.mixin'].with_context(lang=rec.lang)._render_template(
                self.env.ref('odoo_e_password_security.password_expire'),
                model='res.users', res_ids=rec.ids,
                engine='qweb_view', options={'post_process': True},
                add_context={'day_remain': delta_days},
            )[rec.id]
            subject = self.env['mail.render.mixin'].with_context(lang=rec.lang)._render_template(
                self.env.ref('odoo_e_password_security.password_expire_subject'),
                model='res.users', res_ids=rec.ids,
                engine='qweb_view', options={'post_process': True},
            )[rec.id]

            msg_values = {
                # document
                'model': 'res.users',
                'res_id': rec.id,
                # content
                'body': escape(body),  # escape if text, keep if markup
                'is_internal': True,
                'message_type': 'email_outgoing',
                'subject':subject,
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
                # recipients
                'message_id': tools.generate_tracking_message_id('message-notify'),
                'partner_ids': rec.partner_id.ids,
                # notification
                'email_add_signature': True,
            }

            new_message = self.env['mail.thread']._message_create([msg_values])
            self.env['mail.thread']._fallback_lang()._notify_thread(new_message, msg_values)
            if rec.notification_type == 'email':
                mail = self.env['mail.mail'].search([('message_id', '=', new_message.message_id)])
                if mail:
                    mail.send()

    def _compute_next_password_write_date(self):
        params = self.env["ir.config_parameter"].sudo()
        password_expiration = int(params.get_param('auth_password_policy.password_expiration'))
        
        for rec in self:
            if password_expiration > 0:
                rec.next_password_write_date = (rec.password_write_date + timedelta(days=password_expiration))
            else:
                rec.next_password_write_date = False

    @api.model
    def get_password_policy(self):
        data = super(ResUsers, self).get_password_policy()

        params = self.env['ir.config_parameter'].sudo()
        data.update(
            {
                'password_lower': int(params.get_param('auth_password_policy.password_lower', default=0)),
                'password_upper': int(params.get_param('auth_password_policy.password_upper', default=0)),
                'password_numeric': int(params.get_param('auth_password_policy.password_numeric', default=0)),
                'password_special': int(params.get_param('auth_password_policy.password_special', default=0)),
            }
        )

        return data

    def _check_password_policy(self, passwords):
        result = super(ResUsers, self)._check_password_policy(passwords)

        for password in passwords:
            if not password:
                continue
            self._check_password(password)

        return result

    def password_match_message(self):
        self.ensure_one()
        params = self.env["ir.config_parameter"].sudo()
        password_lower = int(params.get_param('auth_password_policy.password_lower', default=0))
        password_upper = int(params.get_param('auth_password_policy.password_upper', default=0))
        password_numeric = int(params.get_param('auth_password_policy.password_numeric', default=0))
        password_special = int(params.get_param('auth_password_policy.password_special', default=0))
        message = []

        if password_lower > 0:
            message.append(_("\n* Lowercase letter (at least %s characters)") % str(password_lower))
        if password_upper > 0:
            message.append(_("\n* Uppercase letter (at least %s characters)") % str(password_upper))
        if password_numeric > 0:
            message.append(_("\n* Numeric digit (at least %s characters)") % str(password_numeric))
        if password_special > 0:
            message.append(_("\n* Special character (at least %s characters)") % str(password_special))
        if message:
            message = [_("Must contain the following:")] + message

        minlength = int(params.get_param("auth_password_policy.minlength", default=0))
        if minlength > 0:
            message = [_("Password must be %d characters or more.") % minlength] + message

        return "\r".join(message)

    def _check_password(self, password):
        self._check_password_rules(password)
        self._check_password_history(password)
        return True

    def _check_password_rules(self, password):
        self.ensure_one()
        if not password:
            return True

        params = self.env["ir.config_parameter"].sudo()
        password_lower = int(params.get_param("auth_password_policy.password_lower", default=0))
        password_upper = int(params.get_param("auth_password_policy.password_upper", default=0))
        password_numeric = int(params.get_param("auth_password_policy.password_numeric", default=0))
        password_special = int(params.get_param("auth_password_policy.password_special", default=0))
        minlength = int(params.get_param("auth_password_policy.minlength", default=0))

        errors = []
        messages = []

        # Check minimum length
        minlength_status = len(password) >= minlength
        messages.append(_("Password must be at least %d characters long: %s") % (minlength, "✅" if minlength_status else "❌"))
        if not minlength_status:
            errors.append(_("Password must be at least %d characters long.") % minlength)

        # Check lowercase letters
        lowercase_count = len(re.findall(r'[a-z]', password))
        lowercase_status = password_lower <= 0 or lowercase_count >= password_lower
        messages.append(_("Password must contain at least %d lowercase letter(s): %s (Found: %d)") % (password_lower, "✅" if lowercase_status else "❌", lowercase_count))
        if not lowercase_status:
            errors.append(_("Password must contain at least %d lowercase letter(s).") % password_lower)

        # Check uppercase letters
        uppercase_count = len(re.findall(r'[A-Z]', password))
        uppercase_status = password_upper <= 0 or uppercase_count >= password_upper
        messages.append(_("Password must contain at least %d uppercase letter(s): %s (Found: %d)") % (password_upper, "✅" if uppercase_status else "❌", uppercase_count))
        if not uppercase_status:
            errors.append(_("Password must contain at least %d uppercase letter(s).") % password_upper)

        # Check numeric digits
        numeric_count = len(re.findall(r'\d', password))
        numeric_status = password_numeric <= 0 or numeric_count >= password_numeric
        messages.append(_("Password must contain at least %d numeric digit(s): %s (Found: %d)") % (password_numeric, "✅" if numeric_status else "❌", numeric_count))
        if not numeric_status:
            errors.append(_("Password must contain at least %d numeric digit(s).") % password_numeric)

        # Check special characters
        special_count = len(re.findall(r'[\W_]', password))
        special_status = password_special <= 0 or special_count >= password_special
        messages.append(_("Password must contain at least %d special character(s): %s (Found: %d)") % (password_special, "✅" if special_status else "❌", special_count))
        if not special_status:
            errors.append(_("Password must contain at least %d special character(s).") % password_special)

         # If there are any errors, raise them all at once
        if errors:
            is_backend = True  # Default to backend
           
            # Check if request context is available
            if http.request:
                path_info = http.request.httprequest.path
                # Check if the request is for Portal or Signup (Frontend)
                is_frontend = any(route in path_info for route in [
                    "/web/signup",
                    "/web/reset_password",
                    "/my",
                    "/portal"
                ])
                # Check for backend routes
                is_backend = path_info.startswith('/web') and not is_frontend
            if is_backend:
                # Backend: Use plain text formatting (no HTML)
                error_message = _("Password does not meet the following requirements:\n\n")
                error_message += "\n".join(f"- {msg}" for msg in messages)

            else:
                # Frontend (Signup, Portal): Use HTML
                error_message = _("<strong>Password does not meet the following requirements:</strong><ul>")
                error_message += "".join(f"<li>{msg}</li>" for msg in messages)
                error_message += "</ul>"
                error_message = Markup(error_message)  # Ensure HTML is rendered

            raise UserError(error_message)

        return True

    def _check_password_history(self, password):
        """It validates proposed password against existing history
        :raises: UserError on reused password
        """
        if not password:
            return True
        crypt = self._crypt_context()
        params = self.env["ir.config_parameter"].sudo()
        password_history = int(params.get_param("auth_password_policy.password_history", default=0))

        if not password_history:  # disabled
            recent_passes = self.env["res.users.pass.history"]
        elif password_history < 0:  # unlimited
            recent_passes = self.password_history_ids
        else:
            recent_passes = self.password_history_ids[:password_history]

        if recent_passes.filtered(lambda r: crypt.verify(password, r.password_crypt)):
            raise UserError(_("Cannot use the most recent %d passwords") % password_history)

        return True
    def _password_has_expired(self):
        self.ensure_one()
        if not self.password_write_date:
            return True

        params = self.env["ir.config_parameter"].sudo()
        password_expiration = int(params.get_param("auth_password_policy.password_expiration"))
        if password_expiration <= 0:
            return False

        test_password_expiration = params.get_param("auth_password_policy.test_password_expiration")
        if test_password_expiration:
            days = (fields.Datetime.now() - self.password_write_date).total_seconds() // 60
            return days > password_expiration
        else:
            return fields.Datetime.now() >= self.next_password_write_date

    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for user in self:
            user.mapped("partner_id").signup_prepare(
                signup_type="reset", expiration=expiration
            )

    def _set_encrypted_password(self, uid, pw):
        """It saves password crypt history for history rules"""

        res = super(ResUsers, self)._set_encrypted_password(uid, pw)
        self.env["res.users.pass.history"].create({"user_id": uid, "password_crypt": pw})
        return res

    def action_reset_password(self):
        """Disallow password resets inside of Minimum Hours"""
        min_reset_interval_hours = int(self.env['ir.config_parameter'].sudo().get_param('minimum_reset_interval'))
        
        for user in self:
            if user.password_write_date:
                next_allowed_reset = user.password_write_date + timedelta(hours=min_reset_interval_hours)
                print(f"Checking password reset for user {user.id}. Next allowed reset time: {next_allowed_reset}")
                if fields.Datetime.now() < next_allowed_reset:
                    print(f"Password reset attempt too soon for user {user.id}.")
                    raise UserError(
                        _(
                           "You cannot reset your password until %s. "
                           "Please wait for %d hours."
                           
                        ) % (
                            next_allowed_reset.strftime('%d-%m-%Y'),
                            min_reset_interval_hours
                        )
                    )
        
        print("Password reset allowed. Proceeding with the reset process.")
        return super(ResUsers, self).action_reset_password()
