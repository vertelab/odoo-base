# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Base: Employee Status Update',
    'version': '14.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Effortlessly manage employment status with our Employee-Contact integration.',
    'category': 'Technical',
    #'sequence': '1'
    'author': 'Vertel AB',
    'website': "https://vertel.se/apps/odoo-base/employee_status_update",
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base',
    'description': """
    
      * Overview:
      
        This module will show the Employee status inside the Contacts Form.
        When creating an Employee via the Users Form the Contacts Employee status will automatically be set.
        The status will automatically be changed when an Employee is being archived/unarchived.
        It will also provide the ability to update the Contacts Employee status in retrospective.
      
      
      * Features:
      
        - Contacts
        
          Shows the Employee boolean field inside a Contact view-form.
        
        
        - Create an Employee via Users Form
        
          This will automatically set the Employee boolean to True inside the Contact Form when creating an Employee via Users view-form.    
        
          1.  Settings / Manage Users / Create User
          2.  When a User has been created, click "Create Employee" button inside the view-form.
        
        
        - Update Employee status inside Contacts in retrospective
        
          This will only work provided that the Employee was created via Settings / Manage Users / Create Employee button inside the User view-form.
        
          1.  Go to Setting / Manage Users
          2.  Check all Users you want to be affected, in the list-view.
          3.  Go to Action and press "Update Employee Status".
          4.  The selected Users Contacts that are Employees are now updated
        
        
        - Archived Employees
        
          When an Employee is being archived/unarchived inside the Employee Form the Contacts Employee status will automatically be changed.      
          This will only work provided that the Employee was created via Settings / Manage Users / Create Employee button inside the User view-form.
            
    
    """,
    'depends': ['base','hr','contacts'],
    'data': [
        'data/data.xml',
        'views/res_partner_view.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
