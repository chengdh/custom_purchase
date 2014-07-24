# -*- coding: utf-8 -*-

{
    'name': 'custom purchase',
    'version': '0.1',
    'category': 'Purchase Management',
    'description': """定制修改purchase的功能""",
    'author': 'chengdh (cheng.donghui@gmail.com)',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['purchase','custom_hr_expense'],
    'init_xml': [],
    'update_xml': [
      'security/purchase_secure.xml',
      'security/ir.rules.xml',
      'purchase_view.xml',
      'purchase_workflow.xml','report.xml'],
    'demo_xml': [],
    'active': False,
    'installable': True,
    'web':True,
    'css': [],
    'js': [],
}

