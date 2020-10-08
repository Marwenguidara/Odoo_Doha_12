# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID
from datetime import datetime
import logging

#the items & sub items
class ItemNumber(models.Model):
    _name = 'item.number'
    _description = 'Items Records for Projects Lines'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'title'


    def _default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    title = fields.Char('Item No', required=True)
    drawing_id = fields.Many2one('construction.drawing', 'Drawing')
    project_id = fields.Many2one(related='drawing_id.project_id', store=True, string='Project', readonly=True)
    pricing_id = fields.Many2one('construction.pricing', String='Pricing',
                                 default=lambda self: self.env.context.get('drawing_id'))
    Type = fields.Char('Type')
    image_medium = fields.Binary(String='image',attachment=True)
    Type_of_finish = fields.Char('Type of finish')
    Length = fields.Float('Length', required=True)
    Width = fields.Float('Width', required=True)
    Height = fields.Float('Height', required=True)
    Thick = fields.Float('Thick', required=True)
    Quantity = fields.Integer('Quantity', required=True)
    Volume = fields.Float('Volume', compute='_compute_total', required=True)
    Unit = fields.Many2one('uom.uom', 'Unit Of Measure')

    # get the unit pricing for each department
    UR_production = fields.Float(String='UR Production',compute='onchange_pricing_id')
    UR_delivery = fields.Float(String='UR Delivery',compute='onchange_pricing_id')
    UR_erection = fields.Float(String='UR Erection',compute='onchange_pricing_id')

    #get the amount of departments
    Amount_prod = fields.Float(String='Amount Production', compute='_compute_total_production', required=True)
    Amount_deli = fields.Float(String='Amount Delivery', compute='_compute_total_delivery', required=True)
    Amount_erec = fields.Float(String='Amount Erection', compute='_compute_total_erection', required=True)

    # get the Total unit sum of three units
    UR_total = fields.Float(String='Unit Rate Total', compute='_compute_total_UR', required=True)
    Amount_total = fields.Float(String='Amount Total', compute='_compute_total_amount', required=True)
   
    # the unit rate of project with currency
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    Unit_Production = fields.Float(String='Unit Production', compute='_compute_unit_production', required=True)
    Unit_Delivery = fields.Float(String='Unit Delivery', compute='_compute_unit_delivery', required=True)
    Unit_Erection = fields.Float(String='Unit Erection', compute='_compute_unit_erection', required=True)
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the estimation without removing it.")

    stage_id = fields.Many2one('project.item.type', string='Stage', ondelete='restrict', track_visibility='onchange', index=True, copy=False,
        domain="['|', ('project_ids', '=', False), ('project_ids', '=', project_id)]",
        group_expand='_read_group_stage_ids', default=lambda self: self.env['project.item.type'].search([], limit=1))
    kanban_state = fields.Selection([
        ('White', 'White'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Orange', 'Orange'),
        ('Yellow', 'Yellow')],string='Kanban State',default='Blue',compute='set_state_kanban')
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label',
                                     track_visibility='onchange')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True,
                                 related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True,
                              related_sudo=False)
    legend_delivery = fields.Char(related='stage_id.legend_delivery', string='Kanban Delivery Explanation', readonly=True,
                              related_sudo=False)
    legend_erection = fields.Char(related='stage_id.legend_erection', string='Kanban Erection Explanation', readonly=True,
                              related_sudo=False)
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.uid)
    item_code_ids = fields.One2many('item.code', 'item_id', string='Code Items')
    sub_item_ids = fields.One2many('item.sub', 'item_id', string="Sub Items")
    sub_items_status = fields.Html(string="SUBItems", compute='get_all_sub_items')
    kanbancolor = fields.Integer('Color Index', compute="set_kanban_color")
    

    @api.multi
    @api.depends('stage_id')
    def set_state_kanban(self):
        j=0
        for record in self :
            if record.stage_id.sequence == 2:
                record.kanban_state='Blue'
            if record.stage_id.sequence == 5:
                record.kanban_state='Green'

            if record.stage_id.sequence == 4:
                record.kanban_state='Orange'
            if record.stage_id.sequence == 3:
                record.kanban_state='Yellow'
            if record.stage_id.sequence == 1:
                record.kanban_state='White'

            # for i in record.item_code_ids :
            #      if i.stage_id.sequence == 4:
            #              j += 1
            #         # if i.stage_id.sequence == 3:
            #         #         k += 1
            #         # if i.stage_id.sequence == 2:
            #         #         y += 1
            #         # if i.stage_id.sequence == 1:
            #         #         f += 1
            # if len(record.item_code_ids):

            #     if len(record.item_code_ids)==j:
            #         record.sudo().write({'stage_id':4})
            #         record.kanban_state='Green'

        
                    
    def set_kanban_color(self):
        for record in self:
            kanbancolor = 0
            if record.kanban_state == 'Blue':
                kanbancolor = 4
            elif record.kanban_state == 'Green':
                kanbancolor = 10
            elif record.kanban_state == 'Orange':
                kanbancolor = 2
            elif record.kanban_state == 'Yellow':
                kanbancolor = 3
            else:
                kanbancolor=0
            record.kanbancolor = kanbancolor

    @api.multi
    @api.depends('project_id','sub_item_ids')
    def get_all_sub_items(self):
        for rec in self:
            if rec.sub_item_ids:
                sub_items = []
                body = """<table  style='width: 100%;'>"""
                body += """<tr>"""
                body += """<td style="width: 50%;border: 1px solid grey;">""" + 'Item Name' + """</td>"""
                body += """<td style="width: 50%;border: 1px solid grey;">""" + 'Stage' + """</td>"""
                body += """</tr>"""
                for data in rec.sub_item_ids:
                    body += """<tr>"""
                    body += """<td style="width: 50%;border: 1px solid grey;">""" + data.title + """</td>"""
                    body += """<td style="width: 50%;border: 1px solid grey;">""" + data.stage_id.name + """</td>"""
                    body += """</tr>"""
                body += "</table>"
                rec.sub_items_status = body


    @api.multi
    def action_open_sub_item(self):
        self.ensure_one()
        return {
            'name': _('Sub Item'),
            'domain': [('item_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'item.sub',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_item_id': %d}" % (self.id)
        }

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            
            if task.kanban_state == 'White':
                task.kanban_state_label = task.legend_normal
            if task.kanban_state == 'Blue':
                task.kanban_state_label = task.legend_delivery
            elif task.kanban_state == 'Orange':
                task.kanban_state_label = task.legend_erection
            elif task.kanban_state == 'Yellow':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['project.item.type'].search([])

    '''
    # get the unit rate price from pricing or this project
    @api.multi
    @api.onchange('pricing_id')
    def onchange_pricing_id(self):
        res = {}
        if not self.pricing_id:
            return res
        self.UR_production = self.pricing_id.UR_production
        self.UR_delivery = self.pricing_id.UR_delivery
        self.UR_erection = self.pricing_id.UR_erection
    '''

    # get the unit rate price from pricing or this project
    @api.multi
    @api.depends('pricing_id')
    def onchange_pricing_id(self):
        res = {}
        for record in self:
            if not record.pricing_id:
                return res
            record.UR_production = record.pricing_id.UR_production
            record.UR_delivery = record.pricing_id.UR_delivery
            record.UR_erection = record.pricing_id.UR_erection

    #open the item codes
    @api.multi
    def open_bom(self):
        self.ensure_one()
        ctx = {
        'default_item_id': self.id,
        'default_project_id' :self.project_id.id,
        'default_title' : self.title,
        }
        return {
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'item.code',
        'target': 'new',
        'context': ctx,
        }

    #Compute Volume of an item
    @api.multi
    @api.depends('Length', 'Width', 'Height')
    def _compute_total(self):
        for rec in self:
            rec.Volume = rec.Length * rec.Width * rec.Height

    #Compute the total units in the pricing
    @api.multi
    @api.depends('UR_production', 'UR_delivery', 'UR_erection')
    def _compute_total_UR(self):
        for rec in self:
            rec.UR_total = rec.UR_production + rec.UR_delivery + rec.UR_erection

    #Compute the total amounts of departments
    @api.multi
    @api.depends('Amount_prod', 'Amount_deli', 'Amount_erec')
    def _compute_total_amount(self):
        for rec in self:
            rec.Amount_total = rec.Amount_prod + rec.Amount_deli + rec.Amount_erec

    @api.multi
    @api.depends('Amount_prod' , 'Quantity', 'Unit_Production')
    def _compute_total_production(self):
        for rec in self:
            rec.Amount_prod = rec.Quantity * rec.Unit_Production

    @api.multi
    @api.depends('Amount_deli', 'Unit_Delivery', 'Quantity')
    def _compute_total_delivery(self):
        for rec in self:
            rec.Amount_deli = rec.Quantity * rec.Unit_Delivery

    @api.multi
    @api.depends('Amount_erec', 'Unit_Erection', 'Quantity')
    def _compute_total_erection(self):
        for rec in self:
            rec.Amount_erec = rec.Quantity * rec.Unit_Erection

    # Compute Unit rates of amount
    @api.multi
    @api.depends('Unit_Production','UR_production', 'Volume')
    def _compute_unit_production(self):
        for rec in self:
            rec.Unit_Production = rec.UR_production * rec.Volume

    @api.multi
    @api.depends('Unit_Delivery','UR_delivery', 'Volume')
    def _compute_unit_delivery(self):
        for rec in self:
            rec.Unit_Delivery = rec.UR_delivery * rec.Volume

    @api.multi
    @api.depends('Unit_Erection', 'UR_erection', 'Volume')
    def _compute_unit_erection(self):
        for rec in self:
            rec.Unit_Erection = rec.UR_erection * rec.Volume

    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id

# ITEM CODE
class ItemCodeID(models.Model):
    _name = 'item.code'
    _description = 'Item Code'
    _rec_name = 'title'


    item_id = fields.Many2one('item.number', string='Item No',
                              default=lambda self: self.env.context.get('item_id'))
    project_id = fields.Many2one('project.project', string='Project',default=lambda self: self.env.context.get('project_id'))
    title = fields.Char('Item Code', required=True)
    
    image_medium = fields.Binary(String='image',attachment=True)
    sequence = fields.Integer('Item Code number', default=10)
    description = fields.Html('Description', translate=True, oldname="note",
                              help="An introductory text to your page")
    sub_ids = fields.One2many('item.sub', 'code_id', string='Item Subs', copy=True)
    Type = fields.Char('Type')
    Type_of_finish = fields.Char('Type of finish')
    Length = fields.Float('Length', required=True)
    Width = fields.Float('Width', required=True)
    Height = fields.Float('Height', required=True)
    Thick = fields.Float('Thick', required=True)
    Quantity = fields.Integer('Quantity', required=True)
    Unit = fields.Many2one('uom.uom','Unit Of Measure')



    @api.multi
    def _default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:

            return False

        return self.stage_find(project_id, [('fold', '=', False)])

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the estimation without removing it.")

    stage_id = fields.Many2one('project.item.type', string='Stage', ondelete='restrict', track_visibility='onchange', index=True, copy=False,
        domain="['|', ('project_ids', '=', False), ('project_ids', '=', project_id)]",
        group_expand='_read_group_stage_ids', default=lambda self: self.env['project.item.type'].search([], limit=1))
    kanban_state = fields.Selection([
        ('White', 'White'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Orange', 'Orange'),
        ('Yellow', 'Yellow')],string='Kanban State',default='Blue',compute='set_state_kanban')
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label',
                                     track_visibility='onchange')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True,
                                 related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True,
                              related_sudo=False)
    legend_delivery = fields.Char(related='stage_id.legend_delivery', string='Kanban Delivery Explanation', readonly=True,
                              related_sudo=False)
    legend_erection = fields.Char(related='stage_id.legend_erection', string='Kanban Erection Explanation', readonly=True,
                              related_sudo=False)
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.uid)
    kanbancolor = fields.Integer('Color Index', compute="set_kanban_color")
    @api.multi
    @api.depends('stage_id')
    def set_state_kanban(self):
        j = 0
        k = 0
        y = 0
        f = 0
        for record in self :

                if record.stage_id.sequence == 2:
                    record.kanban_state='Blue'
                if record.stage_id.sequence == 5:
                    record.kanban_state='Green'

                if record.stage_id.sequence == 4:
                    record.kanban_state='Orange'
                if record.stage_id.sequence == 3:
                    record.kanban_state='Yellow'
                if record.stage_id.sequence == 1:
                    record.kanban_state='White'
                rech_item_fin = self.env['item.code'].sudo().search([('item_id','=',record.item_id.id)])
                logging.info(rech_item_fin)
                if rech_item_fin : 
                    for i in rech_item_fin:
                        if i.stage_id.sequence == 5:
                            j += 1
                        if i.stage_id.sequence == 4:
                            k += 1
                        if i.stage_id.sequence == 3:
                            y += 1
                        if i.stage_id.sequence == 2:
                            f += 1
                if  len(rech_item_fin) == j:
                    rech_item_fin[0].item_id.sudo().write({'stage_id':5})  
                elif  len(rech_item_fin) == k:
                    rech_item_fin[0].item_id.sudo().write({'stage_id':4})
                elif  len(rech_item_fin) == y:
                    rech_item_fin[0].item_id.sudo().write({'stage_id':3}) 
                elif  len(rech_item_fin) == f:
                    rech_item_fin[0].item_id.sudo().write({'stage_id':2})
            
        
                    
    def set_kanban_color(self):
        for record in self:
            kanbancolor = 0
            if record.kanban_state == 'Blue':
                kanbancolor = 4
            elif record.kanban_state == 'Green':
                kanbancolor = 10
            elif record.kanban_state == 'Orange':
                kanbancolor = 2
            elif record.kanban_state == 'Yellow':
                kanbancolor = 3
            else:
                kanbancolor=0
            record.kanbancolor = kanbancolor

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            
            if task.kanban_state == 'White':
                task.kanban_state_label = task.legend_normal
            if task.kanban_state == 'Blue':
                task.kanban_state_label = task.legend_delivery
            elif task.kanban_state == 'Orange':
                task.kanban_state_label = task.legend_erection
            elif task.kanban_state == 'Yellow':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['project.item.type'].search([])

class ItemSub(models.Model):
    _name = 'item.sub'
    _description = 'Item Sub'
    _rec_name = 'title'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence,id'

    # Model fields #
    title = fields.Char('Item Sub', required=True, translate=True)
    code_id = fields.Many2one('item.code', string='Parent Item',default=lambda self: self.env.context.get('code_id'),readonly=True)
    item_id = fields.Many2one(related='code_id.item_id', store=True, string='Parent Item',readonly=True)
    project_id = fields.Many2one('project.project',compute='get_item_data',string='Project')
    # drawing_id = fields.Many2one('construction.drawing', store=True, string='Drawing', readonly=True)
    sequence = fields.Integer('Sequence', default=10)
    image_medium = fields.Binary(String='image',attachment=True,)
    Length = fields.Float('Length', required=True)
    Width = fields.Float('Width', required=True)
    Height = fields.Float('Height', required=True)
    Thick = fields.Float('Thick', required=True)
    Quantity = fields.Integer('Quantity', required=True)
    Unit = fields.Many2one('uom.uom', 'Unit Of Measure')
    
    
    
    @api.multi
    @api.depends('item_id')
    def get_item_data(self):
        for rec in self:
            if rec.item_id:
                rec.project_id = rec.item_id.project_id.id

    """ Manage Status """
    def _default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:

            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the estimation without removing it.")

    stage_id = fields.Many2one('project.item.type', string='Stage', ondelete='restrict', track_visibility='onchange', index=True, copy=False,
        domain="['|', ('project_ids', '=', False), ('project_ids', '=', project_id)]",
        group_expand='_read_group_stage_ids', default=lambda self: self.env['project.item.type'].search([], limit=1))

    kanban_state = fields.Selection([
        ('White', 'White'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Orange', 'Orange'),
        ('Yellow', 'Yellow')],string='Kanban State',default='Blue',compute='set_state_kanban')
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label',
                                     track_visibility='onchange')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True,
                                 related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True,
                              related_sudo=False)
    legend_delivery = fields.Char(related='stage_id.legend_delivery', string='Kanban Delivery Explanation', readonly=True,
                              related_sudo=False)
    legend_erection = fields.Char(related='stage_id.legend_erection', string='Kanban Erection Explanation', readonly=True,
                              related_sudo=False)
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.uid)
    kanbancolor = fields.Integer('Color Index', compute="set_kanban_color")

    @api.multi
    @api.depends('stage_id')
    def set_state_kanban(self):
        j = 0
        k = 0
        y = 0
        f = 0

        for record in self :
            if record.stage_id.sequence == 2:
                    record.kanban_state='Blue'
            if record.stage_id.sequence == 5:
                    record.kanban_state='Green'

            if record.stage_id.sequence == 4:
                    record.kanban_state='Orange'
            if record.stage_id.sequence == 3:
                    record.kanban_state='Yellow'
            if record.stage_id.sequence == 1:
                    record.kanban_state='White'
            rech_item_fin = self.env['item.sub'].sudo().search([('code_id','=',record.code_id.id)])
            logging.info(rech_item_fin)
            if rech_item_fin : 
                for i in rech_item_fin:
                    if i.stage_id.sequence == 5:
                        j += 1
                    if i.stage_id.sequence == 4:
                        k += 1
                    if i.stage_id.sequence == 3:
                        y += 1
                    if i.stage_id.sequence == 2:
                        f += 1
                if  len(rech_item_fin) == j:
                    rech_item_fin[0].code_id.sudo().write({'stage_id':5})  
                elif  len(rech_item_fin) == k:
                    rech_item_fin[0].code_id.sudo().write({'stage_id':4})
                elif  len(rech_item_fin) == y:
                    rech_item_fin[0].code_id.sudo().write({'stage_id':3}) 
                elif  len(rech_item_fin) == f:
                    rech_item_fin[0].code_id.sudo().write({'stage_id':2})
                    
                # if len(record.sub_ids)==j:
                #     record.sudo().write({"stage_id":4})
                #     record.kanban_state='Green'
                # # elif len(record.sub_ids)==k:
                # #      record.sudo().write({"stage_id":3})
                # #      record.kanban_state='Orange'
                # # elif len(record.sub_ids)==y:
                # #      record.sudo().write({"stage_id":2})
                # #      record.kanban_state='Yellow'              
    def set_kanban_color(self):
        for record in self:
            kanbancolor = 0
            if record.kanban_state == 'Blue':
                kanbancolor = 4
            elif record.kanban_state == 'Green':
                kanbancolor = 10
            elif record.kanban_state == 'Orange':
                kanbancolor = 2
            elif record.kanban_state == 'Yellow':
                kanbancolor = 3
            else:
                kanbancolor=0
            record.kanbancolor = kanbancolor

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            
            if task.kanban_state == 'White':
                task.kanban_state_label = task.legend_normal
            if task.kanban_state == 'Blue':
                task.kanban_state_label = task.legend_delivery
            elif task.kanban_state == 'Orange':
                task.kanban_state_label = task.legend_erection
            elif task.kanban_state == 'Yellow':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done
    @api.multi
    def write(self,vals):
        logging.info(vals)
        return super(ItemSub, self).write(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['project.item.type'].search([])