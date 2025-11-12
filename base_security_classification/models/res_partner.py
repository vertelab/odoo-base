import json
import uuid
import logging
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    # Field mapping as class constant
    CM_FIELD_MAPPING = {
        'cm_name': ['name'],
        'cm_address': ['street', 'street2', 'city', 'zip', 'country_id', 'state_id'],
        'cm_mobile': ['mobile'],
        'cm_phone': ['phone'],
        'cm_email': ['email'],
        'cm_ssnr': ['vat', 'ref'],
    }

    confidentiality_marking = fields.Boolean(
        string="Confidentiality Marking",
        default=False,
    )
    cm_name = fields.Boolean(string="Hide Name")
    cm_address = fields.Boolean(string="Hide Address")
    cm_mobile = fields.Boolean(string="Hide Mobile")
    cm_phone = fields.Boolean(string="Hide Phone")
    cm_email = fields.Boolean(string="Hide Email")
    cm_ssnr = fields.Boolean(string="Hide SSN/Registration")
    cm_vault = fields.Text(string="Confidential Vault", readonly=True, copy=False)
    cm_uuid = fields.Char(string="Confidentiality UUID", readonly=True, copy=False, index=True)

    def _is_confidentiality_manager(self):
        """Check if current user is a confidentiality manager"""
        return self.env.user.has_group('base_security_classification.group_confidentiality_marking_manager')

    def _get_fields_to_hide(self):
        """Get list of fields to hide based on CM flags"""
        self.ensure_one()
        return list({
            field
            for cm_flag, field_names in self.CM_FIELD_MAPPING.items()
            if self[cm_flag]
            for field in field_names
        })

    def _get_fields_to_hide_from_vals(self, vals):
        """Get list of fields to hide based on CM flags in vals dict"""
        fields_to_hide = []
        for cm_flag, field_names in self.CM_FIELD_MAPPING.items():
            if vals.get(cm_flag):
                fields_to_hide.extend(field_names)
        return list(set(fields_to_hide))

    def _prepare_vault_data(self):
        """Prepare data dictionary for encryption"""
        self.ensure_one()
        vault_data = {}
        for field_name in self._get_fields_to_hide():
            if field_name in self._fields:
                field_value = self[field_name]
                vault_data[field_name] = field_value.id if isinstance(field_value, models.BaseModel) else field_value
        return vault_data

    def _prepare_vault_data_from_vals(self, vals):
        """Prepare data dictionary for encryption from vals dict"""
        vault_data = {}
        fields_to_hide = self._get_fields_to_hide_from_vals(vals)

        for field_name in fields_to_hide:
            if field_name in vals:
                vault_data[field_name] = vals[field_name]

        return vault_data

    def _get_vault_name(self):
        """Get the vault name for encrypted.data storage"""
        self.ensure_one()
        return f"res.partner,{self.id}"

    def _write_without_tracking(self, vals):
        """Write without tracking in chatter - for confidential updates"""
        return super(Partner, self.with_context(
            tracking_disable=True,
            mail_notrack=True,
            mail_create_nosubscribe=True,
            mail_create_nolog=True,
            mail_auto_subscribe_no_notify=True
        )).write(vals)

    def _encrypt_to_vault(self):
        """Encrypt sensitive data and store in vault"""
        self.ensure_one()
        if not self.confidentiality_marking:
            return

        new_uuid = self.cm_uuid or str(uuid.uuid4())
        vault_data = self._prepare_vault_data()

        if not vault_data:
            return

        # Store encrypted data
        vault_name = self._get_vault_name()
        self.env['encrypted.data'].sudo()._encrypted_store_json(vault_name, vault_data)

        # Prepare masked values
        masked_vals = {
            'cm_vault': json.dumps({
                'encrypted': True,
                'uuid': new_uuid,
                'fields': list(vault_data.keys())
            }),
            'cm_uuid': new_uuid
        }

        # Mask sensitive fields
        for field_name in vault_data.keys():
            if field_name in self._fields:
                field = self._fields[field_name]
                masked_vals[field_name] = (
                    False if field.type == 'many2one'
                    else new_uuid if field.type in ('char', 'text')
                    else False
                )

        # Write without tracking to prevent chatter logs
        self._write_without_tracking(masked_vals)

    def _restore_from_vault(self):
        """Restore data from vault back to database fields"""
        self.ensure_one()
        if not self.cm_uuid:
            return

        decrypted_data = self._decrypt_from_vault()
        if not decrypted_data:
            _logger.warning(f"No data found in vault for partner {self.id}")
            return

        # Prepare restoration values
        restore_vals = {k: v for k, v in decrypted_data.items() if k in self._fields}
        restore_vals.update({'cm_vault': False, 'cm_uuid': False})

        # Write without tracking
        if restore_vals:
            self._write_without_tracking(restore_vals)

        # Cleanup encrypted data
        self._cleanup_vault()

    def _decrypt_from_vault(self):
        """Decrypt sensitive data from vault"""
        self.ensure_one()
        if not self.cm_uuid:
            return {}

        vault_name = self._get_vault_name()
        return self.env['encrypted.data'].sudo()._encrypted_read_json(vault_name) or {}

    def _cleanup_vault(self):
        """Remove encrypted data from vault"""
        self.ensure_one()
        vault_name = self._get_vault_name()
        existing_data = self.env['encrypted.data'].sudo().search([('name', '=', vault_name)])
        if existing_data:
            existing_data.unlink()
            self.env.registry.clear_cache()

    def _check_confidential_access(self, vals):
        """Check if non-manager is trying to modify confidential fields"""
        if self._is_confidentiality_manager():
            return

        for record in self.filtered('confidentiality_marking'):
            restricted_fields = set(vals.keys()) & set(record._get_fields_to_hide())
            if restricted_fields:
                raise AccessError(
                    _("You don't have permission to modify these confidential fields: %s")
                    % ', '.join(restricted_fields)
                )

    def _handle_cm_activation(self, record, vals):
        """Handle confidentiality marking activation"""
        # Use write without tracking for CM activation
        record._write_without_tracking(vals)
        record._encrypt_to_vault()
        record.invalidate_recordset()
        return True

    def _handle_cm_deactivation(self, record, vals):
        """Handle confidentiality marking deactivation"""
        record._restore_from_vault()
        # Use write without tracking for CM deactivation
        result = record._write_without_tracking(vals)
        record.invalidate_recordset()
        return result

    def _handle_cm_update(self, record, vals):
        """Handle updates to already confidential records"""
        cm_flags = list(self.CM_FIELD_MAPPING.keys())
        fields_to_hide = record._get_fields_to_hide()

        # Check if any CM flags or sensitive fields changed
        if any(flag in vals for flag in cm_flags) or any(f in vals for f in fields_to_hide):
            result = record._write_without_tracking(vals)
            record.invalidate_recordset()
            record._encrypt_to_vault()
            return result

        return None

    def _read(self, field_names):
        """Override _read to apply confidentiality masking/unmasking"""
        super(Partner, self)._read(field_names)

        is_manager = self._is_confidentiality_manager()
        cache = self.env.cache

        for record in self:
            if not record.confidentiality_marking:
                continue

            fields_to_hide = record._get_fields_to_hide()
            if not fields_to_hide or not record.cm_uuid:
                continue

            if is_manager:
                self._apply_decryption(record, fields_to_hide, cache)
            else:
                self._apply_masking(record, fields_to_hide, cache)

    def _apply_decryption(self, record, fields_to_hide, cache):
        """Apply decryption for managers"""
        decrypted_data = record._decrypt_from_vault()

        for field_name in fields_to_hide:
            if field_name in decrypted_data and field_name in self._fields:
                field = self._fields[field_name]
                value = decrypted_data[field_name]
                cache.set(record, field, value if field.type != 'many2one' or value else False)

    def _apply_masking(self, record, fields_to_hide, cache):
        """Apply masking for non-managers"""
        uuid_value = record.cm_uuid

        for field_name in fields_to_hide:
            if field_name in self._fields:
                field = self._fields[field_name]
                masked_value = (
                    False if field.type == 'many2one'
                    else uuid_value if field.type in ('char', 'text')
                    else 0 if field.type in ('integer', 'float', 'monetary')
                    else False
                )
                cache.set(record, field, masked_value)

    def write(self, vals):
        """Override write to handle confidentiality marking"""
        # Check access for non-managers
        self._check_confidential_access(vals)

        # Check if CM is being changed
        cm_changing = 'confidentiality_marking' in vals
        is_manager = self._is_confidentiality_manager()

        for record in self:
            if not is_manager:
                continue

            # Handle CM deactivation
            if cm_changing and not vals['confidentiality_marking'] and record.confidentiality_marking:
                return self._handle_cm_deactivation(record, vals)

            # Handle CM activation
            if cm_changing and vals['confidentiality_marking']:
                return self._handle_cm_activation(record, vals)

            # Handle updates to confidential records
            if record.confidentiality_marking:
                result = self._handle_cm_update(record, vals)
                if result is not None:
                    return result

        # Normal write for non-confidential changes
        return super(Partner, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle confidentiality marking"""
        is_manager = self._is_confidentiality_manager()

        # Don't handle CM during create - let it be handled on first write/save
        # This prevents UUID generation issues
        if is_manager:
            # Remove CM from vals during create to prevent auto-encryption
            processed_vals_list = []
            cm_states = []  # Store original CM states

            for vals in vals_list:
                cm_active = vals.get('confidentiality_marking', False)
                cm_states.append(cm_active)

                # If CM is active, temporarily disable it during create
                if cm_active:
                    vals_copy = vals.copy()
                    vals_copy['confidentiality_marking'] = False
                    processed_vals_list.append(vals_copy)
                else:
                    processed_vals_list.append(vals)

            # Create records without CM active
            records = super(Partner, self).create(processed_vals_list)

            # Now activate CM for records that need it
            for record, cm_active in zip(records, cm_states):
                if cm_active:
                    # Activate CM which will trigger encryption
                    record._write_without_tracking({'confidentiality_marking': True})
                    record._encrypt_to_vault()
                    record.invalidate_recordset()
        else:
            records = super(Partner, self).create(vals_list)

        return records

    def unlink(self):
        """Override unlink to clean up encrypted data"""
        is_manager = self._is_confidentiality_manager()

        for record in self.filtered('confidentiality_marking'):
            if not is_manager:
                raise AccessError(
                    _("You don't have permission to delete partners with confidentiality marking.")
                )

            if record.cm_uuid:
                record._cleanup_vault()

        return super(Partner, self).unlink()