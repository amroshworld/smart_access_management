# -*- coding: utf-8 -*-
{
    'name': 'Smart Access Security (Enterprise Security Suite)',
    'version': '19.0.1.0.0',
    'category': 'Administration/Security',
    'summary': 'Modern SaaS-Style Security Profile Manager, Menu Hiding, Model & Field Rules, System Safeguards',
    'description': """
Smart Access Security & Permissions Suite (Enterprise Edition)
==============================================================
A sleek, highly intuitive, and enterprise-grade security profile manager for Odoo 19.

Key Features & Business Benefits:
----------------------------------
* 🛡️ **Global System Safeguards**: One-click Read-Only mode, Developer Mode block (?debug=1), Login suspension, Module Installation block, and XML-RPC API access block.
* 🎯 **Target Scope & User Assignment**: Easily assign security profiles across targeted users and multi-company environments.
* 🙈 **Visual Menu Visibility**: Hide top menus, submenus, and action items effortlessly.
* 🔒 **Model Level Access Rights**: Granular permissions for Read, Create, Edit, Delete, Archive, Export, Import, Kanban, List, Pivot, Graph views.
* ✏️ **Field Access Control**: Set fields as Invisible, Read-Only, or Required per profile.
* 🔘 **Button & Tab Restrictions**: Hide specific header buttons, stat buttons, or notebook tabs.
* 💬 **Chatter Controls**: Restrict send message, log notes, activities, or hide chatter completely.
* 📜 **Audit Trail Logging**: Complete event tracking of security profile changes.
* ⚡ **Batch Configurator Wizard**: Apply rules across multiple models in seconds.
    """,
    'author': 'Smart ERP Solutions',
    'website': 'https://apps.odoo.com',
    'license': 'OPL-1',
    'price': 99.00,
    'currency': 'EUR',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/preset_templates.xml',
        'wizards/access_wizard_views.xml',
        'views/access_management_views.xml',
        'views/res_users_views.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_access_security/static/src/scss/access_management.scss',
            'smart_access_security/static/src/js/dev_mode_guard.js',
        ],
    },
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
