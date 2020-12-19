from odoo import models, fields, api, _
from datetime import date
import logging
from odoo.exceptions import ValidationError
import re


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    age = fields.Char(string="Age", compute="calculate_age")
    company_registry = fields.Char(
        string='Organization number', help="organization number")
    social_sec_nr = fields.Char(string="Social security number", related="company_registry")
    social_sec_nr_age = fields.Char(string="Social security number", compute="combine_social_sec_nr_age")

    _sql_constraints = [
        ('company_registry_unique', 
        'UNIQUE(company_registry)',
        'company_registry (social security number/organization number) field needs to be unique'
        ), 
        ('customer_id_unique', 
        'UNIQUE(customer_id)',
        'customer_id field needs to be unique'
        )]

    @api.one
    @api.constrains("company_registry")
    def calculate_age(self):
        wrong_input = False
        today = date.today()
        social_sec = self.company_registry
        social_sec_stripped = ""
        if social_sec:
            error_message = ""
            if re.fullmatch("([0-9]){8}-([0-9]){4}", social_sec):
                social_sec_stripped = social_sec.split("-")[0]
            elif re.fullmatch("([0-9]){12}", social_sec):
                social_sec_stripped = social_sec[:8]
                self.company_registry = "%s-%s" % (
                    social_sec_stripped,
                    social_sec[8:12],
                )
            else:
                wrong_input = True
                error_message = _(
                    "Social security number %s (company_registry field) is not correctly formated or an incorrect length"
                    % social_sec
                )
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
                        "Could not convert social security number %s (company_registry field) to date"
                        % social_sec
                    )
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
                            "Could not convert social security number %s (company_registry field) to date"
                            % social_sec_stripped
                        )
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
                        "Could not convert social security number %s (company_registry field) to date"
                        % social_sec_stripped
                    )
                    _logger.error(error_message)
            else:
                wrong_input = True
                error_message = _(
                    "Incorrectly formated social security number %s (company_registry field)"
                    % social_sec
                )
                _logger.error(error_message)

            if not wrong_input:
                years = today.year - date_of_birth.year
                if today.month < date_of_birth.month or (
                    today.month == date_of_birth.month and today.day < date_of_birth.day
                ):
                    years -= 1
                if years > 67:
                    self.age = _("This person is too old, at %s years old") % years
                    _logger.warn(
                        "A person older than 67 should not be in the system, a person is %s years old"
                        % years
                    )
                else:
                    self.age = years

            else:
                self.social_sec_nr = ""
                self.age = ""
                raise ValidationError(
                    _(
                        "Please input a correctly formated social security number.\n %s"
                        % error_message
                    )
                )