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
from odoo.exceptions import UserError, AccessError
from odoo.addons.api_ipf_tlr_client.models.client_config import ClientConfig

_logger = logging.getLogger(__name__)


def get_api(self):
    return self.env['ipf.tlr.client.config'].sudo().search([], limit=1)


if not hasattr(ClientConfig, 'get_api'):
    ClientConfig.get_api = get_api



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    """
    The structure of the incoming data is as follows (simplified):
    <organization>
        <contact_person></contact_person>
        <subsidiary>
            <adress>
                <contact_person></contact_person>
            </adress>
        </subsidiary>
    </organization>
    """

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
                ('ns23:avtalId', 'category_id.name'),
            ],
            'address': [
                ('ns23:adressId', 'legacy_no'),
                ('ns23:adressrad', 'street'),
                ('ns23:postnummer', 'zip'),
                ('ns23:postort', 'city'),
                ('ns23:lanskod', 'country_id.name'),
                ('ns23:kommunkod', 'state_id.name'),
            ]
        }

    @api.model
    def clearing_xml(self, xml):
        return re.sub(r"<\?xml.*\?>", '', xml)

    def update_tlr_data_action(self):
        granted = False
        for group in ('base.group_system', ):
            if self.env.user.has_group(group):
                granted = True
                break
        if not granted:
            raise AccessError(_("You are not allowed to sync data with TLR."))
        try:
            self._update_tlr_data()
        except Exception as e:
            _logger.error('TLR APi error: %s', e)
            raise UserError(_('Api error'))

    def _update_tlr_data(self):
        self.ensure_one()
        legacy_no = self.env['ir.config_parameter'].sudo().get_param('dafa.legacy_no')
        if legacy_no:
            api_client = self.env['ipf.tlr.client.config'].sudo().get_api()
            if api_client:
                response = api_client.get_tjansteleverantor(legacy_no)
                if response.status_code == 200:
                    self.parse_xml_tjansteleverantor_data(response.text)
                    _logger.info("PARSED XML")

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
        contact_persons = root.findall(
            ".//ns300:tjansteleverantor/ns107:kontaktpersonLista", 
                namespaces={'ns300': "http://arbetsformedlingen.se/tjansteleverantor/response/hamtatjansteleverantorsvar/v15",
                'ns107': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjansteleverantor/v15'})
        if contact_persons:
            _logger.info("CONTACT PERSONS NOT NONE")
            for elem in contact_persons:
                self.update_contact_person(elem, self.id)
        subsidiaries = root.findall(
            ".//ns107:utforandeVerksamhetLista", namespaces={'ns107': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjansteleverantor/v15'})
        if subsidiaries:
            _logger.info("SUBSIDIARY NOT NONE")
            for elem in subsidiaries:
                self.update_subsidiary(elem)

    @api.multi
    def update_contact_person(self, xml, parent_id):
        person_id = xml.find(".//ns25:kontaktpersonId", namespaces={'ns25':'http://arbetsformedlingen.se/datatyp/tjansteleverantor/kontaktperson/v17'})
        if person_id is not None:
            person_id = person_id.text
            children = self.env['res.users'].search([('parent_id', '=', parent_id),
                                    ('legacy_no', '=', person_id)], limit=1)
            if children:
                _logger.info("found children contact persons")
                user = children
            else:
                _logger.info("creating contact person partner")
                user = self.env['res.users'].create([{
                    'name': 'From TLR',
                    'parent_id': self.id,
                    'login': 'FromTLR'
                }])
            user.partner_id.update_from_xml(xml, 'contact_persons')
            employee = self.env['hr.employee'].create({
                'name': user.name,
                })
            user.write({
                'employee_ids': [(6,0,[employee.id])],
                'login': "_".join((user.partner_id.email,user.partner_id.legacy_no))
                })

    @api.multi
    def update_subsidiary(self, xml):
        subsidiary_id = xml.find(".//ns64:utforandeVerksamhetId",
                                 namespaces={'ns64': 'http://arbetsformedlingen.se/datatyp/tjansteleverantor/utforandeverksamhet/v15'})
        if subsidiary_id is not None:
            subsidiary_id = subsidiary_id.text
            children = self.env['performing.operation'].search([('company_id', '=', self.id),
                                                ('ka_nr', '=', subsidiary_id)], limit=1)
            if children:
                _logger.info("found children subsidiaries")
                subsidiary = children
            else:
                _logger.info("creating subsidiary partner")
                subsidiary = self.env['performing.operation'].create([{
                    'name': 'From TLR',
                    'company_id': self.id,
                }])
            subsidiary.update_from_xml(xml, 'subsidiary', self.match_list())
            addresses = xml.findall(
                ".//ns64:adressLista", namespaces={'ns64': "http://arbetsformedlingen.se/datatyp/tjansteleverantor/utforandeverksamhet/v15"})
            if addresses:
                _logger.info("ADDRESSES NOT NONE")
                for elem in addresses:
                    self.update_sub_address(elem, subsidiary.id)
        

    @api.multi
    def update_sub_address(self, xml, performing_operation_id):
        address_id = xml.find(".//ns23:adressId",
                                 namespaces={'ns23': "http://arbetsformedlingen.se/datatyp/tjansteleverantor/adress/v15"})
        if address_id is not None:
            address_id = address_id.text
            children = self.search([('performing_operation_id', '=', performing_operation_id),
                                    ('legacy_no', '=', address_id)], limit=1)
            if children:
                _logger.info("found children addresses")
                partner = children
            else:
                _logger.info("creating address partner")
                partner = self.create([{
                    'performing_operation_id': performing_operation_id, 
                    'type': 'other'
                }])
            partner.update_from_xml(xml, 'address')
            contact_persons = xml.find(
                ".//ns23:kontaktperson", namespaces={'ns23': "http://arbetsformedlingen.se/datatyp/tjansteleverantor/adress/v15"})
            if contact_persons is not None:
                _logger.info("CONTACT PERSONS NOT NONE")
                for elem in contact_persons:
                    self.update_contact_person(elem, partner.id)
            
class PerformingOperation(models.Model):
    _inherit = 'performing.operation'

    def update_from_xml(self, xml, match_name, match_list):    
        match_fields = match_list[match_name]
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