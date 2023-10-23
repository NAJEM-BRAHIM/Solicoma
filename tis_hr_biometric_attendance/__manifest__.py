# -*- coding: utf-8 -*-
{
    'name': 'Pelagic Pro - ZKteco Biometric Attendance Integration',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'sequence': 1,
    'author': 'Pelagic Pro',
    'summary': 'Biometric attendance integration',
    'description': """
 Synchronization of employee attendance with biometric machine ...""",
    'depends': ['hr_attendance'],
    'data': [
        'data/biometric_data.xml',
        'views/biometric_device_config_view.xml',
        'views/biometric_attnd_log_view.xml',
        'wizard/attendance_calc_wizard_view.xml',
        'wizard/biometric_device_view.xml',
        'wizard/attendance_report_wizard_view.xml',
        'views/hr_attendance_view.xml',
        'views/hr_employee_view.xml',
        'security/ir.model.access.csv',

    ],
    'application': True,
    "license": "LGPL-3",
}
