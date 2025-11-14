import json
import uuid
import logging
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

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

    confidentiality_marking = fields.Boolean(string="Confidentiality Marking", default=False)
    cm_name = fields.Boolean(string="Hide Name")
    cm_address = fields.Boolean(string="Hide Address")
    cm_mobile = fields.Boolean(string="Hide Mobile")
    cm_phone = fields.Boolean(string="Hide Phone")
    cm_email = fields.Boolean(string="Hide Email")
    cm_ssnr = fields.Boolean(string="Hide SSN/Registration")
    cm_uuid = fields.Char(
        string="Confidentiality UUID",
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: str(uuid.uuid4())
    )

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

    def _get_vault_name(self):
        """Get the vault name for encrypted.data storage"""
        self.ensure_one()
        return f"res.partner,{self.id}"

    def _get_vault_data(self):
        """Get current vault data"""
        self.ensure_one()
        vault_name = self._get_vault_name()
        return self.env['encrypted.data'].sudo()._encrypted_read_json(vault_name) or {}

    def _save_vault_data(self, vault_data):
        """Save vault data"""
        self.ensure_one()
        vault_name = self._get_vault_name()
        self.env['encrypted.data'].sudo()._encrypted_store_json(vault_name, vault_data)

    def _cleanup_vault(self):
        """Remove encrypted data from vault"""
        self.ensure_one()
        vault_name = self._get_vault_name()
        vault = self.env['encrypted.data'].sudo().search([('name', '=', vault_name)])
        if vault:
            vault.unlink()
            self.env.registry.clear_cache()

    def _mask_field(self, field_name):
        """Get masked value for a field"""
        self.ensure_one()
        if field_name not in self._fields:
            return None

        field = self._fields[field_name]
        if field.type == 'many2one':
            return False
        elif field.type in ('char', 'text'):
            return self.cm_uuid
        else:
            return 0 if field.type in ('integer', 'float', 'monetary') else False

    def _sync_vault(self):
        """Sync fields with vault based on CM flags"""
        self.ensure_one()

        if not self.confidentiality_marking or not self.cm_uuid:
            return

        fields_to_hide = self._get_fields_to_hide()
        vault_data = self._get_vault_data()

        # Get all possible confidential fields
        all_conf_fields = {f for fields in self.CM_FIELD_MAPPING.values() for f in fields}

        restore_vals = {}
        mask_vals = {}

        for field_name in all_conf_fields:
            if field_name not in self._fields:
                continue

            should_hide = field_name in fields_to_hide
            in_vault = field_name in vault_data
            current_value = self[field_name]
            is_masked = isinstance(current_value, str) and current_value == self.cm_uuid

            if should_hide:
                # Need to hide this field
                if not is_masked:
                    # Not masked yet - store to vault and mask
                    if not in_vault:
                        # Store real value (not UUID)
                        field_value = current_value
                        # Don't store if it's already the UUID
                        if isinstance(field_value, models.BaseModel):
                            vault_data[field_name] = field_value.id if field_value else False
                        elif field_value != self.cm_uuid:
                            vault_data[field_name] = field_value
                    mask_vals[field_name] = self._mask_field(field_name)
            else:
                # Should NOT be hidden
                if in_vault:
                    # Restore from vault
                    restore_vals[field_name] = vault_data.pop(field_name)

        # Save vault if changed
        self._save_vault_data(vault_data)

        # Apply field changes
        if restore_vals or mask_vals:
            super(Partner, self).write({**restore_vals, **mask_vals})
            self.invalidate_recordset()

    def _restore_all_from_vault(self):
        """Restore all fields from vault and cleanup"""
        self.ensure_one()
        vault_data = self._get_vault_data()

        if vault_data:
            restore_vals = {k: v for k, v in vault_data.items() if k in self._fields}

            super(Partner, self).write(restore_vals)

            self._cleanup_vault()
            self.invalidate_recordset()

    def _read(self, field_names):
        """Override _read to apply masking/unmasking"""
        super(Partner, self)._read(field_names)

        is_manager = self._is_confidentiality_manager()
        cache = self.env.cache

        for record in self:
            if not record.confidentiality_marking or not record.cm_uuid:
                continue

            fields_to_hide = record._get_fields_to_hide()
            if not fields_to_hide:
                continue

            if is_manager:
                # Show real values from vault
                vault_data = record._get_vault_data()
                for field_name in fields_to_hide:
                    if field_name in vault_data and field_name in self._fields:
                        field = self._fields[field_name]
                        value = vault_data[field_name]
                        cache.set(record, field, value if field.type != 'many2one' or value else False)
            else:
                # Show masked values
                for field_name in fields_to_hide:
                    if field_name in self._fields:
                        cache.set(record, self._fields[field_name], record._mask_field(field_name))

    def write(self, vals):
        """Override write to handle confidentiality"""
        is_manager = self._is_confidentiality_manager()

        # Access check for non-managers
        if not is_manager:
            for record in self.filtered('confidentiality_marking'):
                restricted = set(vals.keys()) & set(record._get_fields_to_hide())
                if restricted:
                    raise AccessError(_("You cannot modify confidential fields: %s") % ', '.join(restricted))
            return super(Partner, self).write(vals)

        cm_flags = list(self.CM_FIELD_MAPPING.keys())
        cm_changed = 'confidentiality_marking' in vals
        flags_changed = any(f in vals for f in cm_flags)

        for record in self:
            # Deactivating CM
            if cm_changed and not vals['confidentiality_marking'] and record.confidentiality_marking:
                record._restore_all_from_vault()
                result = super(Partner, record).write(vals)
                # Reactivate messages when removing confidentiality
                record._activate_tracking()
                return result

            # Activating CM
            if cm_changed and vals['confidentiality_marking'] and not record.confidentiality_marking:
                if not record.cm_uuid:
                    super(Partner, record).write({'cm_uuid': str(uuid.uuid4())})
                result = super(Partner, record).write(vals)
                record._sync_vault()
                record._deactivate_tracking()
                return result

            # Changing CM flags
            if record.confidentiality_marking and flags_changed:
                result = super(Partner, record).write(vals)
                record._sync_vault()
                record._deactivate_tracking()
                return result

            # Updating hidden fields
            if record.confidentiality_marking:
                fields_to_hide = record._get_fields_to_hide()
                updating_hidden = any(f in vals for f in fields_to_hide)

                if updating_hidden:
                    # Update vault
                    vault_data = record._get_vault_data()
                    for field_name in fields_to_hide:
                        if field_name in vals:
                            vault_data[field_name] = vals[field_name]
                    record._save_vault_data(vault_data)

                    # Mask in write
                    masked_vals = vals.copy()
                    for field_name in fields_to_hide:
                        if field_name in masked_vals:
                            masked_vals[field_name] = record._mask_field(field_name)

                    result = super(Partner, record).write(masked_vals)
                    record._deactivate_tracking()
                    return result
                else:
                    # Normal write with tracking
                    return super(Partner, record).write(vals)

        return super(Partner, self).write(vals)

    def _deactivate_tracking(self):
        """Deactivate all tracking messages for this partner"""
        self.ensure_one()

        # Flush to ensure message is created, then invalidate cache to get fresh data
        self.env.cr.flush()
        self.invalidate_recordset(['message_ids'])

        # Find all notification messages (tracking messages) for this partner
        tracking_messages = self.env['mail.message'].search([
            ('model', '=', 'res.partner'),
            ('res_id', '=', self.id),
            ('message_type', '=', 'notification'),
            ('active', '=', True),
        ])

        if tracking_messages:
            tracking_messages.write({'active': False})
            _logger.info(
                f"Deactivated {len(tracking_messages)} tracking messages for partner {self.id}"
            )

    def _activate_tracking(self):
        """Reactivate all messages when confidentiality is removed"""
        self.ensure_one()

        # Find all inactive messages for this partner
        inactive_messages = self.env['mail.message'].search([
            ('model', '=', 'res.partner'),
            ('res_id', '=', self.id),
            ('active', '=', False),
        ])

        if inactive_messages:
            inactive_messages.write({'active': True})
            _logger.info(
                f"Reactivated {len(inactive_messages)} messages for partner {self.id}"
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle CM"""
        is_manager = self._is_confidentiality_manager()

        if not is_manager:
            return super(Partner, self).create(vals_list)

        # Ensure UUID for CM records
        processed = []
        for vals in vals_list:
            vals_copy = vals.copy()
            if vals_copy.get('confidentiality_marking') and not vals_copy.get('cm_uuid'):
                vals_copy['cm_uuid'] = str(uuid.uuid4())
            processed.append(vals_copy)

        records = super(Partner, self).create(processed)

        # Sync vault for CM records
        for record in records.filtered('confidentiality_marking'):
            record._sync_vault()

        return records

    def unlink(self):
        """Override unlink to cleanup vault"""
        is_manager = self._is_confidentiality_manager()

        for record in self.filtered('confidentiality_marking'):
            if not is_manager:
                raise AccessError(_("You cannot delete partners with confidentiality marking."))
            if record.cm_uuid:
                record._cleanup_vault()

        return super(Partner, self).unlink()