# -*- coding: utf-8 -*-
{
    'name': "arian_manufacturing",

    'summary': """
        Manufacturing Extension""",

    'description': """
        Manufacturing Extension
    """,

    'author': "Enterprise Cube (Pvt) Limited",
    'website': "http://ecube.pk",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','mrp','manufaturing_extension'],

    # always loaded
    'data': [
        'views/lots.xml','views/work_order.xml','views/manufacturing_order.xml'
    ],
}
