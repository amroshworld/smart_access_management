# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccessMenu(models.Model):
    _name = 'access.menu'
    _description = 'Menu Visibility Restriction'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    menu_id = fields.Many2one('ir.ui.menu', string='Menu to Hide', required=True, ondelete='cascade')
    full_name = fields.Char(related='menu_id.complete_name', string='Full Menu Hierarchy', store=True)

    @api.constrains('menu_id')
    def _check_menu_id(self):
        for rec in self:
            if not rec.menu_id:
                raise ValidationError(_("Please select a 'Menu to Hide' for all entries in the Menu Visibility list."))


class IrUiMenuExtension(models.Model):
    _inherit = 'ir.ui.menu'

    @api.depends('complete_name', 'name')
    def _compute_display_name(self):
        super()._compute_display_name()
        for menu in self:
            if menu.complete_name:
                menu.display_name = menu.complete_name
