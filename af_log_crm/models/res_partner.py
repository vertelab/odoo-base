#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import models, api
from odoo.addons.af_log.models.af_log import recursive_default

class Partner(models.Model):
    _inherit = ['res.partner', 'af.log.audit']
    _name = 'res.partner'

    @api.model
    def _af_audit_log_details(self, operation, **kwargs):
        """ Must be implemented by inheriting models. Perform
        filtering of objects. Specify what type of log object it is,
        and any special log requirements. Convert internal values to
        human readable (HR) values.
        :returns: A list of log object descriptions.
        [{
            'obj_type': Arbetsförmedlingen HR internal name, e.g.
                        Arbetssökande, Arbetsgivare.
            'obj_id':   Arbetsförmedlingen HR object id, e.g. a
                        person or org number.
            'id_type':  The type of the id, e.g. Organisationsnummer or
            'id_type':  The type of the id, e.g. Organisationsnummer or
                        Personnummer.
            'values':   {HR field name: HR field value},
            'defaults': Optional. dict with default values. Use to
                        implement special cases. Will be used to update
                        the audit records default values.
            'update':   Optional. dict with update values. Use to
                        implement special cases. Will be used to
                        overwrite the audit records values.
        }...]
        """
        log = super(Partner, self)._af_audit_log_details(operation, **kwargs)
        if operation == 'CREATE':
            # values: create vals
            # result: create result ( so... True?)
            values = kwargs.get('values', {})
            if values.get('is_jobseeker'):
                log.append({
                    'obj_type': 'Arbetssökande',
                    'obj_id': values.get('social_sec_nr'),
                    'id_type': 'Personnummer',
                    'values': self._af_log_human_readable_vals(values),
                })
        elif operation == 'READ':
            # ids: record ids
            # result: read values
            ids = kwargs.get('ids')
            result = kwargs.get('result')
            browse = False
            for p in result:
                if 'is_jobseeker' not in p:
                    browse = True
                    break
                else:
                    if p['is_jobseeker']:
                        if 'social_sec_nr' not in p:
                            browse = True
                            break
                        log.append({
                            'obj_type': 'Arbetssökande',
                            'obj_id': p['social_sec_nr'],
                            'id_type': 'Personnummer',
                            'values': self._af_log_human_readable_vals(p),
                        })
            if browse:
                # Not enough data in read
                for p in self.sudo().browse(ids):
                    if p.is_jobseeker:
                        log.append({
                            'obj_type': 'Arbetssökande',
                            'obj_id': p.social_sec_nr,
                            'id_type': 'Personnummer',
                            'values': self._af_log_human_readable_vals(p),
                        })
        elif operation == 'UPDATE':
            # ids: record ids
            # values: write values
            # data: read from before update (_af_pre_func_audit_log)
            # result: write result (useless?)
            values = kwargs.get('values', {})
            data = kwargs.get('data', {})
            browse = False
            if len(data) > 0:
                if 'is_jobseeker' not in data[0] or 'social_sec_nr' not in data[0]:
                    # Add missing fields to data
                    extra = self.search_read([('id', 'in', [x['id'] for x in data])], ['is_jobseeker', 'social_sec_nr'])
                    for d in data:
                        du = filter(
                            lambda p: p['id'] == d['id'],
                            extra).__next__()[0]
                        recursive_default(d, du)
            for dData in data:
                if dData['is_jobseeker']:
                    social = dData['social_sec_nr']
                    dVals = filter(
                        lambda p: p['id'] == dData['id'],
                        values).__next__()[0]
                    dVals = self._af_log_human_readable_vals(dVals)
                    dData = self._af_log_human_readable_vals(dData)
                    for key, val in dVals.items():
                        dVals[key] = f"{dData[key]} => {dVals[key]}"
                    log.append({
                        'obj_type': 'Arbetssökande',
                        'obj_id': social,
                        'id_type': 'Personnummer',
                        'values': dVals,
                    })
        elif operation == 'DELETE':
            # ids: record ids
            # values: read from before unlink (_af_pre_func_audit_log)
            values = kwargs.get('values', {})
            for p in values:
                if p['is_jobseeker']:
                    log.append({
                        'obj_type': 'Arbetssökande',
                        'obj_id': p['social_sec_nr'],
                        'id_type': 'Personnummer'
                    })
        elif operation == 'SEARCH':
            # result: search_read result
            # search_terms: search domain
            # TODO: Its currently not possible to recognise 0 hits
            #       searches. Try to determine from domain if this is a
            #       jobseeker search.
            search_terms = kwargs.get('search_terms')
            result = kwargs.get('result')['records']
            browse = False
            count = 0
            count_js = 0
            for p in result:
                if 'is_jobseeker' not in p:
                    browse = True
                    break
                else:
                    if p['is_jobseeker']:
                        if 'social_sec_nr' not in p:
                            browse = True
                            break
                        count_js += 1
                count += 1
            if browse:
                count = 0
                count_js = 0
                # Not enough data in read
                # TODO: Replace this fallback with adding relevant
                #       attributes to every search. Remember which and
                #       remove them before returning result in main.py.
                #       Do the same for all other functions.
                for p in self.sudo().browse([p['id'] for p in result]):
                    if p.is_jobseeker:
                        count_js += 1
                    count += 1
            if count_js:
                log.append({
                    'obj_type': 'Arbetssökande',
                    'obj_id': p['social_sec_nr'],
                    'id_type': 'Personnummer',
                    'values': {
                        '#hits': count_js,
                        'search_terms': self._af_log_domain2search_terms(search_terms),
                    },
                })
        return log
