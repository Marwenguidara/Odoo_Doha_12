# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, SUPERUSER_ID
from datetime import datetime

class ProjectItemType(models.Model):
    _name = 'project.item.type'
    _description = 'item Stage'
    _order = 'sequence, id'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id',
                                       string='Projects',
                                       default=_get_default_project_ids)
    legend_priority = fields.Char(
            string='Starred Explanation', translate=True,
            help='Explanation text to help users using the star on tasks or issues in this stage.')
    legend_blocked = fields.Char(
            'Orange Kanban Label', default=lambda s: _('Ready for delvry'), translate=True, required=True,
            help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
            'Green Kanban Label', default=lambda s: _('finshed'), translate=True, required=True,
            help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
            'Grey Kanban Label', default=lambda s: _('Drawing'), translate=True, required=True,
            help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    legend_delivery= fields.Char(
            'Yellow Kanban Label', default=lambda s: _('Pendig'), translate=True, required=True,
            help='Override the default value displayed for the delivery state for kanban selection, when the task or issue is in that stage.')
    legend_erection= fields.Char(
            'Yellow Kanban Label', default=lambda s: _('Ready for erection'), translate=True, required=True,
            help='Override the default value displayed for the erection state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
            'mail.template',
            string='Email Template',
            domain=[('model', '=', 'project.task')],
            help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                              help='This stage is folded in the kanban view when there are no records in that stage to display.')
    rating_template_id = fields.Many2one(
            'mail.template',
            string='Rating Email Template',
            domain=[('model', '=', 'project.task')],
            help="If set and if the project's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
                                                      help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
                                                           " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
                                                           " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")



    @api.multi
    def unlink(self):
        stages = self
        default_project_id = self.env.context.get('default_project_id')
        if default_project_id:
            shared_stages = self.filtered(
                lambda x: len(x.project_ids) > 1 and default_project_id in x.project_ids.ids)
            tasks = self.env['project.task'].with_context(active_test=False).search(
                [('project_id', '=', default_project_id), ('stage_id', 'in', self.ids)])
            if shared_stages and not tasks:
                shared_stages.write({'project_ids': [(3, default_project_id)]})
                stages = self.filtered(lambda x: x not in shared_stages)
            return super(ProjectItemType, stages).unlink()