# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccessButton(models.Model):
    _name = 'access.button'
    _description = 'Button & Notebook Tab Restrictions'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Technical Name', store=True)

    button_type = fields.Selection([
        ('button', 'Header / Stat / Action Button'),
        ('tab', 'Notebook Page / Tab')
    ], string='Target Element Type', required=True, default='button')

    button_name = fields.Char(
        string='Technical Identifier / Label',
        required=True,
        help='Technical name (name="..."), string label (string="..."), or icon/class of the button or tab to hide.'
    )
    title = fields.Char(string='Description / Purpose')

    @api.constrains('model_id', 'button_name')
    def _check_button_fields(self):
        for rec in self:
            if not rec.model_id or not rec.button_name:
                raise ValidationError(_("Please select a 'Target Model' and specify a 'Technical Identifier' for all entries in the Buttons & Tabs list."))
