# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging
import threading
import base64
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tools import image_resize_image_big, image_colorize
from odoo.modules import get_module_resource
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_name = "name_ssn"

    @api.one
    def _compute_eidentification(self):
        bankid_token = self.env["res.partner.bankid"].search(
            [("partner_id", "=", self.id), ("user_id", "=", self.env.user.id)], limit=1
        )
        self.eidentification = bankid_token.name if bankid_token else False

    work_phone = fields.Char(string="Work phone", help="Work phone number") #is added in partner_extension_af
    cfar = fields.Char(string="CFAR", help="CFAR number") #is added in partner_extension_af
    customer_id = fields.Char(
        string="Customer number", help="Customer number", index=True
    ) #is added in partner_extension_af
    eidentification = fields.Char(
        string="E-Identification",
        help="BankId or other e-identification done OK or other",
        compute="_compute_eidentification"
    )

    type = fields.Selection(
        selection_add=[
            ("foreign address", "Foreign Address"),
            ("given address", "Given address"),
            ("visitation address", "Visitation Address"),
            ("mailing address", "Mailing Address"),
        ]
    ) #is added in partner_extension_af

    is_jobseeker = fields.Boolean(string="Jobseeker", index=True) #is added in partner_extension_af
    is_independent_partner = fields.Boolean(string="Independent partner") #is added in partner_extension_af
    is_government = fields.Boolean(string="Government") #is added in partner_extension_af
    is_employer = fields.Boolean(string="Employer", index=True) #is added in partner_extension_af

    jobseeker_category_id = fields.Many2one(comodel_name="res.partner.skat") #is added in partner_extension_af
    jobseeker_category = fields.Char(
        string="Jobseeker category", compute="combine_category_name_code"
    ) #is added in partner_extension_af
    customer_since = fields.Datetime(string="Customer since") #is added in partner_extension_af
    jobseeker_work = fields.Boolean(string="Work") #is added in partner_extension_af
    deactualization_date = fields.Datetime(string="Deactualization date") #is added in partner_extension_af
    deactualization_reason = fields.Char(
        string="Deactualization reason"
    )  # egen modell?
    foreign_country_of_work = fields.Char(string="When working in foreign country") #is added in partner_extension_af
    deactualization_message = fields.Text(
        string="Message to jobseeker regarding deactualization"
    )

    registered_through = fields.Selection(
        selection=[
            ("pdm", "PDM"),
            ("self service", "Self service"),
            ("local office", "Local office"),
        ],
        string="Registered Through",
    )  # is added in partner_extension_af
    match_area = fields.Selection(
        selection=[
            ("Krom", "Ja"),
            ("KromEsf", "Ja"),
            ("EjKrom", "Nej"),
        ],
        string="Rusta och matcha-område",
    )
    share_info_with_employers = fields.Boolean(
        string="Share name and address with employers"
    ) #is added in partner_extension_af
    sms_reminders = fields.Boolean(string="SMS reminders") #is added in partner_extension_af
    visitation_address_id = fields.Many2one("res.partner", string="Visitation address") #is added in partner_extension_af

    given_address_id = fields.Many2one("res.partner", string="given address") # Add to a separate module
    given_address_street = fields.Char(
        string="given address", related="given_address_id.street"
    ) #is added in partner_extension_af
    given_address_zip = fields.Char(related="given_address_id.zip")
    given_address_city = fields.Char(related="given_address_id.city")
    employer_class = fields.Selection(
        selection=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")]
    ) # Add to a separate module

    state_code = fields.Char(string="State code", related="state_id.code") # Moved to l10n_se
    state_name_code = fields.Char(
        string="Municipality", compute="combine_state_name_code"
    )  # Moved to l10n_se

    zip_formated = fields.Char(string="Zip", compute="_compute_zip_format")

    office_code_name = fields.Char(string="office", compute='_compute_office_code_name')

    user_name_sign = fields.Char(string="Administrative officer", compute='_compute_user_name_sign')

    temp_officer_id = fields.Many2many(
        comodel_name="res.users",
        relation="res_partner_temp_officer_rel",
        string="Temporary Officers",
    )

    segment_jobseeker = fields.Selection(
        string="Jobseeker segment",
        selection=[("a", "A"), ("b", "B"), ("c1", "C1"), ("c2", "C2"), ("c3", "C3")],
    ) #is added in partner_extension_af
    segment_employer = fields.Selection(
        string="Employer segment",
        selection=[
            ("including 1", "Including 1"),
            ("including 2", " Including 2"),
            ("entry job", "Entry job"),
            ("national agreement", "National agreement"),
            ("employment subsidy", "Employment subsidy"),
        ],
    ) #is added in partner_extension_af

    name_ssn = fields.Char(compute="_compute_name_ssn", store=True)

    _sql_constraints = [
        ('customer_id_unique',
        'UNIQUE(customer_id)',
        'customer_id field needs to be unique'
        )]

    @api.constrains('zip')
    @api.one
    def _constrain_zip(self):
        if self.zip and not self.zip.isdecimal():
            raise ValidationError(_("Zip field must only contain numbers and no spaces"))

    @api.one
    def _compute_zip_format(self):
        if self.zip and len(self.zip) == 5:
            self.zip_formated = "%s %s" % (self.zip[:3], self.zip[3:])
        else:
            self.zip_formated = self.zip

    @api.one
    def combine_state_name_code(self):
        self.state_name_code = "%s %s" % (self.state_id.code, self.state_id.name)

    @api.one
    def _compute_user_name_sign(self):
        self.user_name_sign = "%s %s" % (self.user_id.name, self.user_id.login)

    @api.one
    def _compute_office_code_name(self):
        self.office_code_name = "%s %s" % (self.office_id.office_code, self.office_id.name)

    @api.one
    def combine_category_name_code(self):
        self.jobseeker_category = "%s %s" % (
            self.jobseeker_category_id.code,
            self.jobseeker_category_id.name,
            #date set here
        )

    def update_partner_images(self):
        for partner in self:
            colorize = False
            if partner.type == "invoice":
                img_path = get_module_resource("base", "static/img", "money.png")
            elif partner.type == "delivery":
                img_path = get_module_resource("base", "static/img", "truck.png")
            elif partner.type == "foreign address":
                img_path = get_module_resource(
                    "partner_view_360", "static/src/img", "foreign_address.png"
                )
            elif partner.type == "given address":
                img_path = get_module_resource(
                    "partner_view_360", "static/src/img", "given_address.png"
                )
            elif partner.type == "visitation address":
                img_path = get_module_resource(
                    "partner_view_360", "static/src/img", "visitation_address.png"
                )
            elif partner.type == "private":
                img_path = get_module_resource(
                    "partner_view_360", "static/src/img", "private_address.png"
                )
            elif partner.is_company:
                img_path = get_module_resource(
                    "base", "static/img", "company_image.png"
                )
            else:
                img_path = get_module_resource("base", "static/img", "avatar.png")
                colorize = True

            if img_path:
                with open(img_path, "rb") as f:
                    image = f.read()
            if image and colorize:
                image = image_colorize(image)

            partner.image = image_resize_image_big(base64.b64encode(image))

    @api.model
    def _get_default_image(self, partner_type, is_company, parent_id):
        if getattr(threading.currentThread(), "testing", False) or self._context.get(
            "install_mode"
        ):
            return False

        colorize, img_path, image = False, False, False
        if partner_type in ["other"] and parent_id:
            parent_image = self.browse(parent_id).image
            image = parent_image and base64.b64decode(parent_image) or None

        if not image and partner_type == "invoice":
            img_path = get_module_resource("base", "static/img", "money.png")
        elif not image and partner_type == "delivery":
            img_path = get_module_resource("base", "static/img", "truck.png")
        elif not image and partner_type == "foreign address":
            img_path = get_module_resource(
                "partner_view_360", "static/src/img", "foreign_address.png"
            )
        elif not image and partner_type == "given address":
            img_path = get_module_resource(
                "partner_view_360", "static/src/img", "given_address.png"
            )
        elif not image and partner_type == "visitation address":
            img_path = get_module_resource(
                "partner_view_360", "static/src/img", "visitation_address.png"
            )
        elif not image and partner_type == "private":
            img_path = get_module_resource(
                "partner_view_360", "static/src/img", "private_address.png"
            )
        elif not image and is_company:
            img_path = get_module_resource("base", "static/img", "company_image.png")
        elif not image:
            img_path = get_module_resource("base", "static/img", "avatar.png")
            colorize = True

        if img_path:
            with open(img_path, "rb") as f:
                image = f.read()
        if image and colorize:
            image = image_colorize(image)

        return image_resize_image_big(base64.b64encode(image))

    @api.multi
    def close_view(self):
        return {
            "name": _("Search Jobseekers"),
            "view_type": "form",
            "res_model": "hr.employee.jobseeker.search.wizard",
            "view_id": False,  # self.env.ref("partner_view_360.search_jobseeker_wizard").id,
            "view_mode": "form",
            "target": "inline",
            "type": "ir.actions.act_window",
        }

    def update_name_ssn(self):
        for partner in self:
            name = partner.name
            if partner.social_sec_nr:
                name += " " + partner.social_sec_nr
            partner.name_ssn = name
            partner.name = partner.name

    @api.depends("name", "social_sec_nr")
    def _compute_name_ssn(self):
        for partner in self:
            name = partner.name
            if partner.social_sec_nr:
                name += " " + partner.social_sec_nr
            partner.name_ssn = name

    @api.multi
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            if partner.company_registry:
                name += " " + partner.company_registry
            result.append((partner.id, name))
        return result

    # Grant temporary access to these jobseekers or set this user as
    # responsible for the jobseeker
    @api.multi
    def escalate_jobseeker_access(self, arendetyp, user):
        return (250, "OK")

    @api.one
    def write(self, vals):
        user_id = vals.get("user_id", False)
        if user_id and user_id == self.env.user.id:
            raise Warning(_("You can't set yourself as responsible case worker"))
        else:
            super(ResPartner, self).write(vals)

    @api.model
    def create(self, values):
        zip = values.get('zip')
        if zip:
            if zip and not zip.isdecimal():
                raise ValidationError(_("Zip field must only contain numbers and no spaces"))
        return super(ResPartner, self).create(values)

    @api.model
    def search_pnr(self, pnr):
        domain = []
        if len(pnr) == 13 and pnr[8] == "-":
            domain.append(("social_sec_nr", "=", pnr))
        elif len(pnr) == 12:
            domain.append(
                ("social_sec_nr", "=", "%s-%s" % (pnr[:8], pnr[8:12])))
        else:
            raise ValidationError(_("Incorrectly formated social security number: %s") % pnr)
        # unless we raised an error, return the result of the search
        return self.env['res.partner'].sudo().search(domain, limit=1)

class ResPartnerSKAT(models.Model):
    _name = "res.partner.skat"

    partner_id = fields.One2many(
        comodel_name="res.partner", inverse_name="jobseeker_category"
    )
    code = fields.Char(string="code")
    name = fields.Char(string="name")
