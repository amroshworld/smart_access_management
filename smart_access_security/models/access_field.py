# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccessField(models.Model):
    _name = 'access.field'
    _description = 'Field Level Access Rights'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    field_id = fields.Many2one(
        'ir.model.fields', string='Target Field', required=True, ondelete='cascade',
        domain="[('model_id', '=', model_id)]"
    )
    field_name = fields.Char(related='field_id.name', string='Field Technical Name', store=True)

    mode = fields.Selection([
        ('invisible', 'Make Invisible'),
        ('readonly', 'Make Read-Only'),
        ('required', 'Make Required')
    ], string='Access Restriction', required=True, default='invisible')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_id = False

    @api.constrains('model_id', 'field_id')
    def _check_field_and_model(self):
        for rec in self:
            if not rec.model_id or not rec.field_id:
                raise ValidationError(_("Please select both a 'Target Model' and a 'Target Field' for all entries in the Field Controls list."))
