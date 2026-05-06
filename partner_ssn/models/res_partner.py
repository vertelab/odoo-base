from odoo import models, fields, api, _
from datetime import date
import logging
from odoo.exceptions import ValidationError
import re

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    social_sec_nr = fields.Char(string="Social Security Number", tracking=True)
    social_sec_nr_age = fields.Integer(
        string="Social Security Number Age",
        compute="_compute_social_sec_nr_age",
        store=True,
        tracking=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "social_sec_nr_unique",
            "UNIQUE(social_sec_nr)",
            "Social security number must be unique.",
        )
    ]

    @api.constrains("social_sec_nr")
    def _check_social_sec_nr(self):
        for rec in self:
            if rec.social_sec_nr:
                _, error = self._normalize_social_sec_nr(rec.social_sec_nr)
                if error:
                    raise ValidationError(error)

    @api.onchange("social_sec_nr")
    def _onchange_social_sec_nr(self):
        if self.social_sec_nr:
            normalized, error = self._normalize_social_sec_nr(self.social_sec_nr)
            if not error:
                self.social_sec_nr = normalized
            else:
                self.social_sec_nr = ""

    @api.depends("social_sec_nr")
    def _compute_social_sec_nr_age(self):
        for rec in self:
            if rec.social_sec_nr:
                normalized, error = self._normalize_social_sec_nr(rec.social_sec_nr)
                rec.social_sec_nr_age = (
                    self._compute_age_from_normalized(normalized) if not error else 0
                )
            else:
                rec.social_sec_nr_age = 0

    def _normalize_social_sec_nr(self, social_sec):
        if re.fullmatch(r"\d{8}-\d{4}", social_sec):
            normalized = social_sec
        elif re.fullmatch(r"\d{12}", social_sec):
            normalized = "%s-%s" % (social_sec[:8], social_sec[8:])
        elif re.fullmatch(r"\d{6}-\d{4}", social_sec) or re.fullmatch(r"\d{10}", social_sec):
            error = _("Format YYMMDD-NNNN is not accepted. Use YYYYMMDD-NNNN.")
            _logger.error(error)
            return "", error
        else:
            error = _("Social security number %s is not correctly formatted.") % social_sec
            _logger.error(error)
            return "", error

        date_part = normalized.split("-")[0]
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        actual_day = day - 60 if day > 60 else day
        try:
            date(year, month, actual_day)
        except ValueError:
            error = _("Social security number %s contains an invalid date.") % social_sec
            _logger.error(error)
            return "", error

        return normalized, ""

    def _compute_age_from_normalized(self, normalized):
        today = date.today()
        date_part = normalized.split("-")[0]
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        if day > 60:
            day -= 60
        try:
            dob = date(year, month, day)
        except ValueError:
            return 0
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
        if years > 67:
            _logger.warning("Person is %s years old, above 67 threshold.", years)
        return years
