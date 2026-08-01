# -*- coding: utf-8 -*-
from odoo import models, fields

class AccessMenu(models.Model):
    _name = 'access.menu'
    _description = 'Menu Visibility Restriction'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    menu_id = fields.Many2one('ir.ui.menu', string='Menu to Hide', required=True, ondelete='cascade')
    full_name = fields.Char(related='menu_id.complete_name', string='Menu Path', store=True)
