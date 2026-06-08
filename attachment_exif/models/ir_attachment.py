import base64
import logging
from io import BytesIO

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    exif_ids = fields.One2many('ir.attachment.exif', 'attachment_id', string='EXIF Data')
    has_exif = fields.Boolean(string='Has EXIF Data', compute='_compute_has_exif')

    @api.depends('exif_ids')
    def _compute_has_exif(self):
        for record in self:
            record.has_exif = bool(record.exif_ids)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._extract_exif()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'datas' in vals:
            for record in self:
                record._extract_exif()
        return res

    def _extract_exif(self):
        self.ensure_one()
        if not self.datas or not self.mimetype or not self.mimetype.startswith('image/'):
            self.exif_ids.unlink()
            return
        try:
            stream = BytesIO(base64.b64decode(self.datas))
            img = Image.open(stream)
            exif_data = img._getexif()
        except Exception:
            self.exif_ids.unlink()
            _logger.debug("Failed to extract EXIF from attachment %s", self.name)
            return
        if not exif_data:
            self.exif_ids.unlink()
            return
        tag_map = {**TAGS, **GPSTAGS}
        existing = {r.exif_tag_id: r for r in self.exif_ids}
        new_vals = []
        for tag_id, value in exif_data.items():
            tag_name = tag_map.get(tag_id, f'Tag{tag_id}')
            str_value = str(value)
            if tag_id in existing:
                existing[tag_id].write({'exif_value': str_value})
            else:
                new_vals.append({
                    'exif_tag': tag_name,
                    'exif_value': str_value,
                    'exif_tag_id': tag_id,
                })
        to_remove = self.exif_ids.filtered(lambda r: r.exif_tag_id not in exif_data)
        if to_remove:
            to_remove.unlink()
        if new_vals:
            self.env['ir.attachment.exif'].create([
                dict(v, attachment_id=self.id) for v in new_vals
            ])


class IrAttachmentExif(models.Model):
    _name = 'ir.attachment.exif'
    _description = 'Attachment EXIF Data'
    _order = 'exif_tag_id'

    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True, ondelete='cascade')
    exif_tag = fields.Char(string='Tag', readonly=True)
    exif_value = fields.Text(string='Value', readonly=True)
    exif_tag_id = fields.Integer(string='Tag ID', readonly=True)
