# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

class AccessButton(models.Model):
    _name = 'access.button'
    _description = 'Button & Notebook Tab Restrictions'

    access_management_id = fields.Many2one('access.management', string='Access Profile', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Technical Name', store=True)

    button_selection = fields.Selection(
        selection='_get_button_selection',
        string='🔍 Select Button / Tab'
    )

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

    @api.model
    def _get_button_selection(self):
        """ Dynamically extract all buttons and notebook tabs from form views of the selected target model """
        model_id = self.env.context.get('default_model_id') or self.model_id.id
        if not model_id and self._context.get('active_model_id'):
            model_id = self._context.get('active_model_id')

        if not model_id:
            return [('none', _('-- Select Target Model First --'))]

        model_rec = self.env['ir.model'].browse(model_id)
        if not model_rec.exists():
            return [('none', _('-- Select Target Model First --'))]

        views = self.env['ir.ui.view'].search([('model', '=', model_rec.model), ('type', '=', 'form')])
        selection = []
        seen = set()

        for v in views:
            arch = v.arch
            if arch:
                try:
                    tree = etree.fromstring(arch.encode('utf-8'))
                    for btn in tree.xpath('//button'):
                        name = btn.get('name') or btn.get('string') or btn.get('class')
                        string = btn.get('string') or btn.get('name') or name
                        if name and name not in seen:
                            seen.add(name)
                            selection.append((f"btn:{name}", f"🔘 Button: {string} ({name})"))
                    for page in tree.xpath('//page'):
                        name = page.get('name') or page.get('string')
                        string = page.get('string') or page.get('name') or name
                        if name and name not in seen:
                            seen.add(name)
                            selection.append((f"tab:{name}", f"📑 Tab: {string} ({name})"))
                except Exception:
                    pass

        if not selection:
            return [('none', _('No buttons/tabs automatically found. Please enter identifier manually below.'))]

        return selection

    @api.onchange('model_id')
    def _onchange_model_id_reset_selection(self):
        self.button_selection = False

    @api.onchange('button_selection')
    def _onchange_button_selection(self):
        """ Auto-populate button_name, button_type, and title when selecting an item from the dropdown """
        if self.button_selection and self.button_selection != 'none':
            if ':' in self.button_selection:
                elem_type, identifier = self.button_selection.split(':', 1)
                self.button_name = identifier
                if elem_type == 'btn':
                    self.button_type = 'button'
                    self.title = _("Hide Button: %s") % identifier
                elif elem_type == 'tab':
                    self.button_type = 'tab'
                    self.title = _("Hide Tab: %s") % identifier

    @api.constrains('model_id', 'button_name')
    def _check_button_fields(self):
        for rec in self:
            if not rec.model_id or not rec.button_name:
                raise ValidationError(_("Please select a 'Target Model' and specify a 'Technical Identifier' for all entries in the Buttons & Tabs list."))
