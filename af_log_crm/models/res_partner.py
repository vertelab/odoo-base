#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import models, api
from odoo.addons.af_log.models.af_log import recursive_default


def identify_job_seeker(env, values):
    return values.get('is_jobseeker', False)


class Partner(models.Model):
    _inherit = ['res.partner', 'af.log.audit']
    _name = 'res.partner'

    @api.model
    def _af_audit_log_setup(self):
        return {
            'audit_types': {
                'jobseeker': {
                    'type': 'Arbetssökande',
                    'id_type': 'Personnummer',
                    'id': 'social_sec_nr',
                    'required_fields': ['is_jobseeker', 'social_sec_nr'],
                    'filter': identify_job_seeker,
                    'priority': 1,
                }
            }
        }
