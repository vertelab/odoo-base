from odoo import models, fields, api, _
from odoo.addons.partner_autocomplete.models.res_company import COMPANY_AC_TIMEOUT
from datetime import date
import logging
from odoo.exceptions import ValidationError
import re

from allabolag import Company
from allabolag.liquidated_companies import iter_liquidated_companies
from allabolag.list import iter_list
from copy import deepcopy
from datetime import datetime
from urllib.parse import quote
from odoo.addons.partner_allabolag.tools.logoscrape import LogoScrape, name2url


_logger = logging.getLogger(__name__)
COMPANY_NO_IAP=True


class ResPartnerMixin(models.AbstractModel):
    _name = "res.partner.allabolag.mixin"
    _description = """
        Mixin class for Allabolag-information
    
    """

    kpi_no_employees = fields.Integer(string='Number of employees')
    kpi_revenue_employees = fields.Float(string='Revenue per Employee')
    linkTo = fields.Char(string='Link', size=64, trim=True, help="Link to Allabolag")
    remarkCode = fields.Char(string='Remark', size=4)
    remarkDate = fields.Date(string='Remark Date') # fields.date.add|context_today|end_of|start_of|substract|to_date|to_string|today
    remarkDescription = fields.Char(string='Remark Descr', trim=True, )
    summary_cash_flow = fields.Float(string='Cash Flow')
    summary_net_sales_change = fields.Float(string='Net Sales Changes')
    summary_parent_company = fields.Char(string='Parent Company')
    summary_profit_ebit = fields.Float(string='Profit EBIT KSEK')
    summary_profit_margin = fields.Float(string='Profit Margin')
    summary_purpose = fields.Text(string='Business and purpose')
    summary_registry_year = fields.Date(string='Registry Year')
    summary_revenue = fields.Float(string='Revenue KSEK')
    summary_solvency = fields.Float(string='Solvency')
    summary_state = fields.Char(string='Business status')
    
    @api.model
    def name2orgno(self,name):
        name = quote(name)
        i = 1
        for item in iter_list(
            f"what/{name}/xs/1",
            # ~ lambda x: _parse_liquidated_company_item(x)["Konkurs inledd"] < until,
            ):
            print(item.keys())
            i += 1
            if i > 1:
                break 
        if i == 1:
            return None,None
        _logger.warning(f'{item=}')
        
        return item['orgnr'],item
        
    def partner_enrich_allabolag(self,company_registry):

        partner = Company(company_registry)
        _logger.warning(f'{partner.data=}')
        
        allabolag = {
        # ~ "Översikt - Besöksadress" :
        # ~ "Översikt - Ort" :
        # ~ "Översikt - Län" :
        "Översikt - Omsättning" : "summary_revenue",
        "Översikt - Årets resultat" : "summary_profit_ebit",
        "Aktivitet och status - Verksamhet & ändamål" : "summary_purpose",
        "Nycketal - Antal anställda" : "kpi_no_employees",
        "Nycketal - Nettoomsättningförändring" : "summary_net_sales_change" ,
        "Nycketal - Vinstmarginal" : "summary_profit_margin" ,
        "Nycketal - Soliditet" : "summary_solvency" ,
        "Nycketal - Kassalikviditet" : "summary_cash_flow" ,
        'Nycketal - Nettoomsättning per anställd (tkr)': 'kpi_revenue_employees',
        "Översikt - Besöksadress" : "street",
        'Översikt - Utdelningsadress': 'street',
        "Översikt - Ort" : "city",
        "Översikt - Telefon" : "phone",
        'Aktivitet och status - Bolaget registrerat': 'summary_registry_year',
        'Aktivitet och status - Status':  'summary_state',
        'Aktivitet och status - Moderbolag': 'summary_parent_company',
        }

        # ~ _logger.warning(f"{self.fields_get()=}")
        #for key in self.fields_get():
        #        fields_dict[key] = self[key]
        zipcode = ''
        f = self.fields_get()
        record = {allabolag[k]:partner.data[k] for k in allabolag.keys() if partner.data.get(k,False) }
        for k in record.keys():
            _logger.warning(f"{k= } {f[k]['type']=} {record[k]=}")
            if k == 'city':
                zipcode,record['city'] = partner.data["Översikt - Ort"].split('  ')
                continue
            if f[k]['type'] == 'integer':
                if type(record[k]) == list:
                    record[k]=int(record[k][0][1] or 0)
                else:
                    record[k]=int(record[k] or 0)
                    
            if f[k]['type'] in ['float', 'monetary']:
                if type(record[k]) == list:
                    record[k]=record[k][0][1]
                else:
                    record[k]=record[k]
            if f[k]['type'] in ['char', 'text', 'html']:
                if type(record[k]) == list:
                    record[k]= ', '.join(record[k]) 
                else:
                    record[k]=record[k]
        
        record['vat'] = self.orgnr2vat(company_registry)
        record['zip'] = zipcode
        if "\n" in record.get('street',''):
            record['street'],record['street2'] = [s.strip() for s in record['street'].split('\n')+['.','.'] if s.strip() > ''][0:2]
            if record['street'] == record['street2']:
                record['street2'] = ''
        _logger.warning(f"write {partner.data=}")
        if partner.data.get('remarks'):
            self.write(partner.data['remarks'])
            partner.message_post(body=_(f'{partner.data["remarks"]["remarkCode"]=} {partner.data["remarks"]["remarkDescription"]=} {partner.data["remarks"]["remarkDate"]=}'), message_type='notification')
            _logger.warning(f"write record[k]=")
        
        return record
                    
        # ~ _logger.warning(f'{record=}')

        
        # ~ self.env['res.partner'].write({'summary_revenue': 1000000663, 'summary_profit_ebit': 999999999, 'summary_purpose': 'Bolaget har till föremål för sin verksamhet att bedriva finansieringsrörelse och därmed sammanhängande verksamhet huvudsakligen genom att lämna och förmedla kredit avseende fastigheter och bostads- rätter, att lämna kredit till samfällighetsföreningar, att lämna kredit till stat, landsting, kommuner, kommunalförbund eller andra kommunala samfälligheter, samt - mot borgen av sådan samfällighet - till andra juridiska personer, att genom lämnande av betalningsgaranti underlätta kreditgivning av det slag bolaget får bedriva, samt att för annans räkning förvalta sådana lån jämte säkerheter som avses i denna paragraf samt ombesörja inteckningsåtgärder, Med "fastighet" avses i denna bolagsordning också tomträtt och byggnad på mark upplåten med nyttjanderätt samt ägarlägenheter. Med "bostadsrätt" avses även andel i bostadsförening eller aktie i bostadsaktiebolag, där en utan begränsning i tiden upplåten nyttjanderätt till en lägenhet är oskiljaktigt förenad med andelen eller aktien. Med "kredit" avses också byggnadskreditiv. Ord och uttryck som används i denna bolagsordning för att beteckna visst slag av egendom eller rättigheter innefattar egendom eller rättighet i samtliga länder där bolaget bedriver verksamhet, om kreditsäkerhetsegenskaperna för egendomen eller säkerheten i fråga väsentligen motsvarar vad som avses med den svenska benämningen. Med stat, kommun, landsting och samfällighetsföreningar avses förutom sådana organ i Sverige, motsvarande organ i samtliga länder där Stadshypotek bedriver verksamhet. För anskaffande av medel för sin rörelse får bolaget bl.a. 1. ge ut säkerställda obligationer 2. ge ut andra obligationer och certifikat och ta upp reverslån, 3. ge ut förlagsbevis eller andra förskrivningar som medför rätt till betalning efter bolagets övriga förbindelser, samt 4. utnyttja kredit i räkning.', 'kpi_no_employees': 49, 'summary_net_sales_change': 34, 'summary_profit_margin': 1, 'summary_solvency': 1, 'summary_cash_flow': 1})

    def autocomplete_override(self, query):
        _logger.warning(f"allabolag autocomplete_override {query=}  {self=}")
        res={}
        company_registry, item = self.name2orgno(query)
        if item['hasremarks']:
            for (key,data) in item.get('remarks',[{}])[0].items():
                res['key'] = data
        res['company_registry'] = company_registry
        res['vat'] = self.orgnr2vat(res['company_registry'])

        res['website'] = name2url(query)
        if res['website']:
            res['image_1920'] = LogoScrape(res['website'])
        return self._format_data_company(res)

    @api.model
    def read_by_vat(self, vat):
        _logger.warning(f"read_by_vat {vat=}")
        # ~ return super(ResPartner, self).read_by_vat(vat)
        return []

    
    @api.model
    def enrich_company(self, company_domain, partner_gid, vat,timeout=COMPANY_AC_TIMEOUT):
        _logger.warning(f"allabolag enrich_company {company_domain=} {partner_gid=} {vat=} {self=}")
        company_registry, item = partner.name2orgno(query)
        _logger.warning(f"allabolag {company_registry=} {item=}")
        try:
            if item['hasremarks']:
                # ~ partner.write(item['remarks'][0])
                partner.message_post(body=_(f'{item["remarks"][0]["remarkCode"]=} {item["remarks"][0]["remarkDescription"]=} {item["remarks"][0]["remarkDate"]=}'), message_type='notification')
                _logger.warning(f"write record[k]=")
        except Exception as e:
            _logger.warning(f"_company hasremarks {item=} error {e}")
        _logger.warning(f'{company_registry=}')
        # ~ if company_registry:
            # ~ record = partner.partner_enrich_allabolag(company_registry)
            # ~ _logger.warning(f'{record=}')
            # ~ partner.write(record)
        return self._format_data_company(record)
        
        
        res = {}
        if COMPANY_NO_IAP == True:
            res = super(ResPartner, self).enrich_company(company_domain,partner_gid,vat)
        return res



class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ["res.partner",'res.partner.allabolag.mixin']
    
    def partner_enrich(self):
        _logger.warning(f"allabolag partner_enrich {self=}")
         
        for partner in self:
            if not partner.website:
                try:
                    partner.website = name2url(partner.name)
                    _logger.warning(f"{partner.website=}")
                except Exception as e:
                    _logger.warning(f"Google: An unexpected error occurred: {e}")
                    partner.message_post(body=_(f'Google name2url: unexpected error {e} {partner.name}\nMaybe you can add website manually?'), message_type='notification')
                    continue
            if not partner.image_1920 and partner.website:
                _logger.warning(f"allabolag partner_enrich {LogoScrape(partner.website)=}")
                partner.image_1920 = LogoScrape(partner.website)
            if not partner.company_registry:
                company_registry, item = partner.name2orgno(partner.name)
                if item['hasremarks']:
                    partner.write(item['remarks'][0])
                    partner.message_post(body=_(f'[{item["remarks"][0]["remarkCode"]}] {item["remarks"][0]["remarkDescription"]} {item["remarks"][0]["remarkDate"]}'), message_type='notification')
                partner.company_registry = company_registry

            if partner.company_registry:
                record = partner.partner_enrich_allabolag(partner.company_registry)
                _logger.warning(f'{record=}')
                partner.write(record)
                return self._format_data_company(record)
        super(ResPartner,self).partner_enrich()

    def enrich_allabolag(self):
        if not self.company_type == "company":
            raise UserError(_('This functio has to be on company.'))

        _logger.warning('%s' % self._fields['summary_revenue'])
        if not self.company_registry:
            self.company_registry, items=self.name2orgno(self.name)

        record = self.partner_enrich_allabolag(self.company_registry)
        self.write(record)

    @api.model
    def check_bankruptcy(self):
        until = datetime.strptime('2024-07-01','%Y-%m-%d') #TODO fetch this date from system parameter
        orgnummer=[]
        
        def _parse_liquidated_company_item(item_dict):
            
            item = deepcopy(item_dict)

            # store for backward compability
            item["link"] = item_dict["linkTo"]
            item["Org.nummer"] = item_dict["orgnr"]

            for remark in item_dict["remarks"]:
                key = remark["remarkDescription"]  # ie. Konkurs inledd
                if remark["remarkDate"] is not None:
                    item[key] = datetime.strptime(remark["remarkDate"], "%Y-%m-%d")
                # TODO: Handle other remarks such as:
                # 'remarkCode': 'SHV',
                # 'remarkDescription': 'Svensk Handel Varningslistan med produktnamn: registersök.',
                # 'remarkDate': None,

            return item
        
        i = 1
        for item in iter_list(
                "/lista/konkurs-inledd/6",
                # ~ lambda x: _parse_liquidated_company_item(until=until),
                lambda x: _parse_liquidated_company_item(x)["Konkurs inledd"] < until,
            ):
            orgnummer.append(item['orgnr'])
            i += 1
            if i > 1000:
                break 
        _logger.warning(f'{orgnummer}')
        
        for partner in self.env['res.partner'].search([('company_registry', 'in', orgnummer )]):
            partner.message_post(body=_(f'Company filed for bankrupcy'), message_type='notification')
        
        #TODO save todays date to system parameter
