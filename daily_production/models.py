# -*- coding: utf-8 -*-

from openerp import models, fields, api

class DailyForm(models.Model):
    _name = 'daily.production'

    date = fields.Date(string="Date",required=True)
    daily_id = fields.One2many('daily.production.tree','daily_tree')
    daily_consump = fields.One2many('daily.consumption.tree','daily_tree_consume')


class DailyFormTree(models.Model):
    _name = 'daily.production.tree'

    product = fields.Many2one('product.product',string="Product",required=True)
    qty_kg = fields.Float(string="Qunatity(Kg)",default=1.00)
    rate = fields.Float(string="Consumption Rate")
    qty_lit = fields.Float(string="Qunatity(Litre)",default=1.00)
    date = fields.Date(string="Date")
    daily_tree = fields.Many2one('daily.production')

    @api.onchange('product')
    def get_date(self):
        if self.product:
            self.date = self.daily_tree.date


class DailyConsumeTree(models.Model):
    _name = 'daily.consumption.tree'

    product = fields.Many2one('product.product',string="Product",required=True)
    qty = fields.Float(string="Qunatity",default=1.00)
    date = fields.Date(string="Date")
    daily_tree_consume = fields.Many2one('daily.production')

    @api.onchange('product')
    def get_dated(self):
        if self.product:
            self.date = self.daily_tree_consume.date
