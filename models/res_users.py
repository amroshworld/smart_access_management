# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class ResUsers(models.Model):
    _inherit = 'res.users'

    access_management_ids = fields.Many2many(
        'access.management', 'access_management_users_rel', 'user_id', 'access_id',
        string='Access Profiles'
    )

    is_readonly_user = fields.Boolean(
        string='Is Read-Only User',
        compute='_compute_security_profile_status',
        store=False
    )
    is_dev_mode_disabled = fields.Boolean(
        string='Is Dev Mode Disabled',
        compute='_compute_security_profile_status',
        store=False
    )

    def _compute_security_profile_status(self):
        for user in self:
            profiles = self.env['access.management'].get_user_access_profiles(user)
            user.is_readonly_user = any(p.readonly_user for p in profiles)
            user.is_dev_mode_disabled = any(p.disable_debug for p in profiles)

    @api.model
    def check_user_dev_mode_allowed(self):
        """ Check if current user is allowed to use developer mode """
        user = self.env.user
        profiles = self.env['access.management'].get_user_access_profiles(user)
        if any(p.disable_debug for p in profiles):
            return False
        return True
