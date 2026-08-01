# -*- coding: utf-8 -*-
from odoo import models, fields

class AccessModel(models.Model):
    _name = 'access.model'
    _description = 'Model Level Access Rights & Actions'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Technical Name', store=True)

    # Basic CRUD Access
    perm_read = fields.Boolean(string='Allow Read', default=True)
    perm_create = fields.Boolean(string='Allow Create', default=True)
    perm_write = fields.Boolean(string='Allow Edit', default=True)
    perm_unlink = fields.Boolean(string='Allow Delete', default=True)

    # Advanced Data Operation Controls
    perm_archive = fields.Boolean(string='Allow Archive', default=True, help='Unchecking hides Archive/Unarchive options in action menu.')
    perm_duplicate = fields.Boolean(string='Allow Duplicate', default=True, help='Unchecking hides Duplicate option in action menu.')
    perm_export = fields.Boolean(string='Allow Export', default=True, help='Unchecking hides Export button in list view.')
    perm_import = fields.Boolean(string='Allow Import', default=True, help='Unchecking hides Import records button.')

    # View Type Restrictions
    hide_kanban = fields.Boolean(string='Hide Kanban View')
    hide_list = fields.Boolean(string='Hide List View')
    hide_pivot = fields.Boolean(string='Hide Pivot View')
    hide_graph = fields.Boolean(string='Hide Graph View')
    hide_calendar = fields.Boolean(string='Hide Calendar View')

    # Reports & Server Actions
    hide_report_ids = fields.Many2many('ir.actions.report', string='Hide Reports', help='Select print reports to hide from the Print menu.')
    hide_action_ids = fields.Many2many('ir.actions.actions', string='Hide Actions', help='Select action menu items to hide for this model.')
