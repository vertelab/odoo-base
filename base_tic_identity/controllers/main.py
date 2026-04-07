# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging
import werkzeug.utils
import requests
import secrets

_logger = logging.getLogger(__name__)


class TICCustomerPortal(CustomerPortal):
    _CALLBACK_URL = '/tic/callback'
    _VERIFICATION_URL = '/tic/verify-identity'
    _TIC_API_BASE = 'https://id.tic.io'

    def _get_tic_config(self):
        config_parameter = request.env['ir.config_parameter'].sudo()
        return {
            'api_key': config_parameter.get_param('base_tic_identity.tic_api_key'),
            'tenant': config_parameter.get_param('base_tic_identity.tic_tenant'),
            'base_url': config_parameter.get_param('web.base.url')
        }

    def _validate_state_token(self, state):
        stored_state = request.session.get('tic_state_token')
        partner_id = request.session.get('tic_partner_id')

        if not state or not stored_state or state != stored_state:
            _logger.error("Invalid state token in TIC callback")
            return False, None

        # Clear state token after validation
        request.session.pop('tic_state_token', None)
        request.session.pop('tic_partner_id', None)

        return True, partner_id

    def _collect_tic_session(self, session_id, api_key):
        if not session_id or not api_key:
            return False, None, "Missing session_id or api_key"

        try:
            url = f"{self._TIC_API_BASE}/api/v1/auth/{session_id}/collect"
            response = requests.get(
                url,
                headers={
                    'X-Api-Key': api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10
            )

            if response.status_code != 200:
                error_msg = f"TIC API returned status {response.status_code}: {response.text}"
                _logger.error(error_msg)
                return False, None, error_msg

            session_data = response.json()
            _logger.info("TIC session data received for session: %s", session_id)

            return True, session_data, None

        except requests.exceptions.Timeout:
            error_msg = "TIC API request timed out"
            _logger.error(error_msg)
            return False, None, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling TIC API: {str(e)}"
            _logger.error(error_msg)
            return False, None, error_msg

        except ValueError as e:
            error_msg = f"Invalid JSON response from TIC API: {str(e)}"
            _logger.error(error_msg)
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error in TIC API call: {str(e)}"
            _logger.error(error_msg)
            return False, None, error_msg

    def _validate_session_data(self, session_data):
        if not session_data:
            return False, None, "No session data received"

        status = session_data.get('status')
        if status != 'complete':
            error_msg = f"TIC session not complete. Status: {status}"
            _logger.warning(error_msg)
            return False, None, error_msg

        user_data = session_data.get('user', {})
        if not user_data:
            error_msg = "No user data in TIC response"
            _logger.error(error_msg)
            return False, None, error_msg

        personal_number = user_data.get('personalNumber')
        if not personal_number:
            error_msg = "No personal number in TIC response"
            _logger.error(error_msg)
            return False, None, error_msg

        # Return structured user data
        validated_data = {
            'personal_number': personal_number,
            'given_name': user_data.get('givenName'),
            'surname': user_data.get('surname'),
            'full_name': user_data.get('name'),
        }

        return True, validated_data, None

    def _update_partner_identity(self, partner_id, user_data):
        if not partner_id:
            return False, "No partner_id provided"

        try:
            partner = request.env['res.partner'].sudo().browse(partner_id)

            if not partner.exists():
                error_msg = f"Partner {partner_id} not found"
                _logger.error(error_msg)
                return False, error_msg

            update_vals = {
                'social_sec_nr': user_data['personal_number'],
                'tic_identity_status': 'verified',
                'tic_identity_verified_date': fields.Datetime.now(),
            }

            # Update name if provided and not empty
            if user_data.get('full_name'):
                update_vals['name'] = user_data['full_name']

            partner.write(update_vals)
            _logger.info("Successfully updated partner %s with TIC identity", partner_id)

            return True, None

        except Exception as e:
            error_msg = f"Error updating partner {partner_id}: {str(e)}"
            _logger.error(error_msg)
            return False, error_msg

    @http.route('/my/account', type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post.get('verified') or request.params.get('verified'):
            values['tic_verified'] = True

        if post.get('error') or request.params.get('error'):
            values['tic_error'] = True

        # Handle regular form submission
        if post and request.httprequest.method == 'POST':
            if not partner.can_edit_vat():
                post['country_id'] = str(partner.country_id.id)

            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                vals = {key: post[key] for key in self._get_mandatory_fields()}
                vals.update({key: post[key] for key in self._get_optional_fields() if key in post})
                for field in set(['country_id', 'state_id']) & set(vals.keys()):
                    try:
                        vals[field] = int(vals[field])
                    except:
                        vals[field] = False
                vals.update({'zip': vals.pop('zipcode', '')})
                self.on_account_update(vals, partner)
                # If name is not changed then pop it from the values
                if vals['name'].strip() == partner.name.strip():
                    vals.pop('name')
                partner.sudo().write(vals)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/account')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route(_VERIFICATION_URL, type='http', auth='user', website=True)
    def verify_identity(self, redirect=None, **kw):
        config = self._get_tic_config()

        if not config['api_key'] or not config['tenant']:
            _logger.error("TIC not properly configured")
            return request.redirect('/my/account?error=1')  # Changed from tic_error=config

        state_token = secrets.token_urlsafe(32)

        request.session['tic_state_token'] = state_token
        request.session['tic_partner_id'] = request.env.user.partner_id.id
        if redirect:
            request.session['tic_redirect'] = redirect

        callback_url = f"{config['base_url']}{self._CALLBACK_URL}?state={state_token}"

        tic_url = f"{self._TIC_API_BASE}/{config['tenant']}/login?callback={werkzeug.urls.url_quote(callback_url)}"

        _logger.info("Redirecting partner %s to TIC for identity verification",
                     request.env.user.partner_id.id)
        return werkzeug.utils.redirect(tic_url, 303)

    @http.route(_CALLBACK_URL, type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def tic_callback(self, session_id=None, state=None, **kwargs):
        _logger.info("TIC Callback received - session_id: %s", session_id)

        valid_state, partner_id = self._validate_state_token(state)
        redirect_url = request.session.pop('tic_redirect', '/my/account')

        if not valid_state:
            sep = '&' if '?' in redirect_url else '?'
            return request.redirect(f'{redirect_url}{sep}error=1')

        if not session_id:
            _logger.error("No session_id in TIC callback")
            sep = '&' if '?' in redirect_url else '?'
            return request.redirect(f'{redirect_url}{sep}error=1')

        config = self._get_tic_config()
        if not config['api_key']:
            _logger.error("TIC API key not configured")
            sep = '&' if '?' in redirect_url else '?'
            return request.redirect(f'{redirect_url}{sep}error=1')

        success, session_data, error = self._collect_tic_session(session_id, config['api_key'])
        if not success:
            sep = '&' if '?' in redirect_url else '?'
            return request.redirect(f'{redirect_url}{sep}error=1')

        valid, user_data, error = self._validate_session_data(session_data)
        if not valid:
            sep = '&' if '?' in redirect_url else '?'
            return request.redirect(f'{redirect_url}{sep}error=1')

        if partner_id:
            success, error = self._update_partner_identity(partner_id, user_data)
            if not success:
                sep = '&' if '?' in redirect_url else '?'
                return request.redirect(f'{redirect_url}{sep}error=1')
        else:
            _logger.warning("No partner_id in session, skipping partner update")

        _logger.info("TIC identity verification completed successfully for partner %s", partner_id)
        sep = '&' if '?' in redirect_url else '?'
        return request.redirect(f'{redirect_url}{sep}verified=1')
