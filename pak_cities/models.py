from odoo import models, fields, api

class AModel(models.Model):
    _name = 'pak.cites'

    name = fields.Char(string='Create City')
    pak_city_code = fields.Integer(string='City Code')


class bingo_inherit(models.Model):
    _inherit='res.partner'
    city = fields.Many2one('pak.cites','City')
    mobile = fields.Char('Mobile')
    _sql_constraints = [
    ('mobile_unique', 'unique(mobile)', 'This Mobile number already exists!')
]
