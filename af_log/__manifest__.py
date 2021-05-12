#  Copyright (c) 2021 Arbetsförmedlingen.

{
    'name': 'AF Logging',
    'version': '12.0.0.1.0',
    'summary': 'Log formatting and audit logging for Arbetsförmedlingen.',
    'description': '''Installation
============
This module requires some hacking in odoo-bin to work its magic.

af_log_monkeypatch.py
---------------------
Provides log format in accordance with Arbetsförmedlingens Elastic
Common Schema. Must be injected before running odoo. Put it next to
odoo-bin and import it in odoo-bin, right after import odoo.

The contents of odoo-bin should look something like (mind the missing
whitespace):


| #!/usr/bin/env python3
| 
| # set server timezone in UTC before time module imported\n
| __import__('os').environ['TZ'] = 'UTC'\n
| import odoo\n
| # AF LOG MONKEYPATCH\n
| import af_log_monkeypatch\n
| 
| if __name__ == "__main__"\:\n
|     odoo.cli.main()\n
| 
    ''',
    'category': 'Technical Settings',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'Other proprietary',
    'depends': ['web'],
    'data': [],
    'demo': [],
    'installable': True,
    'auto_install': False
}
