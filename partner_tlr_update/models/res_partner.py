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
from odoo.exceptions import UserError, Warning, AccessError
from odoo.addons.api_ipf_tlr_client.models.client_config import ClientConfig

_logger = logging.getLogger(__name__)


def get_api(self):
    return self.env['ipf.tlr.client.config'].sudo().search([], limit=1)


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
        granted = False
        for group in ('base.group_system'):
            if self.env.user.has_group(group):
                granted = True
                break
        if not granted:
            raise AccessError(_("You are not allowed to sync data with TLR."))
        try:
            self.update_tlr_data()
        except Exception as e:
            _logger.error('TLR APi error: %s', e)
            raise UserError(_('Api error'))

    def update_tlr_data(self):
        self.ensure_one()
        legacy_no = self.env['ir.config_parameter'].sudo().get_param('dafa.legacy_no')
        if legacy_no:
            api_client = self.env['ipf.tlr.client.config'].sudo().get_api()
            if api_client:
                response = api_client.get_tjansteleverantor(legacy_no)
                if response.status_code == 200:
                    self.parse_xml_tjansteleverantor_data(response.text)
                    _logger.info("PARSED XML")
                #response = api_client.get_utforande_verksamhet_id()
                if response.status_code == 200:
                    self.parse_xml_organisationsnummer_data(response.text)
                    _logger.info("PARSED XML 2")

    def update_from_xml(self, xml, match_name):    
        match_fields = self.match_list()[match_name]
        _logger.info("match_fields %s" % match_fields)
        data = {}
        for field in match_fields:
            country = False
            _logger.info("field[0]: %s" % field[0])
            elem = xml.find(".//%s" % field[0], namespaces={
                'ns107': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjansteleverantor/v15',
                'ns25':'http://arbetsformedlingen.se/datatyp/tjansteleverantor/kontaktperson/v17',
                'ns64': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/utforandeverksamhet/v15',
                'ns23':'http://arbetsformedlingen.se/datatyp/tjansteleverantor/adress/v15',
                'ns26':'http://arbetsformedlingen.se/datatyp/gemensam/personnamn/v0',
                'ns27':'http://arbetsformedlingen.se/datatyp/tjansteleverantor/teleadress/v4',
                })
            if elem is not None:
                _logger.info("field[1] %s" % field[1])
                _logger.info("elem text %s" % elem.text)
                if field[1] == 'state_id.name' and country:
                    _logger.info("field[1] == state_id.name and country")
                    state = self.state_id.search([
                        ('name', '=', elem.text),
                        ('country_id', '=', country)], limit=1)
                    if not state:
                        state = state.create({'name': elem.text,
                                              'country_id': country})
                    data['state_id'] = state.id
                elif '.' in field[1]:
                    _logger.info("'.' in field[1]")
                    field_model, field_name = field[1].split('.')
                    if field_model in self and field_name in self[field_model]:
                        value_id = self[field_model].search([
                            (field_name, '=', elem.text)], limit=1)
                        if value_id:
                            data[field_model] = value_id.id
                            if field[1] == 'country_id.name':
                                country = value_id.id
                elif field[1] in self:
                    _logger.info("field[1] in self")
                    data[field[1]] = elem.text
        _logger.info("data %s" % data)
        if data:
            self.write(data)

    @api.model
    def parse_xml_tjansteleverantor_data(self, xml):
        root = etree.XML(xml.encode())
        self.update_from_xml(root, 'organization')
        _logger.info("UPDATE FROM XML")
        contact_persons = root.find(
            ".//ns107:kontaktpersonLista", namespaces={'ns107': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjansteleverantor/v15'})
        _logger.info("CONTACT PERSONS FOUND")
        if contact_persons is not None:
            _logger.info("CONTACT PERSONS NOT NONE")
            self.update_contact_person(contact_persons)

    @api.model
    def parse_xml_organisationsnummer_data(self, xml):
        #_logger.info("XML: %s" % xml)
        root = etree.fromstring(self.clearing_xml(xml))
        _logger.info("ROOT: %s" % root)
        self.update_subsidiary(root)

    @api.multi
    def update_contact_person(self, xml):
        person_id = xml.find(".//ns25:kontaktpersonId", namespaces={'ns25':'http://arbetsformedlingen.se/datatyp/tjansteleverantor/kontaktperson/v17'})
        if person_id is not None:
            person_id = person_id.text
            children = self.search([('parent_id', '=', self.id),
                                    ('legacy_no', '=', person_id)], limit=1)
            if children:
                _logger.info("found children contact persons")
                partner = children
            else:
                _logger.info("creating contact person partner")
                partner = self.create([{
                    'name': 'From TLR',
                    'parent_id': self.id,
                }])
            partner.update_from_xml(xml, 'contact_persons')

    @api.multi
    def update_subsidiary(self, xml):
        subsidiary_id = xml.find(".//ns64:utforandeVerksamhetId",
                                 namespaces={'ns64': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/utforandeverksamhet/v15'})
        if subsidiary_id is not None:
            subsidiary_id = subsidiary_id.text
            children = self.search([('parent_id', '=', self.id),
                                    ('legacy_no', '=', subsidiary_id)], limit=1)
            if children:
                _logger.info("found children subsidiaries")
                partner = children
            else:
                _logger.info("creating subsidiary partner")
                partner = self.create([{
                    'name': 'From TLR',
                    'parent_id': self.id,
                    'type': 'other',
                }])
            partner.update_from_xml(xml, 'subsidiary')
