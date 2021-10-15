from odoo import models, fields, api, _
from datetime import date
import logging
from odoo.exceptions import ValidationError
import re


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    age = fields.Char(string="Age", compute="calculate_age")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", compute="calculate_gender")
    social_sec_nr = fields.Char(string="Social security number")
    social_sec_nr_age = fields.Char(string="Social security number", compute="combine_social_sec_nr_age")

    @api.depends('social_sec_nr')
    def combine_social_sec_nr_age(self):
        for rec in self:
            if rec.social_sec_nr != False:
                rec.social_sec_nr_age = _("%s (%s years old)") % (
                    rec.social_sec_nr,
                    rec.age,
                )
            else:
                rec.social_sec_nr_age = ""

    _sql_constraints = [
        ('social_sec_nr_unique',
        'UNIQUE(social_sec_nr)',
        'social security number field needs to be unique'
        )]

    def calculate_gender(self):
        for partner in self:
            if partner.social_sec_nr:
                last_digit = int(partner.social_sec_nr[-1])
                if last_digit % 2 == 0:
                    partner.gender = 'female'
                else:
                    partner.gender = 'male'

    @api.depends('social_sec_nr')
    @api.constrains("social_sec_nr")
    def calculate_age(self):
        for rec in self:
            wrong_input = False
            today = date.today()
            social_sec = rec.social_sec_nr
            social_sec_stripped = ""
            if social_sec:
                error_message = ""
                if re.fullmatch("([0-9]){8}-([0-9]){4}", social_sec):
                    social_sec_stripped = social_sec.split("-")[0]
                elif re.fullmatch("([0-9]){12}", social_sec):
                    social_sec_stripped = social_sec[:8]
                    rec.social_sec_nr = "%s-%s" % (
                        social_sec_stripped,
                        social_sec[8:12],
                    )
                elif re.fullmatch("([0-9]){6}-([0-9]){4}", social_sec):
                    social_sec_stripped = social_sec.split("-")[0]
                    wrong_input = True
                    error_message = _(
                        "Social security number %s is formated as YYMMDD-NNNN, this format is not accepted"
                    ) % social_sec
                elif re.fullmatch("([0-9]){10}", social_sec):
                    social_sec_stripped = social_sec[:8]
                    rec.social_sec_nr = "%s-%s" % (
                        social_sec_stripped,
                        social_sec[8:12],
                    )
                    wrong_input = True
                    error_message = _(
                        "Social security number %s is formated as YYMMDDNNNN, this format is not accepted"
                    ) % social_sec
                else:
                    wrong_input = True
                    error_message = _(
                        "Social security number %s is not correctly formated."
                    ) % social_sec
                    _logger.error(error_message)
                date_of_birth = date(1980, 1, 1)
                if len(social_sec_stripped) == 6:
                    yr = social_sec_stripped[:2]
                    year = int("20" + yr)
                    month = int(social_sec_stripped[2:4])
                    day = int(social_sec_stripped[4:6])
                    if day > 60:
                        day = day - 60
                    try:
                        date_of_birth = date(year, month, day)
                    except:
                        wrong_input = True
                        error_message = _(
                            "Could not convert social security number %s to date"
                        ) % social_sec
                        _logger.error(error_message)
                    # if social security numbers with 10 numbers are reallowed,
                    # change this to something more reasonable in case children
                    # are allowed to register
                    if today.year - date_of_birth.year < 18:
                        year = int("19" + yr)
                        try:
                            date_of_birth = date(year, month, day)
                        except:
                            wrong_input = True
                            error_message = _(
                                "Could not convert social security number %s to date"
                            ) % social_sec_stripped
                            _logger.error(error_message)
                elif len(social_sec_stripped) == 8:
                    year = int(social_sec_stripped[:4])
                    month = int(social_sec_stripped[4:6])
                    day = int(social_sec_stripped[6:8])
                    if day > 60:
                        day = day - 60
                    try:
                        date_of_birth = date(year, month, day)
                    except:
                        wrong_input = True
                        error_message = _(
                            "Could not convert social security number %s to date"
                        ) % social_sec_stripped
                        _logger.error(error_message)
                else:
                    wrong_input = True
                    error_message = _(
                        "Incorrectly formated social security number %s"
                    ) % social_sec
                    _logger.error(error_message)

                if not wrong_input:
                    years = today.year - date_of_birth.year
                    if today.month < date_of_birth.month or (
                        today.month == date_of_birth.month and today.day < date_of_birth.day
                    ):
                        years -= 1
                    if years > 67:
                        rec.age = "%s" % years
                        _logger.warn(
                            "A person older than 67 should not be in the system, a person is %s years old"
                            % years
                        )
                    else:
                        rec.age = years

                else:
                    rec.social_sec_nr = ""
                    rec.age = ""
                    raise ValidationError(
                        _(
                            "Please input a correctly formated social security number.\n the correct format is YYYYMMDDNNNN or YYYYMMDD-NNNN.\n %s"
                        ) % error_message
                    )
