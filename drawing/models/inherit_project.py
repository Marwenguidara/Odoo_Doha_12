# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID


""" Project Custom"""
class Project(models.Model):
    _inherit = 'project.project'
    drawing_ids = fields.One2many('construction.drawing', 'project_id', string="Drawing")
    @api.multi
    def action_open_items_sub(self):
        self.ensure_one()
        return {
            'name': _('Items Sub'),
            'domain': [('project_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'item.sub',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_project_id': %d}" % (self.id)
        }
    @api.multi
    def action_open_items_code(self):
        self.ensure_one()
        return {
            'name': _('Items Code'),
            'domain': [('project_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'item.code',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_project_id': %d}" % (self.id)
        }
    @api.multi
    def action_open_items_number(self):
        self.ensure_one()
        return {
            'name': _('Items Code'),
            'domain': [('project_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'item.number',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_project_id': %d}" % (self.id)
        }