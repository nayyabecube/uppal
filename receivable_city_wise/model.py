#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from openerp import models, fields, api
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import time

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.receivable_city_wise.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('receivable_city_wise.customer_report')
        active_wizard = self.env['city.wise'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['city.wise'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['city.wise'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()
        date = record_wizard.date

        journal_cust = []
        rec = self.env['account.move.line'].search([('date','>',record_wizard.date)])
        for x in rec:
            if x.partner_id:
                if x.partner_id.id not in journal_cust:
                    journal_cust.append(x.partner_id.id)

        print journal_cust


        city = []
        records = self.env['res.partner'].search([])
        for z in records:
            if z.city:
                if z.city not in city:
                    city.append(z.city)


        cust = []
        def get_cust(attr):
            del cust[:]
            for z in journal_cust:
                for x in records:
                    if x.id == z:
                        if x.city.id == attr:
                            cust.append(x)


        def get_bal(attr):
            value = 0
            for y in records:
                if y.id == attr:
                    value = y.credit - y.debit

            return value


        
        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'city': city,
            'cust': cust,
            'get_cust': get_cust,
            'get_bal': get_bal,
    

            }

        return report_obj.render('receivable_city_wise.customer_report', docargs)