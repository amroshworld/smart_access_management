# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccessConfigWizard(models.TransientModel):
    _name = 'access.config.wizard'
    _description = 'Quick Security Rule Configurator Wizard'

    access_management_id = fields.Many2one('access.management', string='Access Profile', required=True, ondelete='cascade')
    model_ids = fields.Many2many('ir.model', string='Select Models', required=True)

    # Model Level Toggles
    perm_read = fields.Boolean(string='Allow Read', default=True)
    perm_create = fields.Boolean(string='Allow Create', default=True)
    perm_write = fields.Boolean(string='Allow Edit', default=True)
    perm_unlink = fields.Boolean(string='Allow Delete', default=True)
    perm_export = fields.Boolean(string='Allow Export', default=True)
    perm_import = fields.Boolean(string='Allow Import', default=True)

    def action_apply_quick_rules(self):
        """ Batch create access.model rules for all selected models """
        self.ensure_one()
        AccessModel = self.env['access.model']
        for model in self.model_ids:
            existing = AccessModel.search([
                ('access_management_id', '=', self.access_management_id.id),
                ('model_id', '=', model.id)
            ], limit=1)
            vals = {
                'access_management_id': self.access_management_id.id,
                'model_id': model.id,
                'perm_read': self.perm_read,
                'perm_create': self.perm_create,
                'perm_write': self.perm_write,
                'perm_unlink': self.perm_unlink,
                'perm_export': self.perm_export,
                'perm_import': self.perm_import,
            }
            if existing:
                existing.write(vals)
            else:
                AccessModel.create(vals)

        # Log audit entry
        self.env['access.audit.log'].create({
            'access_management_id': self.access_management_id.id,
            'action_type': 'update',
            'details': f"Quick Configurator applied rules for {len(self.model_ids)} models."
        })
        return {'type': 'ir.actions.act_window_close'}
