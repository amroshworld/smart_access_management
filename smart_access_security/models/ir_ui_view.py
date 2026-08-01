# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

# Core internal system models that must NEVER be mutated to avoid breaking Odoo core engine
ADMIN_SYSTEM_MODELS = (
    'access.menu', 'access.model', 'access.field', 'access.button',
    'access.chatter', 'access.domain', 'access.audit.log', 'access.config.wizard',
    'res.users', 'res.company', 'res.groups',
    'ir.model', 'ir.model.fields', 'ir.ui.view', 'ir.ui.menu',
    'ir.actions.act_window', 'ir.module.module', 'ir.attachment', 'ir.asset'
)

class BaseModelSecurity(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """ Enforce backend RPC/API access rights for active Access Management profiles """
        res = super(BaseModelSecurity, self).check_access_rights(operation, raise_exception=raise_exception)
        
        user = self.env.user
        if self._name in ADMIN_SYSTEM_MODELS or self._name.startswith('access.') or self._name.startswith('ir.'):
            return res

        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        # 1. Global Read-Only User Enforcement for target business models
        if any(p.readonly_user for p in profiles) and operation in ('create', 'write', 'unlink'):
            if raise_exception:
                raise AccessError(_("Global Read-Only Security Policy prevents %s operations on %s.") % (operation, self._name))
            return False

        # 2. Model Level CRUD Enforcement
        model_rules = profiles.mapped('access_model_ids').filtered(lambda r: r.model_name == self._name)
        for rule in model_rules:
            if operation == 'create' and not rule.perm_create:
                if raise_exception:
                    raise AccessError(_("Create access restricted for model %s.") % self._name)
                return False
            elif operation == 'write' and not rule.perm_write:
                if raise_exception:
                    raise AccessError(_("Edit access restricted for model %s.") % self._name)
                return False
            elif operation == 'unlink' and not rule.perm_unlink:
                if raise_exception:
                    raise AccessError(_("Delete access restricted for model %s.") % self._name)
                return False
            elif operation == 'read' and not rule.perm_read:
                if raise_exception:
                    raise AccessError(_("Read access restricted for model %s.") % self._name)
                return False

        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """ Enforce field-level read-only / invisible flags at dictionary level """
        res = super(BaseModelSecurity, self).fields_get(allfields=allfields, attributes=attributes)
        
        user = self.env.user
        if self._name in ADMIN_SYSTEM_MODELS or self._name.startswith('access.') or self._name.startswith('ir.'):
            return res

        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        field_rules = profiles.mapped('access_field_ids').filtered(lambda r: r.model_id.model == self._name)
        for f_rule in field_rules:
            fname = f_rule.field_name
            if fname in res:
                if f_rule.mode == 'invisible':
                    res[fname]['invisible'] = True
                elif f_rule.mode == 'readonly':
                    res[fname]['readonly'] = True
                elif f_rule.mode == 'required':
                    res[fname]['required'] = True

        return res


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _postprocess_access(self, model, node, access):
        """ Patch view XML architecture dynamically based on active security profiles """
        res = super(IrUiView, self)._postprocess_access(model, node, access)
        
        user = self.env.user
        if model in ADMIN_SYSTEM_MODELS or model.startswith('ir.'):
            return res

        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        # 1. Global Read-Only User
        if any(p.readonly_user for p in profiles):
            node.set('create', 'false')
            node.set('edit', 'false')
            node.set('delete', 'false')

        # Find rules matching current model
        model_rules = profiles.mapped('access_model_ids').filtered(lambda r: r.model_name == model)
        field_rules = profiles.mapped('access_field_ids').filtered(lambda r: r.model_id.model == model)
        button_rules = profiles.mapped('access_button_ids').filtered(lambda r: r.model_id.model == model)
        chatter_rules = profiles.mapped('access_chatter_ids').filtered(lambda r: r.model_id.model == model)

        # Apply Model level CRUD flags on root node
        for rule in model_rules:
            if not rule.perm_create:
                node.set('create', 'false')
            if not rule.perm_write:
                node.set('edit', 'false')
            if not rule.perm_unlink:
                node.set('delete', 'false')
            if not rule.perm_import:
                node.set('import', 'false')
            if not rule.perm_export:
                node.set('export_xlsx', 'false')

        # 2. Patch Field Rules
        for f_rule in field_rules:
            fname = f_rule.field_name
            for field_node in node.xpath(f"//field[@name='{fname}']"):
                if f_rule.mode == 'invisible':
                    field_node.set('invisible', '1')
                    field_node.set('column_invisible', '1')
                elif f_rule.mode == 'readonly':
                    field_node.set('readonly', '1')
                elif f_rule.mode == 'required':
                    field_node.set('required', '1')

        # 3. Patch Button & Notebook Tab Rules
        for b_rule in button_rules:
            b_identifier = b_rule.button_name
            if b_rule.button_type == 'button':
                expr = f"//button[@name='{b_identifier}' or @string='{b_identifier}' or contains(@class, '{b_identifier}')]"
                for b_node in node.xpath(expr):
                    b_node.set('invisible', '1')
                    b_node.set('column_invisible', '1')
            elif b_rule.button_type == 'tab':
                expr = f"//page[@name='{b_identifier}' or @string='{b_identifier}']"
                for p_node in node.xpath(expr):
                    p_node.set('invisible', '1')

        # 4. Patch Chatter Rules
        for c_rule in chatter_rules:
            if c_rule.hide_chatter:
                for chatter_node in node.xpath("//div[contains(@class, 'oe_chatter')] | //chatter"):
                    chatter_node.set('invisible', '1')
            else:
                if c_rule.hide_send_mail:
                    for sm in node.xpath("//button[contains(@class, 'o_Chatter_buttonSendMessage')]"):
                        sm.set('invisible', '1')
                if c_rule.hide_log_notes:
                    for ln in node.xpath("//button[contains(@class, 'o_Chatter_buttonLogNote')]"):
                        ln.set('invisible', '1')
                if c_rule.hide_schedule_activity:
                    for sa in node.xpath("//button[contains(@class, 'o_Chatter_buttonScheduleActivity')]"):
                        sa.set('invisible', '1')

        return res


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _load_menus_blacklist(self):
        """ Add profile-hidden menus to Odoo's menu blacklist """
        res = super(IrUiMenu, self)._load_menus_blacklist()
        user = self.env.user
        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        hidden_menu_ids = profiles.mapped('hide_menu_ids.menu_id.id')
        if hidden_menu_ids:
            res = list(set(res) | set(hidden_menu_ids))
        return res

    def _filter_visible_menus(self):
        """ Filter out hidden menus for restricted users during menu load """
        res = super(IrUiMenu, self)._filter_visible_menus()
        user = self.env.user
        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        hidden_menu_ids = profiles.mapped('hide_menu_ids.menu_id.id')
        if hidden_menu_ids:
            res = res.filtered(lambda m: m.id not in hidden_menu_ids)
        return res

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        """ Filter out hidden menus for restricted users """
        res = super(IrUiMenu, self).search(domain, offset=offset, limit=limit, order=order)
        user = self.env.user

        profiles = self.env['access.management'].get_user_access_profiles(user)
        if not profiles:
            return res

        if self.env.su or user._is_superuser() or user.has_group('base.group_system'):
            if not any(p.apply_to_admin for p in profiles):
                return res

        hidden_menu_ids = profiles.mapped('hide_menu_ids.menu_id.id')
        if hidden_menu_ids:
            res = res.filtered(lambda m: m.id not in hidden_menu_ids)

        return res
