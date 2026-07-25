{
    'name': 'Solicoma - Grupos de Usuarios',
    'summary': 'Grupo Solo Lectura para acceso de auditoría',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/groups.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
