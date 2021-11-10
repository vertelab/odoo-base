# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2020 Vertel AB (<http://vertel.se>).
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

# noinspection PyStatementEffect
{
    'name': 'Web Extra Options',
    'version': '12.0.1.0.0',
    'category': '',
    'description': """Adds extra features to web.

=== Date and Datetime formating ===
Adds formatting options to date and datetime widgets through the datepicker option.

Specify a format through the format option. Remember that this destroys language based formatting.
Example: options="{'datepicker': {'format': 'YYYY-MM-DD HH:mm'}}"

You can also hide specific parts of the datetime (only seconds so far). NOT IMPLEMENTED FOR EDIT MODE!
Example: options="{'datepicker': {'hide': {'seconds': True}}}"

Date formatting string is from moment.js, not python.
                                Token                     Output
Month                           M                         1 2 ... 11 12
                                Mo                        1st 2nd ... 11th 12th
                                MM                        01 02 ... 11 12
                                MMM                       Jan Feb ... Nov Dec
                                MMMM                      January February ... November December
Quarter                         Q                         1 2 3 4
                                Qo                        1st 2nd 3rd 4th
Day of Month                    D                         1 2 ... 30 31
                                Do                        1st 2nd ... 30th 31st
                                DD                        01 02 ... 30 31
Day of Year                     DDD                       1 2 ... 364 365
                                DDDo                      1st 2nd ... 364th 365th
                                DDDD                      001 002 ... 364 365
Day of Week                     d                         0 1 ... 5 6
                                do                        0th 1st ... 5th 6th
                                dd                        Su Mo ... Fr Sa
                                ddd                       Sun Mon ... Fri Sat
                                dddd                      Sunday Monday ... Friday Saturday
Day of Week (Locale)            e                         0 1 ... 5 6
Day of Week (ISO)               E                         1 2 ... 6 7
Week of Year                    w                         1 2 ... 52 53
                                wo                        1st 2nd ... 52nd 53rd
                                ww                        01 02 ... 52 53
Week of Year (ISO)              W                         1 2 ... 52 53
                                Wo                        1st 2nd ... 52nd 53rd
                                WW                        01 02 ... 52 53
Year                            YY                        70 71 ... 29 30
                                YYYY                      1970 1971 ... 2029 2030
                                YYYYYY                    -001970 -001971 ... +001907 +001971
                                                          Note: Expanded Years (Covering the full time value range of approximately 273,790 years forward or backward from 01 January, 1970)
                                Y                         1970 1971 ... 9999 +10000 +10001
                                                          Note: This complies with the ISO 8601 standard for dates past the year 9999
Era Year                        y                         1 2 ... 2020 ...
Era                             N                         BC AD
                                                          Note: Abbr era name
                                NN                        BC AD
                                                          Note: Narrow era name
                                NNN                       Before Christ, Anno Domini
                                                          Note: Full era name
Week Year                       gg                        70 71 ... 29 30
                                gggg                      1970 1971 ... 2029 2030
Week Year (ISO)                 GG                        70 71 ... 29 30
                                GGGG                      1970 1971 ... 2029 2030
AM/PM                           A                         AM PM
                                a                         am pm
Hour                            H                         0 1 ... 22 23
                                HH                        00 01 ... 22 23
                                h                         1 2 ... 11 12
                                hh                        01 02 ... 11 12
                                k                         1 2 ... 23 24
                                kk                        01 02 ... 23 24
Minute                          m                         0 1 ... 58 59
                                mm                        00 01 ... 58 59
Second                          s                         0 1 ... 58 59
                                ss                        00 01 ... 58 59
Fractional Second               S                         0 1 ... 8 9
                                SS                        00 01 ... 98 99
                                SSS                       000 001 ... 998 999
                                SSSS ... SSSSSSSSS        000[0..] 001[0..] ... 998[0..] 999[0..]
Time Zone                       z or zz                   EST CST ... MST PST
                                                          Note: as of 1.6.0, the z/zz format tokens have been deprecated from plain moment objects. Read more about it here. However, they *do* work if you are using a specific time zone with the moment-timezone addon.
                                Z                         -07:00 -06:00 ... +06:00 +07:00
                                ZZ                        -0700 -0600 ... +0600 +0700
Unix Timestamp                  X                         1360013296
Unix Millisecond Timestamp      x                         1360013296123


=== SUDO rights for Search_Count ===
Extends search_count with the ability to search with Sudo rights if user belongs to the right groups.
Extend the model that is to use it with a customised search function, an example can be found in mass_mailing_count.
In the view extend search_count widget with option={method:customized_function}.
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['web',],
    'data': [
			'views/assets.xml',
        ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
