from odoo import models, fields, api, _



class calendarDOTevent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    doc_count = fields.Integer(string='Number of documents attached', readonly=True, store=False) #Source Module dms_calendar_event, Module author Vertel AB


class hrDOTcontract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTdepartment(models.Model):
    _inherit = 'hr.department'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    address_ids = fields.One2many(string='Address', comodel_name='hr.department.address', inverse_name='department_id') #Source Module hr_department_partner, Module author Vertel AB
    department_number = fields.Char(string='Dept Number') #Source Module hr_department_partner, Module author Vertel AB
    first_deputy_manager_id = fields.Many2one(string='Deputy Manager 1', comodel_name='hr.employee') #Source Module rest_kontorsdb, Module author Vertel AB
    internal_region_name = fields.Char(string='Internal Region') #Source Module rest_kontorsdb, Module author Vertel AB
    region_name = fields.Char(string='Region', readonly=True, store=False) #Source Module rest_kontorsdb, Module author Vertel AB
    second_deputy_manager_id = fields.Many2one(string='Deputy Manager 2', comodel_name='hr.employee') #Source Module rest_kontorsdb, Module author Vertel AB


class dmsDOTdirectory(models.Model):
    _inherit = 'dms.directory'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTdocument(models.Model):
    _name = 'rk.document'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Archived') #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='activity_ids.summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='activity_ids.icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='activity_ids.activity_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='activity_ids.user_id', store=False) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='matter_id.classification_id', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
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
    res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ') #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB


class dmsDOTapproval(models.Model):
    _name = 'dms.approval'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module document_signatures, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module document_signatures, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module document_signatures, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='activity_ids.summary', store=False) #Source Module document_signatures, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='activity_ids.icon', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='activity_ids.activity_type_id', store=False) #Source Module document_signatures, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='activity_ids.user_id', store=False) #Source Module document_signatures, Module author Vertel AB
    approve_customer_document = fields.Boolean(string='Approval on Documents') #Source Module document_signatures, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    document_approver_ids = fields.Many2many(string='Document Approver', comodel_name='res.users') #Source Module document_signatures, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module document_signatures, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module document_signatures, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_has_sms_error = fields.Boolean(string='SMS Delivery error', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module document_signatures, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module document_signatures, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module document_signatures, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module document_signatures, Module author Vertel AB


class rkDOTdocumentDOTtype(models.Model):
    _name = 'rk.document.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Active') #Source Module sks_record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
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


class mailDOTthreadDOTcc(models.AbstractModel):
    _inherit = 'mail.thread.cc'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class mailDOTthread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTemployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    department_number = fields.Char(string='Dept Number', related='department_id.department_number', readonly=True) #Source Module hr_department_partner, Module author Vertel AB
    doc_count = fields.Integer(string='Doc count', readonly=True, store=False) #Source Module dms_hr_employee, Module author Vertel AB


class eventDOTevent(models.Model):
    _inherit = 'event.event'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    access_token = fields.Char(string='Security Token') #Source Module event_sks, Module author Vertel AB
    access_url = fields.Char(string='Portal Access URL', readonly=True, store=False) #Source Module event_sks, Module author Vertel AB
    access_warning = fields.Text(string='Access warning', readonly=True, store=False) #Source Module event_sks, Module author Vertel AB
    agresso_status = fields.Boolean(string='Project number sent') #Source Module rest_unit4bw_sks, Module author Vertel AB
    calculation_ids = fields.One2many(string='Calculation', comodel_name='calculation.calculation', inverse_name='kurs', readonly=True) #Source Module calculation, Module author Vertel AB
    calendar_event_id = fields.Many2one(string='Calendar Event', comodel_name='calendar.event', readonly=True) #Source Module event_partner_calendar, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    #datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    department_id = fields.Many2one(string='Department', comodel_name='hr.department') #Source Module event_extend_views, Module author Vertel AB
    doc_count = fields.Integer(string='Doc count', readonly=True, store=False) #Source Module dms_event, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping_event, Module author Vertel AB
    document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping_event, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping_event, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping_event, Module author Vertel AB
    empty_description_html = fields.Html(string='HTML Description') #Source Module event_webpage, Module author Vertel AB
    event_publish_date = fields.Date(string='Publish On') #Source Module event_publish_dates, Module author Vertel AB
    event_un_publish_date = fields.Date(string='Un-Publish On') #Source Module event_publish_dates, Module author Vertel AB
    food_is_served = fields.Boolean(string='Food Is Served') #Source Module event_partner_foodallergy, Module author Vertel AB
    is_final_invoice = fields.Boolean(string='Is Final Invoice', readonly=True, store=False) #Source Module sks_invoice_selection, Module author Vertel AB
    is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping_event, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping_event, Module author Vertel AB
    json_data = fields.Text(string='JSON Data', readonly=True) #Source Module migration_data, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping_event, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping_event, Module author Vertel AB
    migration_data = fields.Text(string='Migration Data', readonly=True) #Source Module migration_data, Module author Vertel AB
    #mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    #partner_id = fields.Many2one(string='Contact', comodel_name='res.partner', related='document_id.partner_id', store=False) #Source Module sks_record_keeping, Module author Vertel AB
    project_id = fields.Many2one(string='Project', comodel_name='project.project') #Source Module event_extend_views, Module author Vertel AB
    project_no = fields.Char(string='Project No', readonly=True) #Source Module event_extend_views, Module author Vertel AB
    #receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping_event, Module author Vertel AB
    #receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping_event, Module author Vertel AB
    #res_id = fields.Integer(string='Resource ID', related='document_id.res_id', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    #res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    res_partner_ids = fields.Many2many(string='Partners', comodel_name='res.partner') #Source Module event_partner, Module author Vertel AB
    #res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping_event, Module author Vertel AB
    #secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping_event, Module author Vertel AB
    #sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping_event, Module author Vertel AB
    state_id = fields.Many2one(string='State', comodel_name='res.country.state', related='address_id.state_id') #Source Module event_website_filters, Module author Vertel AB
    ticket_description = fields.Text(string='Ticket Description', readonly=True, store=False) #Source Module event_webpage, Module author Vertel AB
    use_event_no = fields.Boolean(string='Use Project No') #Source Module event_extend_views, Module author Vertel AB


class eventDOTregistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    certified = fields.Selection(string='Certified', selection=[('True', 'Approved'),('False', 'Unapproved')]) #Source Module event_reservation_certificate, Module author Vertel AB
    food_allergy = fields.Char(string='Födoämnesallergi') #Source Module event_partner_foodallergy, Module author Vertel AB
    food_is_served = fields.Boolean(string='Food Is Served', related='event_id.food_is_served', readonly=True, store=False) #Source Module event_partner_foodallergy, Module author Vertel AB
    hr_department_id = fields.Many2one(string='HR Department', comodel_name='hr.department', related='event_id.department_id', readonly=True, store=False) #Source Module hr_department_sale_order, Module author Vertel AB
    is_decremented_sale = fields.Boolean(string='Is Decremented Sale') #Source Module event_abort, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='event_id.matter_id', readonly=True, store=False) #Source Module event_sks, Module author Vertel AB
    partner_gender = fields.Selection(string='Partner gender', readonly=True, selection=[('male', 'Man'),('female', 'Kvinna'),('other', 'Annan'),('decline', 'Vill ej svara')]) #Source Module event_reservation_gender, Module author Vertel AB
    show_on_customer_portal = fields.Boolean(string='Show on Customer Portal') #Source Module toggle_record_on_portal, Module author Vertel AB
    special_food = fields.Boolean(string='Specialkost', readonly=True, store=False) #Source Module event_partner_foodallergy, Module author Vertel AB


class dmsDOTfile(models.Model):
    _inherit = 'dms.file'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    approval_ids = fields.One2many(string='Approval', comodel_name='dms.approval.line', inverse_name='document_id') #Source Module document_signatures, Module author Vertel AB
    assertion = fields.Binary(string='Assertion', readonly=True) #Source Module document_signatures, Module author Vertel AB
    check_approve_ability = fields.Boolean(string='Check Approve Ability', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    document_fully_approved = fields.Boolean(string='Document Fully Approved', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    document_locked = fields.Boolean(string='Document Locked') #Source Module document_signatures, Module author Vertel AB
    is_approved = fields.Boolean(string='Is Approved', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    page_visibility = fields.Boolean(string='Page Visibility', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    project_id = fields.Many2one(string='Project', comodel_name='project.project') #Source Module document_signatures, Module author Vertel AB
    relay_state = fields.Binary(string='Relay State', readonly=True) #Source Module document_signatures, Module author Vertel AB
    requires_customer_signature = fields.Boolean(string='Requires customer signature') #Source Module document_signatures, Module author Vertel AB
    show_on_customer_portal = fields.Boolean(string='Show on Customer Portal') #Source Module document_signatures, Module author Vertel AB
    signed_by = fields.Many2one(string='Signed by', comodel_name='res.users') #Source Module document_signatures, Module author Vertel AB
    signed_document = fields.Binary(string='Signed Document', readonly=True) #Source Module document_signatures, Module author Vertel AB
    signed_on = fields.Datetime(string='Signed on') #Source Module document_signatures, Module author Vertel AB
    signer_ca = fields.Binary(string='Signer Ca', readonly=True) #Source Module document_signatures, Module author Vertel AB


class hrDOTjob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTlawDOTsection(models.Model):
    _name = 'rk.law.section'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='activity_ids.summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='activity_ids.icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='activity_ids.activity_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='activity_ids.user_id', store=False) #Source Module record_keeping, Module author Vertel AB
    description = fields.Html(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
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


class mailDOTthreadDOTblacklist(models.AbstractModel):
    _inherit = 'mail.thread.blacklist'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTmatter(models.Model):
    _name = 'rk.matter'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Active') #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='activity_ids.summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='activity_ids.icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='activity_ids.activity_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='activity_ids.user_id', store=False) #Source Module record_keeping, Module author Vertel AB
    administrator_id = fields.Many2one(string='Administrator', comodel_name='res.users') #Source Module record_keeping, Module author Vertel AB
    assisting_administrator_ids = fields.Many2many(string='Co-Administrator', comodel_name='res.users') #Source Module sks_record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    close_date = fields.Date(string='Closed', readonly=True) #Source Module record_keeping, Module author Vertel AB
    department_id = fields.Many2one(string='Department', comodel_name='hr.department', related='administrator_id.department_id', readonly=True) #Source Module record_keeping, Module author Vertel AB
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


class mailDOTthreadDOTphone(models.AbstractModel):
    _inherit = 'mail.thread.phone'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


# class projectDOTproject(models.Model):
#     _inherit = 'project.project'

#     @api.model
#     def _selection_target_model_mock(self):
#         return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
#     activity_date_deadline = fields.Date(string='Next Activity Deadline', related='document_id.activity_date_deadline', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', related='document_id.activity_exception_decoration', readonly=True, store=False, selection=[]) #Source Module record_keeping_project, Module author Vertel AB
#     activity_exception_icon = fields.Char(string='Icon', related='document_id.activity_exception_icon', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', related='document_id.activity_ids', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_state = fields.Selection(string='Activity State', related='document_id.activity_state', readonly=True, store=False, selection=[]) #Source Module record_keeping_project, Module author Vertel AB
#     activity_summary = fields.Char(string='Next Activity Summary', related='document_id.activity_summary', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_type_icon = fields.Char(string='Activity Type Icon', related='document_id.activity_type_icon', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='document_id.activity_type_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='document_id.activity_user_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     agresso_status = fields.Boolean(string='Project number sent') #Source Module rest_unit4bw_sks, Module author Vertel AB
#     allow_create_sale = fields.Boolean(string='Allow Create Sale') #Source Module record_keeping_sale_project, Module author Vertel AB
#     analytic_line_ids = fields.One2many(string='Related analytic lines', comodel_name='account.analytic.line', inverse_name='project_id') #Source Module account_analytic_line_project, Module author Vertel AB
#     automatic_matter_connection_task = fields.Boolean(string='Automatic Matter Connection on Tasks') #Source Module record_keeping_project, Module author Vertel AB
#     avtal_from = fields.Date(string='Contract from') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     avtal_from_related = fields.Date(string='Sale order contract from', related='sale_order_id.avtal_from', store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     avtal_tom = fields.Date(string='Contract to') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     avtal_tom_related = fields.Date(string='Sale order contract to', related='sale_order_id.avtal_tom', store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     calculation_ids = fields.One2many(string='Calculation', comodel_name='calculation.calculation', inverse_name='uppdrag', readonly=True) #Source Module calculation, Module author Vertel AB
#     certification_list = fields.Selection(string='Certification', selection=[('1', 'Vet ej'),('2', 'FSC'),('3', 'PEFC'),('4', 'Dubbel certifierade'),('5', 'Nej'),('6', 'Vet ej/Nej')]) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     district = fields.Many2one(string='District', comodel_name='hr.department', related='sale_order_id.hr_department_id', store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping_project, Module author Vertel AB
#     document_ids = fields.One2many(string='Documents', comodel_name='dms.file', inverse_name='project_id') #Source Module document_signatures, Module author Vertel AB
#     document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     event_ids = fields.One2many(string='Event', comodel_name='event.event', inverse_name='project_id') #Source Module event_extend_views, Module author Vertel AB
#     fardigstallandegrad = fields.Float(string='Degree of completion') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     json_data = fields.Text(string='JSON Data', readonly=True) #Source Module migration_data, Module author Vertel AB
#     law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     migration_data = fields.Text(string='Migration Data', readonly=True) #Source Module migration_data, Module author Vertel AB
#     mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     my_activity_date_deadline = fields.Date(string='My Activity Deadline', related='document_id.my_activity_date_deadline', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     offert_giltig = fields.Date(string='Sale order validity') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     offert_giltig_related = fields.Date(string='Sale order validity', related='sale_order_id.validity_date', store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     product_stat_count = fields.Integer(string='Product Statistics', readonly=True, store=False) #Source Module product_statistics, Module author Vertel AB
#     project_no = fields.Char(string='Project Number') #Source Module project_task_id, Module author Vertel AB
#     receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     res_id = fields.Integer(string='Resource ID', related='document_id.res_id', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     sale_order_related_quotation_locked = fields.Boolean(string='Quotation status', related='sale_order_id.quotation_locked', store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     sale_order_related_state = fields.Selection(string='Sale order related state', related='sale_order_id.state', store=False, selection=[]) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     show_on_customer_portal = fields.Boolean(string='Show on Customer Portal') #Source Module toggle_record_on_portal, Module author Vertel AB
#     task_no_next = fields.Integer(string='Next Task id') #Source Module project_task_id, Module author Vertel AB
#     uppdragsnummer_legacy = fields.Char(string='Project number legacy', readonly=True) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     use_default_types = fields.Boolean(string='Use default stages') #Source Module project_task_add_default_stage, Module author Vertel AB
#     use_project_no = fields.Boolean(string='Use Project No') #Source Module project_task_id, Module author Vertel AB


class accountDOTanalyticDOTaccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    doc_count = fields.Integer(string='Doc count', readonly=True, store=False) #Source Module dms_account_analytic_account, Module author Vertel AB


class saleDOTapproval(models.Model):
    _name = 'sale.approval'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    activity_date_deadline = fields.Date(string='Next Activity Deadline', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', readonly=True, store=False, selection=[('warning', 'Alert'),('danger', 'Error')]) #Source Module sale_multi_approval, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', inverse_name='res_id') #Source Module sale_multi_approval, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', readonly=True, store=False, selection=[('overdue', 'Overdue'),('today', 'Today'),('planned', 'Planned')]) #Source Module sale_multi_approval, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='activity_ids.summary', store=False) #Source Module sale_multi_approval, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='activity_ids.icon', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='activity_ids.activity_type_id', store=False) #Source Module sale_multi_approval, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='activity_ids.user_id', store=False) #Source Module sale_multi_approval, Module author Vertel AB
    approve_customer_sale = fields.Boolean(string='Approval on Sale Orders') #Source Module sale_multi_approval, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', inverse_name='res_id') #Source Module sale_multi_approval, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_has_sms_error = fields.Boolean(string='SMS Delivery error', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module sale_multi_approval, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment') #Source Module sale_multi_approval, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module sale_multi_approval, Module author Vertel AB
    threshold = fields.Integer(string='Threshold for double signing') #Source Module sale_multi_approval, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', inverse_name='res_id') #Source Module sale_multi_approval, Module author Vertel AB


# class saleDOTorder(models.Model):
#     _inherit = 'sale.order'

#     @api.model
#     def _selection_target_model_mock(self):
#         return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
#     active = fields.Boolean(string='Archived', related='document_id.active', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     allowed_internal_sale_user_ids = fields.Many2many(string='Allowed Internal Users', comodel_name='res.users') #Source Module sale_portal_access, Module author Vertel AB
#     allowed_portal_sale_user_ids = fields.Many2many(string='Allowed Portal Users', comodel_name='res.users') #Source Module sale_portal_access, Module author Vertel AB
#     allowed_sale_user_ids = fields.Many2many(string='Allowed Sale User', comodel_name='res.users', store=False) #Source Module sale_portal_access, Module author Vertel AB
#     approval_ids = fields.One2many(string='Approval', comodel_name='approval.line', inverse_name='sale_order_id') #Source Module sale_multi_approval, Module author Vertel AB
#     assertion = fields.Binary(string='Assertion', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
#     attendee_names_added = fields.Boolean(string='Attendee Names Added') #Source Module event_invoice_attendees, Module author Vertel AB
#     avtal_from = fields.Date(string='Contract from') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     avtal_tom = fields.Date(string='Contract to') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     check_approve_ability = fields.Boolean(string='Check Approve Ability', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module sale, Module author Odoo S.A.
#     description = fields.Char(string='Description', related='document_id.description', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     doc_count = fields.Integer(string='Doc count', readonly=True, store=False) #Source Module dms_sale_order, Module author Vertel AB
#     document_fully_approved = fields.Boolean(string='Document Fully Approved', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping_sale, Module author Vertel AB
#     document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     error_msg = fields.Char(string=' ', readonly=True, store=False) #Source Module sale_order_sks, Module author Vertel AB
#     event_event_id = fields.Many2one(string='Event', comodel_name='event.event', readonly=True) #Source Module hr_department_sale_order, Module author Vertel AB
#     footer_template_description = fields.Html(string='Website Description footer') #Source Module website_quote_header, Module author Vertel AB
#     has_sign_group = fields.Boolean(string='Has Sign Group', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     header_template_description = fields.Html(string='Website Description header') #Source Module website_quote_header, Module author Vertel AB
#     hr_department_id = fields.Many2one(string='HR Department', comodel_name='hr.department') #Source Module hr_department_sale_order, Module author Vertel AB
#     is_approved = fields.Boolean(string='Is Approved', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     is_final_invoice = fields.Boolean(string='Is Final Invoice') #Source Module sks_invoice_selection, Module author Vertel AB
#     is_not_portal_user = fields.Boolean(string='Is Portal User', readonly=True, store=False) #Source Module sale_order_sks, Module author Vertel AB
#     is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     last_order_line_event_id = fields.Many2one(string='Last Order Event', comodel_name='event.event', readonly=True, store=False) #Source Module rest_unit4bw_sks, Module author Vertel AB
#     latest_pdf_export = fields.Many2one(string='Latest PDF Export', comodel_name='ir.attachment') #Source Module sale_multi_approval, Module author Vertel AB
#     latest_xml_export = fields.Many2one(string='Latest XML Export', comodel_name='ir.attachment') #Source Module sale_export_extend, Module author Vertel AB
#     law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     many_approval_ids = fields.Many2many(string='Approvers', comodel_name='approval.line', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module sale, Module author Odoo S.A.
#     name_description = fields.Char(string='Name Description') #Source Module sale_order_sks, Module author Vertel AB
#     other_analytic_count = fields.Float(string='Timesheet activities ', readonly=True, store=False) #Source Module sale_order_analytic_expense, Module author Vertel AB
#     other_analytic_ids = fields.Many2many(string='Other Timesheet activities associated to this sale', comodel_name='account.analytic.line', readonly=True, store=False) #Source Module sale_order_analytic_expense, Module author Vertel AB
#     page_visibility = fields.Boolean(string='Page Visibility', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
#     privacy_visibility = fields.Selection(string='Visibility', selection=[('followers', 'Invited internal users'),('employees', 'All internal users'),('portal', 'Invited portal users and all internal users')]) #Source Module sale_portal_access, Module author Vertel AB
#     project_manager = fields.Many2one(string='Project Manager', comodel_name='res.users', related='sale_created_project_id.user_id', readonly=True, store=False) #Source Module sale_order_sks, Module author Vertel AB
#     project_task_id = fields.Many2one(string='Project Task', comodel_name='project.task') #Source Module hr_department_sale_order, Module author Vertel AB
#     quotation_locked = fields.Boolean(string='Quotation Locked') #Source Module sale_multi_approval, Module author Vertel AB
#     receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     relay_state = fields.Binary(string='Relay State', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
#     res_id = fields.Integer(string='Resource ID', related='document_id.res_id', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     sale_created_project_id = fields.Many2one(string='Uppdrag', comodel_name='project.project') #Source Module website_quote_contract_project, Module author Vertel AB
#     _SaleOrder__last_update = fields.Datetime(string=' Saleorder  Last Update') #Source Module field_tooltips, Module author Vertel AB
#     secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping_sale, Module author Vertel AB
#     show_on_customer_portal = fields.Boolean(string='Show on Customer Portal') #Source Module toggle_record_on_portal, Module author Vertel AB
#     signed_document = fields.Binary(string='Is Document Signed', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
#     signed_xml_document = fields.Many2one(string='Signed XML Document', comodel_name='ir.attachment', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
#     signer_ca = fields.Binary(string='Signer Ca', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
#     terms_page = fields.Char(string='Terms Page') #Source Module website_quote_header, Module author Vertel AB
#     website_description_footer = fields.Html(string='Website Description Footer') #Source Module website_quote_header, Module author Vertel AB


class crmDOTteam(models.Model):
    _inherit = 'crm.team'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


# class projectDOTtask(models.Model):
#     _inherit = 'project.task'

#     @api.model
#     def _selection_target_model_mock(self):
#         return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
#     allow_create_sale = fields.Boolean(string='Allow Create Sale', readonly=True, store=False) #Source Module record_keeping_sale_project, Module author Vertel AB
#     check_list_history_ids = fields.One2many(string='History', comodel_name='check.history', inverse_name='task_id') #Source Module task_checklist, Module author faOtools
#     check_list_len = fields.Integer(string='Total points', readonly=True) #Source Module task_checklist, Module author faOtools
#     check_list_line_ids = fields.Many2many(string='Check list', comodel_name='check.list') #Source Module task_checklist, Module author faOtools
#     checklist_progress = fields.Float(string='Checklist Progress', readonly=True) #Source Module task_checklist, Module author faOtools
#     classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     district = fields.Many2one(string='District', comodel_name='hr.department') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     doc_count = fields.Integer(string='Number of documents attached', readonly=True, store=False) #Source Module dms_project, Module author Vertel AB
#     document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping_project, Module author Vertel AB
#     document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     is_uppdragsforfragning = fields.Boolean(string='Is Uppdragsforfragning', readonly=True, store=False) #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     is_utbildningsforfragning = fields.Boolean(string='Is Utbildningsforfragning', readonly=True, store=False) #Source Module project_utbildningsforfragningar, Module author Vertel AB
#     json_data = fields.Text(string='JSON Data', readonly=True) #Source Module migration_data, Module author Vertel AB
#     law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     migration_data = fields.Text(string='Migration Data', readonly=True) #Source Module migration_data, Module author Vertel AB
#     mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     related_project_id = fields.Many2one(string='Related project', comodel_name='project.project') #Source Module project_uppdragsforfragningar, Module author Vertel AB
#     related_project_stage_ids = fields.Many2many(string='Tasks Stages', comodel_name='project.task.type', related='project_id.type_ids', readonly=True, store=False) #Source Module remove_project_ids_view, Module author Vertel AB
#     res_id = fields.Integer(string='Resource ID', related='document_id.res_id', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping_project, Module author Vertel AB
#     secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping_project, Module author Vertel AB
#     show_on_customer_portal = fields.Boolean(string='Show on Customer Portal') #Source Module toggle_record_on_portal, Module author Vertel AB
#     task_no = fields.Char(string='Task id') #Source Module project_task_id, Module author Vertel AB
#     use_project_no = fields.Boolean(string='Use Project No') #Source Module project_task_id, Module author Vertel AB


class hr_timesheetDOTsheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class abstractDOTdmsDOTmixin(models.AbstractModel):
    _inherit = 'abstract.dms.mixin'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class dmsDOTapprovalDOTline(models.Model):
    _name = 'dms.approval.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    approval_status = fields.Boolean(string='Status', readonly=True) #Source Module document_signatures, Module author Vertel AB
    approver_id = fields.Many2one(string='Approver', comodel_name='res.users', readonly=True) #Source Module document_signatures, Module author Vertel AB
    assertion = fields.Binary(string='Assertion', readonly=True) #Source Module document_signatures, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='dms.file') #Source Module document_signatures, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module document_signatures, Module author Vertel AB
    relay_state = fields.Binary(string='Relay State', readonly=True) #Source Module document_signatures, Module author Vertel AB
    signed_document = fields.Binary(string='Signed Document', readonly=True) #Source Module document_signatures, Module author Vertel AB
    signed_on = fields.Datetime(string='Signed on') #Source Module document_signatures, Module author Vertel AB
    signer_ca = fields.Binary(string='Signer Ca', readonly=True) #Source Module document_signatures, Module author Vertel AB


class approvalDOTline(models.Model):
    _name = 'approval.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    approval_status = fields.Boolean(string='Status', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    approver_id = fields.Many2one(string='Approver', comodel_name='res.users', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    assertion = fields.Binary(string='Assertion', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    color = fields.Integer(string='Color', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    relay_state = fields.Binary(string='Relay State', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    sale_order_id = fields.Many2one(string='Sale Order', comodel_name='sale.order') #Source Module sale_multi_approval, Module author Vertel AB
    signed_document = fields.Binary(string='Is Document Signed', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    signed_on = fields.Datetime(string='Signed on') #Source Module sale_multi_approval, Module author Vertel AB
    signed_xml_document = fields.Many2one(string='Signed Document', comodel_name='ir.attachment', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB
    signer_ca = fields.Binary(string='Signer Ca', readonly=True) #Source Module sale_multi_approval, Module author Vertel AB


class hrDOTemployeeDOTbase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class restDOTapi(models.Model):
    _name = 'rest.api'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    api_type = fields.Selection(string='Api type', selection=[('generic', 'Generic'),('signport', 'Knowit signport')]) #Source Module rest_base, Module author Vertel AB
    customer_string = fields.Char(string='Customer signature label') #Source Module rest_signport, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module rest_base, Module author Vertel AB
    employee_string = fields.Char(string='Employee signature label') #Source Module rest_signport, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module rest_base, Module author Vertel AB
    idp_entity_id = fields.Char(string='Identity service url') #Source Module rest_signport, Module author Vertel AB
    loa = fields.Char(string='Levels of assurance') #Source Module rest_signport, Module author Vertel AB
    log_count = fields.Integer(string='no. logs', readonly=True, store=False) #Source Module rest_base, Module author Vertel AB
    log_success = fields.Boolean(string='Log successes') #Source Module rest_base, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module rest_base, Module author Vertel AB
    password = fields.Char(string='Password') #Source Module rest_base, Module author Vertel AB
    signature_algorithm = fields.Char(string='Signature algorithm') #Source Module rest_signport, Module author Vertel AB
    sp_entity_id = fields.Char(string='Service provider url') #Source Module rest_signport, Module author Vertel AB
    ssl_certfile = fields.Char(string='Certfile') #Source Module rest_base, Module author Vertel AB
    ssl_keyfile = fields.Char(string='Keyfile') #Source Module rest_base, Module author Vertel AB
    ssl_protocol = fields.Selection(string='SSL Protocol', selection=[('no_verify', 'None'),('simple', 'Simple'),('mutual', 'Mutual')]) #Source Module rest_base, Module author Vertel AB
    url = fields.Char(string='URL') #Source Module rest_base, Module author Vertel AB
    use_basic_auth = fields.Boolean(string='Use Basic Authentication') #Source Module rest_base, Module author Vertel AB
    user = fields.Char(string='User') #Source Module rest_base, Module author Vertel AB


class rkDOTclassification(models.Model):
    _name = 'rk.classification'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    child_ids = fields.One2many(string='Child Structures', comodel_name='rk.classification', inverse_name='parent_id') #Source Module record_keeping, Module author Vertel AB
    classification_name = fields.Char(string='Classification name') #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    has_types = fields.Boolean(string='Has Types') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    parent_id = fields.Many2one(string='Parent Structure', comodel_name='rk.classification') #Source Module record_keeping, Module author Vertel AB
    parent_path = fields.Char(string='Parent Path') #Source Module record_keeping, Module author Vertel AB
    sequence = fields.Integer(string='Sequence') #Source Module record_keeping, Module author Vertel AB
    type_ids = fields.One2many(string='Document Types', comodel_name='rk.document.type', inverse_name='classification_id') #Source Module record_keeping, Module author Vertel AB


class hrDOTpayrollDOTstructureDOTtype(models.Model):
    _inherit = 'hr.payroll.structure.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTcreateDOTinvoice(models.TransientModel):
    _inherit = 'project.create.invoice'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTcreateDOTsaleDOTorder(models.TransientModel):
    _inherit = 'project.create.sale.order'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTcreateDOTsaleDOTorder(models.TransientModel):
    _inherit = 'project.task.create.sale.order'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTcreateDOTsaleDOTorderDOTline(models.TransientModel):
    _inherit = 'project.create.sale.order.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTcreateDOTtimesheet(models.TransientModel):
    _inherit = 'project.task.create.timesheet'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTdepartureDOTwizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class dmsDOTapproverDOTaddDOTwizard(models.TransientModel):
    _name = 'dms.approver.add.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module document_signatures, Module author Vertel AB
    document = fields.Many2one(string='Document', comodel_name='dms.file', readonly=True) #Source Module document_signatures, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module document_signatures, Module author Vertel AB
    user_id = fields.Many2one(string='Approver to add', comodel_name='res.users') #Source Module document_signatures, Module author Vertel AB


class dmsDOTsecurityDOTmixin(models.AbstractModel):
    _inherit = 'dms.security.mixin'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class dmsDOTmixinsDOTthumbnail(models.AbstractModel):
    _inherit = 'dms.mixins.thumbnail'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class dmsDOTcategory(models.Model):
    _inherit = 'dms.category'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTdocumentDOTmixin(models.AbstractModel):
    _name = 'rk.document.mixin'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Archived', related='document_id.active', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', related='document_id.activity_date_deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', related='document_id.activity_exception_decoration', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', related='document_id.activity_exception_icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', related='document_id.activity_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', related='document_id.activity_state', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='document_id.activity_summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='document_id.activity_type_icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='document_id.activity_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='document_id.activity_user_id', store=False) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    #datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    description = fields.Char(string='Description', related='document_id.description', store=False) #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping, Module author Vertel AB
    document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', related='document_id.message_attachment_count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', related='document_id.message_channel_ids', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', related='document_id.message_follower_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', related='document_id.message_has_error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', related='document_id.message_has_error_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', related='document_id.message_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', related='document_id.message_is_follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment', related='document_id.message_main_attachment_id', store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', related='document_id.message_needaction', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', related='document_id.message_needaction_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', related='document_id.message_partner_ids', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', related='document_id.message_unread', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', related='document_id.message_unread_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', related='document_id.my_activity_date_deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', related='document_id.name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Contact', comodel_name='res.partner', related='document_id.partner_id', store=False) #Source Module sks_record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping, Module author Vertel AB
    res_id = fields.Integer(string='Resource ID', related='document_id.res_id', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', related='document_id.website_message_ids', store=False) #Source Module record_keeping, Module author Vertel AB


class dmsDOTtag(models.Model):
    _inherit = 'dms.tag'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class websiteDOTsaleDOTextraDOTfield(models.Model):
    _inherit = 'website.sale.extra.field'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class registrationDOTeditor(models.TransientModel):
    _inherit = 'registration.editor'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class registrationDOTeditorDOTline(models.TransientModel):
    _inherit = 'registration.editor.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTemployeeDOTcategory(models.Model):
    _inherit = 'hr.employee.category'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class event_abortDOTwizard(models.TransientModel):
    _name = 'event_abort.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module event_abort, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module event_abort, Module author Vertel AB


class calendarDOTalarm(models.Model):
    _inherit = 'calendar.alarm'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class calendarDOTalarm_manager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTmail(models.Model):
    _inherit = 'event.mail'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTeventDOTconfigurator(models.TransientModel):
    _inherit = 'event.event.configurator'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class calendarDOTeventDOTtype(models.Model):
    _inherit = 'calendar.event.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class calendarDOTrecurrence(models.Model):
    _inherit = 'calendar.recurrence'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTstage(models.Model):
    _inherit = 'event.stage'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTtag(models.Model):
    _inherit = 'event.tag'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTtagDOTcategory(models.Model):
    _inherit = 'event.tag.category'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


# class eventDOTtype(models.Model):
#     _inherit = 'event.type'

#     @api.model
#     def _selection_target_model_mock(self):
#         return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
#     can_forward = fields.Boolean(string='Can Forward', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     can_publish = fields.Boolean(string='Can Publish', readonly=True, store=False) #Source Module event_type_webpage, Module author Vertel AB
#     can_review = fields.Boolean(string='Can Review', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     department_id = fields.Many2one(string='Department', comodel_name='hr.department') #Source Module event_extend_views, Module author Vertel AB
#     description = fields.Html(string='Description') #Source Module event_webpage, Module author Vertel AB
#     has_comment = fields.Boolean(string='Has Comment', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     is_published = fields.Boolean(string='Is Published') #Source Module event_type_webpage, Module author Vertel AB
#     need_validation = fields.Boolean(string='Need Validation', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     next_review = fields.Char(string='Next Review', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     organizer_id = fields.Many2one(string='Organizer', comodel_name='res.partner') #Source Module event_filtered_dropdowns, Module author Vertel AB
#     rejected = fields.Boolean(string='Rejected', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     rejected_message = fields.Html(string='Rejected Message', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     reviewer_ids = fields.Many2many(string='Reviewers', comodel_name='res.users', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     review_ids = fields.One2many(string='Validations', comodel_name='tier.review', inverse_name='res_id') #Source Module event_type_tier_validation, Module author Vertel AB
#     state = fields.Selection(string='Status', readonly=True, selection=[('draft', 'Event Template Draft'),('reviewed', 'Event Template Reviewed')]) #Source Module event_type_tier_validation, Module author Vertel AB
#     ticket_description = fields.Text(string='Ticket Description', readonly=True, store=False) #Source Module event_webpage, Module author Vertel AB
#     to_validate_message = fields.Html(string='To Validate Message', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     validated = fields.Boolean(string='Validated', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     validated_message = fields.Html(string='Validated Message', readonly=True, store=False) #Source Module event_type_tier_validation, Module author Vertel AB
#     website_id = fields.Many2one(string='Website', comodel_name='website') #Source Module event_type_webpage, Module author Vertel AB
#     website_published = fields.Boolean(string='Visible on current website', store=False) #Source Module event_type_webpage, Module author Vertel AB
#     website_url = fields.Char(string='Website URL', readonly=True, store=False) #Source Module event_type_webpage, Module author Vertel AB


class eventDOTtypeDOTticket(models.Model):
    _inherit = 'event.type.ticket'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTeventDOTticket(models.Model):
    _inherit = 'event.event.ticket'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    seats_available_event_limit = fields.Integer(string='Available Seats Event Limit', readonly=True) #Source Module event_reservation, Module author Vertel AB


class paymentDOTlinkDOTwizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTdepartmentDOTaddress(models.Model):
    _name = 'hr.department.address'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    department_id = fields.Many2one(string='Department', comodel_name='hr.department') #Source Module hr_department_partner, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module hr_department_partner, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module hr_department_partner, Module author Vertel AB
    name = fields.Many2one(string='Address', comodel_name='res.partner') #Source Module hr_department_partner, Module author Vertel AB


class importDOTparticipantsDOTwizard(models.TransientModel):
    _name = 'import.participants.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module event_sks, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module event_sks, Module author Vertel AB
    partner_id = fields.Many2one(string='Booked by', comodel_name='res.partner') #Source Module event_sks, Module author Vertel AB
    registration_list = fields.Binary(string='List of participants to Register') #Source Module event_sks, Module author Vertel AB


class restDOTlog(models.Model):
    _name = 'rest.log'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    data = fields.Text(string='Data') #Source Module rest_base, Module author Vertel AB
    direction = fields.Selection(string='Direction', selection=[('in', 'In'),('out', 'Out')]) #Source Module rest_base, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module rest_base, Module author Vertel AB
    endpoint_url = fields.Char(string='Endpoint') #Source Module rest_base, Module author Vertel AB
    headers = fields.Text(string='Headers') #Source Module rest_base, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module rest_base, Module author Vertel AB
    message = fields.Text(string='Message') #Source Module rest_base, Module author Vertel AB
    method = fields.Char(string='Method') #Source Module rest_base, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module rest_base, Module author Vertel AB
    rest_api_id = fields.Many2one(string='API', comodel_name='rest.api') #Source Module rest_base, Module author Vertel AB
    state = fields.Selection(string='State', selection=[('error', 'Error'),('ok', 'OK')]) #Source Module rest_base, Module author Vertel AB


class eventDOTtypeDOTmail(models.Model):
    _inherit = 'event.type.mail'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTmixin(models.AbstractModel):
    _name = 'rk.mixin'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Archived') #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up') #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received') #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received') #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ') #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ') #Source Module record_keeping, Module author Vertel AB


class hrDOTplan(models.Model):
    _inherit = 'hr.plan'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTplanDOTactivityDOTtype(models.Model):
    _inherit = 'hr.plan.activity.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTplanDOTwizard(models.TransientModel):
    _inherit = 'hr.plan.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class reportDOTsaleDOTreport_saleproforma(models.AbstractModel):
    _inherit = 'report.sale.report_saleproforma'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTdeleteDOTwizard(models.TransientModel):
    _inherit = 'project.delete.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTprofitabilityDOTreport(models.Model):
    _inherit = 'project.profitability.report'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTsaleDOTlineDOTemployeeDOTmap(models.Model):
    _inherit = 'project.sale.line.employee.map'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTtypeDOTdeleteDOTwizard(models.TransientModel):
    _inherit = 'project.task.type.delete.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTstatus(models.Model):
    _inherit = 'project.status'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtags(models.Model):
    _inherit = 'project.tags'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTcopyDOTmap(models.TransientModel):
    _inherit = 'project.task.copy.map'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtype(models.Model):
    _inherit = 'project.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hrDOTemployeeDOTpublic(models.Model):
    _inherit = 'hr.employee.public'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    department_number = fields.Char(string='Dept Number', related='department_id.department_number', readonly=True) #Source Module hr_department_partner, Module author Vertel AB


class saleDOTorderDOTtemplate(models.Model):
    _inherit = 'sale.order.template'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    footer_template_description = fields.Html(string='Website Description footer') #Source Module website_quote_header, Module author Vertel AB
    header_template_description = fields.Html(string='Website Description header') #Source Module website_quote_header, Module author Vertel AB
    terms_page = fields.Char(string='Terms Page') #Source Module website_quote_header, Module author Vertel AB
    website_description_footer = fields.Html(string='Website Description Footer') #Source Module website_quote_header, Module author Vertel AB


class saleDOTorderDOTtemplateDOTline(models.Model):
    _inherit = 'sale.order.template.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTorderDOTtemplateDOToption(models.Model):
    _inherit = 'sale.order.template.option'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class dmsDOTaccessDOTgroup(models.Model):
    _inherit = 'dms.access.group'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class resDOTpartnerDOTregisterDOTevent(models.TransientModel):
    _inherit = 'res.partner.register.event'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class eventDOTmailDOTregistration(models.Model):
    _inherit = 'event.mail.registration'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTorderDOToption(models.Model):
    _inherit = 'sale.order.option'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTpaymentDOTacquirerDOTonboardingDOTwizard(models.TransientModel):
    _inherit = 'sale.payment.acquirer.onboarding.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTadvanceDOTpaymentDOTinv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    is_final_invoice = fields.Selection(string='Is Final Invoice', selection=[('final', 'Yes'),('no', 'No')]) #Source Module sks_invoice_selection, Module author Vertel AB


class saleDOTreport(models.Model):
    _inherit = 'sale.report'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class reportDOTallDOTchannelsDOTsales(models.Model):
    _inherit = 'report.all.channels.sales'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTorderDOTcancel(models.TransientModel):
    _inherit = 'sale.order.cancel'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class saleDOTorderDOTline(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    event_for_unit4_id = fields.Many2one(string='Event For Unit4', comodel_name='event.event') #Source Module rest_unit4bw_sks, Module author Vertel AB
    quotation_locked = fields.Boolean(string='Lock Quotation', related='order_id.quotation_locked', readonly=True, store=False) #Source Module sale_multi_approval, Module author Vertel AB


class rkDOTmail(models.Model):
    _name = 'rk.mail'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    active = fields.Boolean(string='Archived', related='document_id.active', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_date_deadline = fields.Date(string='Next Activity Deadline', related='document_id.activity_date_deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_exception_decoration = fields.Selection(string='Activity Exception Decoration', related='document_id.activity_exception_decoration', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_exception_icon = fields.Char(string='Icon', related='document_id.activity_exception_icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_ids = fields.One2many(string='Activities', comodel_name='mail.activity', related='document_id.activity_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_state = fields.Selection(string='Activity State', related='document_id.activity_state', readonly=True, store=False, selection=[]) #Source Module record_keeping, Module author Vertel AB
    activity_summary = fields.Char(string='Next Activity Summary', related='document_id.activity_summary', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_icon = fields.Char(string='Activity Type Icon', related='document_id.activity_type_icon', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    activity_type_id = fields.Many2one(string='Next Activity Type', comodel_name='mail.activity.type', related='document_id.activity_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    activity_user_id = fields.Many2one(string='Responsible User', comodel_name='res.users', related='document_id.activity_user_id', store=False) #Source Module record_keeping, Module author Vertel AB
    attachment_ids = fields.Many2many(string='Attachment', comodel_name='ir.attachment', readonly=True) #Source Module record_keeping, Module author Vertel AB
    author_id = fields.Many2one(string='Author', comodel_name='res.partner', readonly=True) #Source Module record_keeping, Module author Vertel AB
    auto_delete = fields.Boolean(string='Auto Delete', readonly=True) #Source Module record_keeping, Module author Vertel AB
    body_html = fields.Text(string='Rich-text Contents', readonly=True) #Source Module record_keeping, Module author Vertel AB
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='document_id.classification_id', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    #datas = fields.Binary(string='Datas', related='document_id.datas', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    date = fields.Datetime(string='Date', readonly=True) #Source Module record_keeping, Module author Vertel AB
    description = fields.Char(string='Description', related='document_id.description', store=False) #Source Module record_keeping, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_id = fields.Many2one(string='Document', comodel_name='rk.document') #Source Module record_keeping, Module author Vertel AB
    document_no = fields.Char(string='Document number', related='document_id.document_no', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_ref = fields.Reference(string='Document Reference', selection='_selection_target_model_mock', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type', related='document_id.document_type_id', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_date = fields.Date(string='Drawn up', related='document_id.draw_up_date', store=False) #Source Module record_keeping, Module author Vertel AB
    draw_up_receive_date = fields.Date(string='Drawn up/Received', related='document_id.draw_up_receive_date', store=False) #Source Module record_keeping, Module author Vertel AB
    email_cc = fields.Char(string='Cc', readonly=True) #Source Module record_keeping, Module author Vertel AB
    email_from = fields.Char(string='From', readonly=True) #Source Module record_keeping, Module author Vertel AB
    email_to = fields.Text(string='To', readonly=True) #Source Module record_keeping, Module author Vertel AB
    headers = fields.Text(string='Headers', readonly=True) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document', related='document_id.is_official', store=False) #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker', related='document_id.is_secret', store=False) #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section', related='document_id.law_section_id', store=False) #Source Module record_keeping, Module author Vertel AB
    mail_server_id = fields.Many2one(string='Outgoing mail server', comodel_name='ir.mail_server', readonly=True) #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter', related='document_id.matter_id', store=False) #Source Module record_keeping, Module author Vertel AB
    message_attachment_count = fields.Integer(string='Attachment Count', related='document_id.message_attachment_count', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_channel_ids = fields.Many2many(string='Followers (Channels)', comodel_name='mail.channel', related='document_id.message_channel_ids', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_follower_ids = fields.One2many(string='Followers', comodel_name='mail.followers', related='document_id.message_follower_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error = fields.Boolean(string='Message Delivery error', related='document_id.message_has_error', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_has_error_counter = fields.Integer(string='Number of errors', related='document_id.message_has_error_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_id = fields.Char(string='Message-Id', readonly=True) #Source Module record_keeping, Module author Vertel AB
    message_ids = fields.One2many(string='Messages', comodel_name='mail.message', related='document_id.message_ids', store=False) #Source Module record_keeping, Module author Vertel AB
    message_is_follower = fields.Boolean(string='Is Follower', related='document_id.message_is_follower', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_main_attachment_id = fields.Many2one(string='Main Attachment', comodel_name='ir.attachment', related='document_id.message_main_attachment_id', store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction = fields.Boolean(string='Action Needed', related='document_id.message_needaction', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_needaction_counter = fields.Integer(string='Number of Actions', related='document_id.message_needaction_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_partner_ids = fields.Many2many(string='Followers (Partners)', comodel_name='res.partner', related='document_id.message_partner_ids', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_type = fields.Selection(string='Type', readonly=True, selection=[('email', 'Email'),('comment', 'Comment'),('notification', 'System notification'),('user_notification', 'User Specific Notification')]) #Source Module record_keeping, Module author Vertel AB
    message_unread = fields.Boolean(string='Unread Messages', related='document_id.message_unread', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    message_unread_counter = fields.Integer(string='Unread Messages Counter', related='document_id.message_unread_counter', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    mimetype = fields.Char(string='Mimetype', related='document_id.mimetype', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    model = fields.Char(string='Related Document Model', readonly=True) #Source Module record_keeping, Module author Vertel AB
    my_activity_date_deadline = fields.Date(string='My Activity Deadline', related='document_id.my_activity_date_deadline', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    name = fields.Char(string='Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    notification = fields.Boolean(string='Is Notification', readonly=True) #Source Module record_keeping, Module author Vertel AB
    partner_id = fields.Many2one(string='Contact', comodel_name='res.partner', related='document_id.partner_id', store=False) #Source Module sks_record_keeping, Module author Vertel AB
    receive_date = fields.Date(string='Received', related='document_id.receive_date', store=False) #Source Module record_keeping, Module author Vertel AB
    receiver = fields.Char(string='Receiver ', related='document_id.receiver', store=False) #Source Module record_keeping, Module author Vertel AB
    recipient_ids = fields.Many2many(string='To (Partners)', comodel_name='res.partner', readonly=True) #Source Module record_keeping, Module author Vertel AB
    record_name = fields.Char(string='Message Record Name', readonly=True) #Source Module record_keeping, Module author Vertel AB
    references = fields.Text(string='References', readonly=True) #Source Module record_keeping, Module author Vertel AB
    reply_to = fields.Char(string='Reply-To', readonly=True) #Source Module record_keeping, Module author Vertel AB
    res_id = fields.Many2oneReference(string='Related Document ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    res_model = fields.Char(string='Resource Model', related='document_id.res_model', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    res_ref = fields.Reference(string='Resource Reference', selection='_selection_target_model_mock', related='document_id.res_ref', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    scheduled_date = fields.Char(string='Scheduled Send Date', readonly=True) #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds', related='document_id.secrecy_grounds', store=False) #Source Module record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender ', related='document_id.sender', store=False) #Source Module record_keeping, Module author Vertel AB
    subject = fields.Char(string='Subject', readonly=True) #Source Module record_keeping, Module author Vertel AB
    website_message_ids = fields.One2many(string='Website Messages', comodel_name='mail.message', related='document_id.website_message_ids', store=False) #Source Module record_keeping, Module author Vertel AB


class dmsDOTstorage(models.Model):
    _inherit = 'dms.storage'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTrecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class reportDOTprojectDOTtaskDOTuser(models.Model):
    _inherit = 'report.project.task.user'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class projectDOTtaskDOTtype(models.Model):
    _inherit = 'project.task.type'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    default_check_list_ids = fields.One2many(string='Check List', comodel_name='check.list', inverse_name='project_task_type_id') #Source Module task_checklist, Module author faOtools
    is_default = fields.Boolean(string='Default stage') #Source Module project_task_add_default_stage, Module author Vertel AB
    no_need_for_checklist = fields.Boolean(string='No need for checklist') #Source Module task_checklist, Module author faOtools


class hr_timesheetDOTsheetDOTline(models.TransientModel):
    _inherit = 'hr_timesheet.sheet.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hr_timesheetDOTsheetDOTlineDOTabstract(models.AbstractModel):
    _inherit = 'hr_timesheet.sheet.line.abstract'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class hr_timesheetDOTsheetDOTnewDOTanalyticDOTline(models.TransientModel):
    _inherit = 'hr_timesheet.sheet.new.analytic.line'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class websiteDOTeventDOTmenu(models.Model):
    _inherit = 'website.event.menu'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class websiteDOTsaleDOTpaymentDOTacquirerDOTonboardingDOTwizard(models.TransientModel):
    _inherit = 'website.sale.payment.acquirer.onboarding.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        


class rkDOTaddDOTfileDOTwizard(models.TransientModel):
    _name = 'rk.add.file.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    classification_id = fields.Many2one(string='Classification', comodel_name='rk.classification', related='rk_matter_id.classification_id', readonly=True, store=False) #Source Module sks_record_keeping, Module author Vertel AB
    datas = fields.Binary(string='File Content') #Source Module record_keeping_attachment, Module author Vertel AB
    datas_name = fields.Char(string='Matter Name') #Source Module record_keeping_attachment, Module author Vertel AB
    description = fields.Text(string='Description') #Source Module record_keeping_attachment, Module author Vertel AB
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping_attachment, Module author Vertel AB
    document_type_id = fields.Many2one(string='Document Type', comodel_name='rk.document.type') #Source Module sks_record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping_attachment, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module sks_record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy Provision', comodel_name='rk.law.section') #Source Module sks_record_keeping, Module author Vertel AB
    name = fields.Char(string='Name') #Source Module record_keeping_attachment, Module author Vertel AB
    recipient = fields.Char(string='Recipient') #Source Module sks_record_keeping, Module author Vertel AB
    rk_matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping_attachment, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy Grounds') #Source Module sks_record_keeping, Module author Vertel AB
    sender = fields.Char(string='Sender') #Source Module sks_record_keeping, Module author Vertel AB


class rkDOTwizard(models.TransientModel):
    _name = 'rk.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping_wizard, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping_wizard, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping_wizard, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping_wizard, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping_wizard, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping_wizard, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping_wizard, Module author Vertel AB


class rkDOTaddDOTrecordDOTwizard(models.TransientModel):
    _name = 'rk.add.record.wizard'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        
    display_name = fields.Char(string='Display Name', readonly=True, store=False) #Source Module record_keeping, Module author Vertel AB
    id = fields.Integer(string='ID', readonly=True) #Source Module record_keeping, Module author Vertel AB
    is_official = fields.Boolean(string='Official document') #Source Module record_keeping, Module author Vertel AB
    is_secret = fields.Boolean(string='Secrecy marker') #Source Module record_keeping, Module author Vertel AB
    law_section_id = fields.Many2one(string='Secrecy provision', comodel_name='rk.law.section') #Source Module record_keeping, Module author Vertel AB
    matter_id = fields.Many2one(string='Matter', comodel_name='rk.matter') #Source Module record_keeping, Module author Vertel AB
    secrecy_grounds = fields.Char(string='Secrecy grounds') #Source Module record_keeping, Module author Vertel AB

