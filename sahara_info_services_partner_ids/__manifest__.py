# -*- coding: utf-8 -*-
{
    'name': "Sahara Info Services - Partner IDs",
    'summary': "Agrega campos ICE, NIF y RC en la ficha de partners con control de unicidad",
    'description': """
Partner IDs - Sahara Info Services
===================================

Este módulo agrega campos de identificación fiscal a la ficha de partners (res.partner):

- **ICE** (Identifiant Commun de l'Entreprise)
- **NIF** (Numéro d'Identification Fiscale)
- **RC** (Registre de Commerce)

Cada campo tiene una restricción de unicidad (SQL constraint) para evitar duplicados.
    """,
    'author': "Sahara Info Services",
    'category': 'Sales/CRM',
    'version': '19.0.1.0.1',
    'license': 'LGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'views/res_partner_views.xml',
        'reports/report_invoice_partner_ids.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
