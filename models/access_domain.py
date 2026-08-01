# -*- coding: utf-8 -*-
from odoo import models, fields

class AccessDomain(models.Model):
    _name = 'access.domain'
    _description = 'Record Level Domain Access Rules'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Technical Name', store=True)

    domain = fields.Text(
        string='Domain Filter Expression',
        required=True,
        default="[('id', '!=', False)]",
        help="Standard Odoo domain string, e.g. [('user_id', '=', user.id)]"
    )
