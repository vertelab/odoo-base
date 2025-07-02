from odoo import models, fields, api, _



class rkDOTdocument(models.Model):
    _name = 'rk.document'

    active = fields.Boolean(string='Archived') #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', store=False) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    datas = fields.Binary(string='Datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_no = fields.Char(string='Document number', readonly=True) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up') #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    mimetype = fields.Char(string='Mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Contact', comodel_name='res.partner') #Source Module sks_record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received') #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ') #Source Module record_keeping, Module author Vertel AB
    res_id = fields.Integer(string='Resource ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    res_model = fields.Char(string='Resource Model', readonly=True) #Source Module record_keeping, Module author Vertel AB
    #res_ref = fields.Reference(string='Resource Reference', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ') #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTdocumentDOTtype(models.Model):
    _name = 'rk.document.type'

    active = fields.Boolean(string='Active') #Source Module sks_record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module sks_record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_has_sms_error = fields.Boolean(string='SMS Delivery error', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module sks_record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module sks_record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module sks_record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTlawDOTsection(models.Model):
    _name = 'rk.law.section'

    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', store=False) #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Html(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module record_keeping, Module author Vertel AB
    url = fields.Char(string='Url') #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTmatter(models.Model):
    _name = 'rk.matter'

    active = fields.Boolean(string='Active') #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', store=False) #Source Module record_keeping, Module author Vertel AB
    administrator_id = fields.Many2one(string='Administrator', comodel_name='res.users') #Source Module record_keeping, Module author Vertel AB
    assisting_administrator_ids = fields.Many2many(string='Co-Administrator', comodel_name='res.users') #Source Module sks_record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    close_date = fields.Date(string='Closed', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    department_id = fields.Many2one(string='Department', comodel_name='hr.department', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_count = fields.Integer(string='Number of documents in this matter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_ids = fields.One2many(string='Documents', comodel_name='rk.document', inverse_name='matter_id') #Source Module record_keeping, Module author Vertel AB
    document_no_next = fields.Integer(string='The next document number', readonly=True) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up') #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    latest_change = fields.Char(string='Latest change', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    legacy_reg_no = fields.Char(string='Legacy registration number') #Source Module record_keeping, Module author Vertel AB
    matter_name = fields.Char(string='Matter Name') #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Matter Number', readonly=True) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner') #Source Module record_keeping, Module author Vertel AB
    partner_name = fields.Char(string='Partner Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received') #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ') #Source Module record_keeping, Module author Vertel AB
    reg_no = fields.Char(string='Registration number', readonly=True) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ') #Source Module record_keeping, Module author Vertel AB
    sorting_out_date = fields.Date(string='Sorting Out Date') #Source Module record_keeping, Module author Vertel AB
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'),('pending', 'Pending'),('done', 'Done'),('cancel', 'Cancelled')]) #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTclassification(models.Model):
    _name = 'rk.classification'

    child_ids = fields.One2many(string='Child Structures', comodel_name='rk.classification', inverse_name='parent_id') #Source Module record_keeping, Module author Vertel AB
    classification_name = fields.Char(string='Classification name') #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    has_types = fields.Boolean(string='Has Types') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    parent_id = fields.Many2one(string='Parent Structure', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    parent_path = fields.Char(string='Parent Path') #Source Module record_keeping, Module author Vertel AB
    sequence = fields.Integer(string='Sequence') #Source Module record_keeping, Module author Vertel AB
    type_ids = fields.One2many(string='Document Types', comodel_name='rk.document.type', inverse_name='classification_id') #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTdocumentDOTmixin(models.Model):
    _name = 'rk.document.mixin'

    active = fields.Boolean(string='Archived', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', store=False) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    datas = fields.Binary(string='Datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    description = fields.Char(string='Description', store=False) #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping, Module author Vertel AB
    document_no = fields.Char(string='Document number', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_ref = fields.Reference(string='Document Reference', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received', store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document', store=False) #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker', store=False) #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', store=False) #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment', store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    mimetype = fields.Char(string='Mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Contact', comodel_name='res.partner', store=False) #Source Module sks_record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received', store=False) #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ', store=False) #Source Module record_keeping, Module author Vertel AB
    res_id = fields.Integer(string='Resource ID', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_model = fields.Char(string='Resource Model', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_ref = fields.Reference(string='Resource Reference', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds', store=False) #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ', store=False) #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB


class rkDOTmixin(models.Model):
    _name = 'rk.mixin'

    active = fields.Boolean(string='Archived') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up') #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received') #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ') #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ') #Source Module record_keeping, Module author Vertel AB


class rkDOTmail(models.Model):
    _name = 'rk.mail'

    active = fields.Boolean(string='Archived', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', store=False) #Source Module record_keeping, Module author Vertel AB
    attachment_ids = fields.Many2many(string='Attachment', comodel_name='ir.attachment', readonly=True) #Source Module record_keeping, Module author Vertel AB
    author_id = fields.Many2one(string='Author', comodel_name='res.partner', readonly=True) #Source Module record_keeping, Module author Vertel AB
    auto_delete = fields.Boolean(string='Auto Delete', readonly=True) #Source Module record_keeping, Module author Vertel AB
    body_html = fields.Text(string='Rich-text Contents', readonly=True) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    datas = fields.Binary(string='Datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    date = fields.Datetime(string='Date', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description', store=False) #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping, Module author Vertel AB
    document_no = fields.Char(string='Document number', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_ref = fields.Reference(string='Document Reference', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received', store=False) #Source Module record_keeping, Module author Vertel AB
    email_cc = fields.Char(string='Cc', readonly=True) #Source Module record_keeping, Module author Vertel AB
    email_from = fields.Char(string='From', readonly=True) #Source Module record_keeping, Module author Vertel AB
    email_to = fields.Text(string='To', readonly=True) #Source Module record_keeping, Module author Vertel AB
    headers = fields.Text(string='Headers', readonly=True) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document', store=False) #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker', store=False) #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', store=False) #Source Module record_keeping, Module author Vertel AB
    mail_server_id = fields.Many2one(string='Outgoing mail server', comodel_name='ir.mail_server', readonly=True) #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_id = fields.Char(string='Message-Id', readonly=True) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment', store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_type = fields.Selection(string='Type', readonly=True, selection=[('email', 'Email'),('comment', 'Comment'),('notification', 'System notification'),('user_notification', 'User Specific Notification')]) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    mimetype = fields.Char(string='Mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    model = fields.Char(string='Related Document Model', readonly=True) #Source Module record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    notification = fields.Boolean(string='Is Notification', readonly=True) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Contact', comodel_name='res.partner', store=False) #Source Module sks_record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received', store=False) #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ', store=False) #Source Module record_keeping, Module author Vertel AB
    recipient_ids = fields.Many2many(string='To (Partners)', comodel_name='res.partner', readonly=True) #Source Module record_keeping, Module author Vertel AB
    record_name = fields.Char(string='Message Record Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    references = fields.Text(string='References', readonly=True) #Source Module record_keeping, Module author Vertel AB
    reply_to = fields.Char(string='Reply-To', readonly=True) #Source Module record_keeping, Module author Vertel AB
    res_id = fields.Reference(string='Related Document ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    res_model = fields.Char(string='Resource Model', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_ref = fields.Reference(string='Resource Reference', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    scheduled_date = fields.Char(string='Scheduled Send Date', readonly=True) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds', store=False) #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ', store=False) #Source Module record_keeping, Module author Vertel AB
    subject = fields.Char(string='Subject', readonly=True) #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='False', store=False) #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB


class rkDOTaddDOTfileDOTwizard(models.TransientModel):
    _name = 'rk.add.file.wizard'

    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB
    datas = fields.Binary(string='File Content') #Source Module record_keeping_attachment, Module author Vertel AB
    datas_name = fields.Char(string='Matter Name') #Source Module record_keeping_attachment, Module author Vertel AB
    description = fields.Text(string='Description') #Source Module record_keeping_attachment, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping_attachment, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module sks_record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module sks_record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping_attachment, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy Provision', comodel_name='rk.law.section') #Source Module sks_record_keeping, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module record_keeping_attachment, Module author Vertel AB
    recipient = fields.Char(string='Recipient') #Source Module sks_record_keeping, Module author Vertel AB
    rk_matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping_attachment, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy Grounds') #Source Module sks_record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender') #Source Module sks_record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB


class rkDOTwizard(models.TransientModel):
    _name = 'rk.wizard'

    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping_wizard, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping_wizard, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping_wizard, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping_wizard, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping_wizard, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping_wizard, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping_wizard, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB


class rkDOTaddDOTrecordDOTwizard(models.TransientModel):
    _name = 'rk.add.record.wizard'

    create_date = fields.Datetime(string='Created on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    create_uid = fields.Many2one(string='Created by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    __last_update = fields.Datetime(string='Last Modified on', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    write_date = fields.Datetime(string='Last Updated on', readonly=True) #Source Module record_keeping, Module author Vertel AB
    write_uid = fields.Many2one(string='Last Updated by', comodel_name='res.users', readonly=True) #Source Module record_keeping, Module author Vertel AB

