# -*- coding: utf-8 -*-
from odoo import models, fields

class AccessAuditLog(models.Model):
    _name = 'access.audit.log'
    _description = 'Access Security Audit Log'
    _order = 'create_date desc'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Modified By', default=lambda self: self.env.user)
    action_type = fields.Selection([
        ('create', 'Profile Created'),
        ('update', 'Rules Updated'),
        ('user_assigned', 'Users Assigned'),
        ('active_toggle', 'Status Toggled')
    ], string='Action Category', required=True, default='update')
    details = fields.Text(string='Audit Summary', required=True)
