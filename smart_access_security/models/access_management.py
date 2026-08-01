# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccessManagement(models.Model):
    _name = 'access.management'
    _description = 'Smart Access Management Profile'
    _order = 'sequence, id desc'

    name = fields.Char(string='Profile Name', required=True, translate=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Priority Sequence', default=10)
    color = fields.Integer(string='Color Index', default=4)
    description = fields.Text(string='Notes / Purpose')

    # Admin Testing Mode
    apply_to_admin = fields.Boolean(
        string='Apply Rules to Administrators (Testing Mode)',
        default=False,
        help='Enable this if you want security rules to also apply to System Administrator (admin) users for testing or strict governance.'
    )

    # Scope & Targets
    user_ids = fields.Many2many(
        'res.users', 'access_management_users_rel', 'access_id', 'user_id',
        string='Target Users'
    )
    company_ids = fields.Many2many(
        'res.company', 'access_management_company_rel', 'access_id', 'company_id',
        string='Companies', default=lambda self: self.env.companies
    )

    # Time-Based Access Expiration
    valid_from = fields.Datetime(string='Valid From', help='Profile active start timestamp.')
    valid_until = fields.Datetime(string='Valid Until (Expiration)', help='Profile automatically expires after this timestamp.')
    is_expired = fields.Boolean(string='Is Expired', compute='_compute_is_expired', store=False)

    # IP Whitelist & Location Restriction
    allowed_ip_addresses = fields.Char(
        string='Allowed IP Addresses',
        help='Comma-separated IPs or subnets (e.g. 192.168.1.100, 10.0.0.0/24). Leave blank to allow any IP.'
    )

    # Global System Safeguards
    readonly_user = fields.Boolean(
        string='Global Read-Only User',
        help='Forces all models to be read-only for targeted users across the system.'
    )
    disable_debug = fields.Boolean(
        string='Disable Developer Mode',
        help='Blocks targeted users from activating ?debug mode in Odoo.'
    )
    disable_login = fields.Boolean(
        string='Block Login',
        help='Prevents targeted users from logging into the database.'
    )
    disable_app_install = fields.Boolean(
        string='Disable Apps Installation',
        help='Prevents users from installing, uninstalling, or updating modules in Apps menu.'
    )
    disable_api_access = fields.Boolean(
        string='Disable XML-RPC / API Access',
        help='Blocks external API scripts and XML-RPC/JSON-RPC authentication for target users.'
    )

    # One2many Sub-rules
    hide_menu_ids = fields.One2many('access.menu', 'access_management_id', string='Menu Restrictions')
    access_model_ids = fields.One2many('access.model', 'access_management_id', string='Model Restrictions')
    access_field_ids = fields.One2many('access.field', 'access_management_id', string='Field Restrictions')
    access_button_ids = fields.One2many('access.button', 'access_management_id', string='Button & Tab Restrictions')
    access_chatter_ids = fields.One2many('access.chatter', 'access_management_id', string='Chatter Restrictions')
    access_domain_ids = fields.One2many('access.domain', 'access_management_id', string='Domain & Record Rules')
    audit_log_ids = fields.One2many('access.audit.log', 'access_management_id', string='Audit Trail')

    # Counters for Dashboard KPI Badges
    hide_menu_count = fields.Integer(compute='_compute_rule_counts', string='Menus Restricted')
    access_model_count = fields.Integer(compute='_compute_rule_counts', string='Models Restricted')
    access_field_count = fields.Integer(compute='_compute_rule_counts', string='Fields Restricted')
    access_button_count = fields.Integer(compute='_compute_rule_counts', string='Buttons Restricted')
    access_chatter_count = fields.Integer(compute='_compute_rule_counts', string='Chatter Restricted')

    @api.depends('valid_from', 'valid_until')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for rec in self:
            expired = False
            if rec.valid_until and now > rec.valid_until:
                expired = True
            elif rec.valid_from and now < rec.valid_from:
                expired = True
            rec.is_expired = expired

    @api.depends('hide_menu_ids', 'access_model_ids', 'access_field_ids', 'access_button_ids', 'access_chatter_ids')
    def _compute_rule_counts(self):
        for rec in self:
            rec.hide_menu_count = len(rec.hide_menu_ids)
            rec.access_model_count = len(rec.access_model_ids)
            rec.access_field_count = len(rec.access_field_ids)
            rec.access_button_count = len(rec.access_button_ids)
            rec.access_chatter_count = len(rec.access_chatter_ids)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env['ir.ui.menu'].clear_caches()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.env['ir.ui.menu'].clear_caches()
        return res

    def unlink(self):
        res = super().unlink()
        self.env['ir.ui.menu'].clear_caches()
        return res

    def action_open_quick_wizard(self):
        """ Opens Quick Configurator Wizard for current profile """
        self.ensure_one()
        return {
            'name': _('Batch Apply Model Rules'),
            'type': 'ir.actions.act_window',
            'res_model': 'access.config.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_access_management_id': self.id}
        }

    def action_clone_profile(self):
        """ Enterprise Feature: Clone Security Profile """
        self.ensure_one()
        new_profile = self.sudo().copy({'name': f"{self.name} (Copy)"})
        self.env['access.audit.log'].sudo().create({
            'access_management_id': new_profile.id,
            'action_type': 'create',
            'details': f"Cloned profile from '{self.name}'."
        })
        return {
            'name': _('Cloned Profile'),
            'type': 'ir.actions.act_window',
            'res_model': 'access.management',
            'res_id': new_profile.id,
            'view_mode': 'form',
        }

    @api.model
    def get_user_access_profiles(self, user=None):
        """ Returns all active profiles applicable to the given user and current company """
        if not user:
            user = self.env.user
        current_company = self.env.company
        now = fields.Datetime.now()
        domain = [
            ('active', '=', True),
            ('user_ids', 'in', user.id),
            '|', ('company_ids', '=', False), ('company_ids', 'in', current_company.id),
            '|', ('valid_from', '=', False), ('valid_from', '<=', now),
            '|', ('valid_until', '=', False), ('valid_until', '>=', now),
        ]
        profiles = self.sudo().search(domain)
        return profiles
