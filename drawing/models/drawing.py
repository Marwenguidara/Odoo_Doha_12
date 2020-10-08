# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID
from datetime import datetime
import logging

""" Drawing Sheet """
class ConstructionDrawing (models.Model):
    _name = 'construction.drawing'
    _description = 'Items Records for Projects'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    partner_id = fields.Many2one(related = "project_id.partner_id" , string = "Customer")
    pricing_id = fields.Many2one('construction.pricing', string='Pricing', required=True)
    item_ids = fields.One2many('item.number', 'drawing_id', string='Item Code', copy=True)
    Division = fields.Selection([('GRC', 'GRC'),('GRP', 'GRP'),('GRG','GRG'),('MOULD', 'MOULD'),('STEEL', 'STEEL')],)
    Building = fields.Char(String='Building')
    name_seq = fields.Char(string='Drawing No', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    create_date = fields.Datetime(string="Create Date", default=datetime.now())
    close_date = fields.Datetime(string="Close Date", default=datetime.now())
    create_by_id = fields.Many2one('res.users', 'Created By',default=lambda self: self.env.uid)
    confirmed_by_id = fields.Many2one('res.users', string="Confirmed By", copy=False)
    department_manager_id = fields.Many2one('res.users', string="Department Manager", copy=False)
    approved_by_id = fields.Many2one('res.users', string="Approved By", copy=False)
    rejected_by = fields.Many2one('res.users', string="Rejected By", copy=False)
    confirmed_date = fields.Date(string="Confirmed Date", readonly=True, copy=False)
    department_approval_date = fields.Date(string="Department Approval Date", readonly=True, copy=False)
    approved_date = fields.Date(string="Approved Date", readonly=True, copy=False)
    rejected_date = fields.Date(string="Rejected Date", readonly=True, copy=False)
    reason_for_requisition = fields.Text(string="Reason For Requisition")
    user_id = fields.Many2one('res.users', 'Created By',default=lambda self: self.env.uid)
    state = fields.Selection([
        ('new', 'New'),
        ('department_approval', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting User Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel')], string='Stage', copy=False, default="new")
    active = fields.Boolean(default=True, help="If the active field is set to False")
    """la somme de tout les drawings """
    total_drawing = fields.Float(String='Total Drawing', compute='_compute_total_drawing',store=True)
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    #Calculate the total amount of any department in one drawing
    total_prod = fields.Float(String='Amount Production', compute='_compute_total_prod',store=True)
    total_deli = fields.Float(String='Amount Delivery', compute='_compute_total_deli',store=True)
    total_erec = fields.Float(String='Amount Erection', compute='_compute_total_erec',store=True)
    type_name = fields.Char('Type Name', compute='_compute_type_name')
    total_volume = fields.Char('Total Volume', compute='_compute_total_volume')
    total_test =fields.Float(string='tessssssst',compute='_compute_total_drawing2',store=True)
    division_copy=fields.Char(string='Division',compute='get_division',store=True)
    nb_production=fields.Integer(string='Progress Production',compute='avancement',store=True)
    nb_deli=fields.Integer(string='Progress Delivery',compute='avancement',store=True)
    nb_ere=fields.Integer(string='Progress Erection',compute='avancement',store=True)
    nb_total=fields.Integer(string='Progress Total',compute='avancement',store=True)
    nb_item=fields.Integer(string='number Item',compute='avancement',store=True)


    @api.multi
    @api.depends('item_ids.stage_id')
    def avancement(self):
        nb_item_pro =0
        nb_item_de = 0
        nb_item_er = 0
        nb_item_fi = 0
        try:
            nb_item = len(self.item_ids)

            for item in self.item_ids:
                if item.stage_id.sequence == 1 :
                    nb_item_pro += 1
                if item.stage_id.sequence == 2 :
                    nb_item_pro += 1
                if item.stage_id.sequence == 3 :
                    nb_item_de += 1
                if item.stage_id.sequence == 4 :
                    nb_item_er += 1
                if item.stage_id.sequence == 5 :
                    nb_item_fi += 1
            progress_pr=((nb_item_de+nb_item_er+nb_item_fi)/nb_item)*100
            progress_de=((nb_item_er+nb_item_fi)/nb_item)*100
            progress_er=(nb_item_fi/nb_item)*100
        except ZeroDivisionError:
            progress_pr=0
            progress_de=0
            progress_er=0

        self.nb_production= progress_pr
        self.nb_deli=progress_de
        self.nb_ere= progress_er
        self.nb_total= round((progress_pr+progress_de+progress_er)/3)
        self.nb_item=nb_item
                
    @api.multi
    @api.depends('Division')
    def get_division(self):
        for record in self:
            record.division_copy=record.Division

        
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        res = {}
        if self.project_id :
            res =  {'domain': {'pricing_id': [('project_id', '=', self.project_id.id)]}}
            search_pricing = self.env['construction.pricing'].search([('project_id', '=', self.project_id.id)], limit=1)
            self.pricing_id = search_pricing.id
        else : 
            res = {'domain':{'pricing_id':[]}}
            self.pricing_id = ""
        return res

    @api.onchange('pricing_id')
    def onchange_pricing_id(self):
        for record in self.item_ids :
            record.pricing_id = self.pricing_id.id
    # @api.multi
    # def send_mail_template(self):
    #     # Find the e-mail template
    #     template = self.env.ref('drawing.boq_email_template')
    #     # You can also find the e-mail template like this:
    #     # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

    #     # Send out the e-mail template to the user
    #     self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in ('draft', 'sent', 'cancel') else _('Sales Order')

    #mail template
    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('drawing',   'boq_email_template4')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'construction.drawing',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        # ****************************
        # self.ensure_one()
        # ir_model_data = self.env['ir.model.data']
        # try:
        #     template_id = ir_model_data.get_object_reference('drawing', 'boq_email_template3')[1]
        # except ValueError:
        #     template_id = False
        # try:
        #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        # except ValueError:
        #     compose_form_id = False
        # lang = self.env.context.get('lang')
        # template = template_id and self.env['mail.template'].browse(template_id)
        # if template and template.lang:
        #     lang = template._render_template(template.lang, 'construction.drawing', self.ids[0])
        # ctx = {
        #     'default_model': 'construction.drawing',
        #     'default_res_id': self.ids[0],
        #     'default_use_template': bool(template_id),
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        #     'mark_so_as_sent': True,
        #     'model_description': self.with_context(lang=lang).type_name,
        #     'custom_layout': "mail.mail_notification_paynow",
        #     'proforma': self.env.context.get('proforma', False),
        #     'force_email': True
        # }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(compose_form_id, 'form')],
        #     'view_id': compose_form_id,
        #     'target': 'new',
        #     'context': ctx,
        # }

    @api.multi
    def force_quotation_send(self):
        for order in self:
            email_act = order.action_quotation_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    # the currency of project
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id

    '''
        This function give status for the drawing 
    '''
    @api.multi
    def print_quotation(self):
        return self.env.ref('drawing.report_boq').report_action(self)

    @api.multi
    def confirm_drawing(self):
        res = self.write({
            'state': 'department_approval',
            'confirmed_by_id': self.env.user.id,
            'confirmed_date': datetime.now()
        })
        return res

    @api.multi
    def department_approve(self):
        res = self.write({
            'state': 'ir_approve',
            'department_manager_id': self.env.user.id,
            'department_approval_date': datetime.now()
        })
        return res

    @api.multi
    def action_cancel(self):
        res = self.write({
            'state': 'cancel',
        })
        return res

    @api.multi
    def action_reject(self):
        res = self.write({
            'state': 'cancel',
            'rejected_date': datetime.now(),
            'rejected_by': self.env.user.id
        })
        return res

    @api.multi
    def action_reset_draft(self):
        res = self.write({
            'state': 'new',
        })
        return res

    @api.multi
    def action_approve(self):
        res = self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': datetime.now()
        })
        return res

    '''
            This function create a sequence for the drawing loaded by default
    '''

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('construction.drawing') or _('New')
        result = super(ConstructionDrawing, self).create(vals)
        return result

    @api.multi
    def pricing(self):
        self.ensure_one()
        return {
            'name': _('Pricing'),
            'domain': [('drawing_id', '=', self.id)],
            'res_model': 'construction.pricing',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d,'default_drawing_id': %d}" % (self.project_id.id, self.id)
        }

    #Compute the total amount of the drawing in the project
    @api.multi
    @api.depends('item_ids.Amount_total')
    def _compute_total_drawing(self):
        for line in self:
            total_drawing = 0.0
            for rec in line.item_ids:
                total_drawing += rec.Amount_total
            line.update({
                'total_drawing': total_drawing,
            })
    @api.multi
    @api.depends('item_ids.Amount_total')
    def _compute_total_drawing2(self):
        logging.info("tessssssssssssssst")
        for line in self:
            total_drawing = 0.0
            for rec in line.item_ids:
                total_drawing += rec.Amount_total
            # total_test = total_drawing
            line.update({
                'total_test': total_drawing,
            })

    #Compute the Volume of item
    @api.multi
    def _compute_total_volume(self):
        total = 0.0
        for rec in self.item_ids:
            total += rec.Volume
        self.total_volume = total


    # compute the amount of any department
    @api.multi
    @api.depends('item_ids.Amount_prod')
    def _compute_total_prod(self):
        for line in self:
            total_prod = 0.0
            for rec in line.item_ids:
                total_prod += rec.Amount_prod
            line.update({
                'total_prod': total_prod,
            })

    @api.multi
    @api.depends('item_ids.Amount_deli')
    def _compute_total_deli(self):
        for line in self:
            total_deli = 0.0
            for rec in line.item_ids:
                total_deli += rec.Amount_deli
            line.update({
                'total_deli': total_deli,
            })

    @api.multi
    @api.depends('item_ids.Amount_erec')
    def _compute_total_erec(self):
        for line in self:
            total_erec = 0.0
            for rec in line.item_ids:
                total_erec += rec.Amount_erec
            line.update({
                'total_erec': total_erec,
            })

    '''
    @api.onchange('pricing_id')
    @api.depends('pricing_id')
    def onchange_product_id(self):
        for rec in self:
            # lines = ([5, 0, 0])
            lines = []
            for line in self.item_ids:
                vals = {
                    'pricing_id': self.pricing_id,
                    'UR_production': self.pricing_id.UR_production,
                    'UR_delivery': self.pricing_id.UR_delivery,
                    'UR_erection': self.pricing_id.UR_erection,
                }
                lines.append(vals)
            rec.item_ids = lines
    '''


# # RES PARTNER inherit
# class Partner(models.Model):
#     _inherit = 'res.partner'

#     @api.multi
#     def send_mail_template(self):
#         # Find the e-mail template
#         template = self.env.ref('mail_template_demo.example_email_template')
#         # You can also find the e-mail template like this:
#         # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

#         # Send out the e-mail template to the user
#         self.env['mail.template'].browse(template.id).send_mail(self.id)