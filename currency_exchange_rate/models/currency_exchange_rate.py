from lxml import etree
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_update_interval = field.Selection(['manually', 'Manually',
                                                'daily', 'Daily',
                                                'weekly', 'Weekly',
                                                'monthly', 'Monthly'],
                                               default='manually',
                                               string='Update Interval')
    currency_last_sync = fields.Date(string= 'Last currency sync',
                                     readonly=True)

    def update_currency_rates(self):
        res = self.get_currency_data()
        if res:
            currency_rates, time = res
        else:
            return
            
        currencies = self.env['res.currency'].search([])
        Rate = self.env['res.currency.rate']
        Currency = self.env['res.currency']
        for company in self:
            main_currency_rate = currency_data.get(company.curency_id.name)
            if not main_currency_rate:
                raise UserError("Your Company's main currency is not"
                                " supported")
            for currency in currencies:
                rate = currency_rates.get(currency)/main_currency_rate
                currency_id = Currency.search(['name', '=', currency]).id
                cr = Rate.search([('currency_id', '=', currency_id),
                                  ('name', '=', date_rate),
                                  ('company_id', '=', company.id)])
                if cr:
                    cr.rate = rate
                else:
                    Rate.create({'currency_id': currency_id,
                                 'rate': rate,
                                 'name': time,
                                 'company_id': company.id})
        self.currency_last_sync = fields.Date.today()
        return True

    
    def get_currency_data(self):
        url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            response = requests.request('GET', url)
        except Exception as e:
            return False
        if not response.status_code in (200, 201):
            return False
        xml = etree.fromstring(response.content)

        time = xml[2][0].get('time')
        res = {child.get('currency'): child.get('rate')
               for child in xml[2][0]}

        # Euro is reference currency.
        res['EUR'] = 1.0
        return (res, time)

    def automatic_currency_update:
        interval = {'daily': 1,
                    'weekly': 7,
                    'monthly': 30,}
        wanted = interval[self.currency_update_interval]
        last_update = datetime.datetime.now() - self.currency_last_sync
        if last_update >= datetime.timedelta(days=wanted):
            self.update_currency_rates()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_last_sync_date = fields.Date(related='company_id.currency_last_sync')
    currency_update_interval = fields.Selection(related='company_id.currency_update_interval')

    def manual_currency_update(self):
        self.ensure_one()
        if not self.company_id.update_currency_rates():
            raise UserError(_('Unable to update currency rates'))

