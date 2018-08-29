# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
from openerp.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def geo_localize(self):
        res = super(res_partner, self).geo_localize()
        for partner in self:
            if not partner:
                continue
            if partner.street2:
                result = geo_find(geo_query_address(street=partner.street2,
                                                    zip=partner.zip,
                                                    city=partner.city,
                                                    state=partner.state_id.name,
                                                    country=partner.country_id.name))
                if result:
                    partner.write({
                        'partner_latitude': result[0],
                        'partner_longitude': result[1],
                        'date_localization': fields.Date.context_today(partner)
                    })
        return res

    @api.model
    def get_map(self, zoom=12, center=None, partners=None, icon=''):
        if len(partners) > 0:
            map_tmp = """function initMap() {
                    var center = {lat: %s, lng: %s};
                    var map = new google.maps.Map(document.getElementById('map'), {
                      zoom: %s,
                      center: center
                    });
                    %s
                  }"""
            marker_tmp = """
                    var marker%s = new google.maps.Marker({
                        title: '%s',
                        position: {lat: %s, lng: %s},
                        map: map,
                        icon: '%s'
                    });
                  """
            center = center.get_position() if center else partners[0].get_position()
            markers = ''
            for partner in partners:
                pos = partner.get_position()
                markers += marker_tmp %(partner.id, partner.sudo().name, pos['lat'], pos['lng'], icon)
            return map_tmp %(center['lat'], center['lng'], zoom, markers)
        return ''

    @api.multi
    def get_position(self):
        #~ url = ''
        #~ if not self.partner_latitude and (self.street or self.street2):
            #~ url = u'https://maps.googleapis.com/maps/api/geocode/json?address=%s,%s,%s,%s' %(self.street if (self.street and not self.street2) else self.street2, self.zip, self.city, self.country_id.name)
            #~ try:
                #~ geo_info = urllib.urlopen(url.encode('ascii', 'xmlcharrefreplace')).read()
                #~ geo = json.loads(geo_info)
                #~ result = geo.get('results')
                #~ if len(result) > 0:
                    #~ geometry = result[0].get("geometry")
                    #~ if geometry:
                        #~ self.partner_latitude = geometry["location"]["lat"]
                        #~ self.partner_longitude = geometry["location"]["lng"]
            #~ except ValueError as e:
                #~ _logger.error(e)
        if self.sudo().partner_latitude == 0.0 and self.sudo().partner_longitude == 0.0:
            self.geo_localize()
        return {'lat': self.sudo().partner_latitude, "lng": self.sudo().partner_longitude}
