# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
################################################################################

import re
import logging
from lxml import etree
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.addons.api_ipf_tlr_client.models.client_config import ClientConfig

_logger = logging.getLogger(__name__)


def get_api(self):
    return self.env['ipf.tlr.client.config'].search([], limit=1)


if not hasattr(ClientConfig, 'get_api'):
    ClientConfig.get_api = get_api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def match_list(self):
        return {
            'organization': [
                ('ns107:tjansteleverantorId', 'legacy_no'),
                ('ns107:namn', 'name'),
                ('ns107:organisationsnummer', 'company_registry'),
                ('ns107:hemsida', 'website'),
                ('ns107:teleadressfax', 'fax'),
                ('ns107:telefonnummer', 'phone'),
            ],
            'contact_persons': [
                ('ns25:kontaktpersonId', 'legacy_no'),
                ('ns26:Fornamn', 'firstname'),
                ('ns26:Efternamn', 'lastname'),
                ('ns27:telefonnummer', 'phone'),
                ('ns25:epost', 'email'),
            ],
            'subsidiary': [
                ('ns64:utforandeVerksamhetId', 'legacy_no'),
                ('ns64:namn', 'name'),
                ('ns23:adressrad', 'street'),
                ('ns23:postnummer', 'zip'),
                ('ns23:postort', 'city'),
                ('ns23:lanskod', 'country_id.name'),
                ('ns23:kommunkod', 'state_id.name'),
                ('ns23:avtalId', 'category_id.name'),
            ]
        }

    @api.model
    def clearing_xml(self, xml):
        return re.sub(r"<\?xml.*\?>", '', xml)

    def update_tlr_data_action(self):
        try:
            self.update_tlr_data()
        except Exception as e:
            _logger.error('TLR APi error: %s', e)
            raise UserError(_('Api error'))

    def update_tlr_data(self):
        self.ensure_one()
        if self.legacy_no:
            api_client = self.env['ipf.tlr.client.config'].get_api()
            if api_client:
                response = api_client.get_tjansteleverantor(self.legacy_no)
                if response.status_code == 200:
                    self.parse_xml_tjansteleverantor_data(response.text)
                response = api_client.get_utforande_verksamhet_id(
                    self.legacy_no)
                if response.status_code == 200:
                    self.parse_xml_organisationsnummer_data(response.text)

    def update_from_xml(self, xml, match_name):
        match_fields = self.match_list()[match_name]
        data = {}
        for field in match_fields:
            country = False
            elem = xml.find(".//%s" % field[0], namespaces=xml.nsmap)
            if elem is not None:
                if field[1] == 'state_id.name' and country:
                    state = self.state_id.search([
                        ('name', '=', elem.text),
                        ('country_id', '=', country)], limit=1)
                    if not state:
                        state = state.create({'name': elem.text,
                                              'country_id': country})
                    data['state_id'] = state.id
                elif '.' in field[1]:
                    field_model, field_name = field[1].split('.')
                    if field_model in self and field_name in self[field_model]:
                        value_id = self[field_model].search([
                            (field_name, '=', elem.text)], limit=1)
                        if value_id:
                            data[field_model] = value_id.id
                            if field[1] == 'country_id.name':
                                country = value_id.id
                elif field[1] in self:
                    data[field[1]] = elem.text

        if data:
            self.write(data)

    @api.model
    def parse_xml_tjansteleverantor_data(self, xml):
        root = etree.XML(xml)
        self.update_from_xml(root, 'organization')
        contact_persons = root.find(
            ".//ns107:kontaktpersonLista", namespaces=root.nsmap)
        if contact_persons is not None:
            self.update_contact_person(contact_persons)

    @api.model
    def parse_xml_organisationsnummer_data(self, xml):
        root = etree.fromstring(self.clearing_xml(xml))
        self.update_subsidiary(root)

    @api.multi
    def update_contact_person(self, xml):
        person_id = xml.find(".//ns25:kontaktpersonId", namespaces=xml.nsmap)
        if person_id is not None:
            person_id = person_id.text
            children = self.search([('parent_id', '=', self.id),
                                    ('legacy_no', '=', person_id)], limit=1)
            if children:
                partner = children
            else:
                partner = self.create([{
                    'name': 'From TLR',
                    'parent_id': self.id,
                }])
            partner.update_from_xml(xml, 'contact_persons')

    @api.multi
    def update_subsidiary(self, xml):
        subsidiary_id = xml.find(".//ns64:utforandeVerksamhetId",
                                 namespaces=xml.nsmap)
        if subsidiary_id is not None:
            subsidiary_id = subsidiary_id.text
            children = self.search([('parent_id', '=', self.id),
                                    ('legacy_no', '=', subsidiary_id)], limit=1)
            if children:
                partner = children
            else:
                partner = self.create([{
                    'name': 'From TLR',
                    'parent_id': self.id,
                    'type': 'other',
                }])
            partner.update_from_xml(xml, 'subsidiary')
