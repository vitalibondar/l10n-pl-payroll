{
    "name": "Poland - Payroll",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Polish payroll calculation and pay slip generation",
    "description": """
        Calculates gross-to-net salary for Polish employees.
        Supports umowa o pracę and umowa zlecenie.
        Generates pay slips (pasek wynagrodzeń).
    """,
    "author": "Om Energy Solutions",
    "website": "https://omenergysolutions.pl",
    "license": "LGPL-3",
    "depends": ["hr_contract", "hr_attendance"],
    "data": [
        "security/pl_payroll_security.xml",
        "security/ir.model.access.csv",
        "data/pl_payroll_parameters_2025.xml",
        "data/pl_payroll_parameters_2026.xml",
        "report/pl_payroll_payslip_report.xml",
        "report/pl_payroll_payslip_template.xml",
        "views/pl_payroll_payslip_views.xml",
        "views/pl_payroll_parameter_views.xml",
        "views/pl_payroll_compute_wizard_views.xml",
        "views/pl_payroll_menus.xml",
    ],
    "demo": [
        "data/demo/pl_payroll_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
