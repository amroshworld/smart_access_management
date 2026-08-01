# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccessChatter(models.Model):
    _name = 'access.chatter'
    _description = 'Chatter Component Access Restrictions'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Technical Name', store=True)

    hide_chatter = fields.Boolean(string='Hide Entire Chatter Widget', help='Hides the entire chatter panel for this model.')
    hide_send_mail = fields.Boolean(string='Hide "Send Message"', help='Hides the Send Message composer.')
    hide_log_notes = fields.Boolean(string='Hide "Log Note"', help='Hides the internal Log Note composer.')
    hide_schedule_activity = fields.Boolean(string='Hide "Schedule Activity"', help='Hides the Activity button in chatter.')
    hide_followers = fields.Boolean(string='Hide Followers', help='Hides the followers section in chatter.')

    @api.constrains('model_id')
    def _check_chatter_model(self):
        for rec in self:
            if not rec.model_id:
                raise ValidationError(_("Please select a 'Target Model' for all entries in the Chatter Controls list."))
