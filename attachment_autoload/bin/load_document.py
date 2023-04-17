#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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

import sys, getopt, os, subprocess
import erppeek
from openerp.modules import get_module_path

def usage():
    print """-h, --host=\thost
-P, --port=\tport
-d, --database=\tdatabase
-p, --password=\tadmin password
-D, --document=\ddocument to upload

"""

try:
    opts, args = getopt.getopt(sys.argv[1:], "h:P:d:D:m:p:", ["host=", "port=", "database=", "document=", "password="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

output = None
verbose = False
#~ HOST = os.environ.get('HOST', 'localhost')
HOST = os.environ.get('HOST', 'http://localhost')
PORT = os.environ.get('PORT', '8069')
DATABASE = os.environ.get('DATABASE', None)
PASSWD = os.popen('grep admin_passwd /etc/odoo/openerp-server.conf | cut -f 3 -d" "').read().replace('\n', '')
DOCUMENT = None

for o, a in opts:
    if o == "-v":
        verbose = True
    elif o in ("-h", "--host"):
        HOST = a
        #~ usage()
        #~ sys.exit()
    elif o in ("-P", "--port"):
        PORT = a
    elif o in ("-d", "--database"):
        DATABASE = a
    elif o in ("-p", "--password"):
        PASSWD = a
    elif o in ("-D", "--document"):
        DOCUMENT = a
    else:
        assert False, "unhandled option"

client = erppeek.Client(HOST+':'+PORT, DATABASE, 'admin', PASSWD)
client.model('ir.attachment').load_document(DOCUMENT)
#~ os.remove(DOCUMENT)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: