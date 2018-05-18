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
##############################################################################
import xlsxwriter
import webbrowser
import os
import errno
import urllib
from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta

class RegionWiseReport(models.AbstractModel):
	_name = 'report.rm_assets_report.report_module'



	@api.model
	def render_html(self,docids, data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('rm_assets_report.report_module')
		active_wizard = self.env['rm.assets.report'].search([])
		emp_list = []
		for x in active_wizard:
			emp_list.append(x.id)
		emp_list = emp_list
		emp_list_max = max(emp_list) 

		record_wizard = self.env['rm.assets.report'].search([('id','=',emp_list_max)])

		record_wizard_del = self.env['rm.assets.report'].search([('id','!=',emp_list_max)])
		record_wizard_del.unlink()

		records = self.env['account.asset.asset'].search([('date','>=',record_wizard.form),('date','<=',record_wizard.to)])
		lisst = []
		for x in records:
			if x.category_id.name not in lisst:
				lisst.append(x.category_id.name)



			
		self.sales_annexure(records,lisst,record_wizard)



		docargs = {
			'doc_ids': docids,
			'doc_model': 'account.asset.asset',
			'docs': records,
			'data': data,
			'lisst': lisst,
			}

		return report_obj.render('rm_assets_report.report_module', docargs)

	def sales_annexure(self,records,lisst,record_wizard):
		row = 1
		col = 0

		def get_months(attr):
			month = 0
			for x in records:
				if x.id == attr:
					new = x.date
					d1 = datetime.strptime(record_wizard.to, "%Y-%m-%d")
					d2 = datetime.strptime(new, "%Y-%m-%d")
					days = str((d1 - d2).days)
					month = int(days) / (365/12)

			return str(month)

		def old_dep(attr):
			amt = 0
			for x in records:
				if x.id == attr:
					for y in x.depreciation_line_ids:
						if y.depreciation_date < record_wizard.form:
							amt = amt + y.amount
	
			return amt

		def current_dep(attr):
			value = 0
			for x in records:
				if x.id == attr:
					for y in x.depreciation_line_ids:
						if y.depreciation_date > record_wizard.form and y.depreciation_date <= record_wizard.to:
							value = value + y.amount

			return value


		# def tot_dep(attr):
		# 	value = 0
		# 	amt = 0
		# 	total = 0
		# 	for x in records:
		# 		if x.id == attr:
		# 			for y in x.depreciation_line_ids:
		# 				if y.depreciation_date >= record_wizard.form and y.depreciation_date <= record_wizard.to:
		# 					value = value + y.amount
		# 				if y.depreciation_date < record_wizard.form:
		# 					amt = amt + y.amount
		# 	total = amt + value

		# 	return total

		def gross_dep(attr):
			value = 0
			amt = 0
			total = 0
			gross = 0
			for x in records:
				if x.id == attr:
					for y in x.depreciation_line_ids:
						if y.depreciation_date >= record_wizard.form and y.depreciation_date <= record_wizard.to:
							value = value + y.amount
						if y.depreciation_date < record_wizard.form:
							amt = amt + y.amount
					total = amt + value
					gross = x.value - total

			return gross
		
		workbook = xlsxwriter.Workbook("/home/odoo/odoo-dev/odoo/custom-addons/rm_assets_report/static/src/rm_assets_report.xlsx")
		worksheet = workbook.add_worksheet()

		main_heading = workbook.add_format({
			"bold": 1,
			"align": 'center',
			"valign": 'vcenter',
			"color": 'blue',
			})

		main_head = workbook.add_format({
			"bold": 1,
			"align": 'center',
			"valign": 'vcenter',
			})

		main_date = workbook.add_format({
			"bold": 1,
			"align": 'right',
			"valign": 'vcenter',
			})

		main_data = workbook.add_format({
			"align": 'center',
			"valign": 'vcenter'
			})

		main_cat = workbook.add_format({
			"align": 'left',
			"valign": 'vcenter',
			"color": 'red',
			})


		worksheet.set_column('A:A', 5)
		worksheet.set_column('B:B', 35)
		worksheet.set_column('C:J', 23)
		worksheet.set_column('K:K', 30)
		worksheet.set_column('L:L', 23)
		worksheet.set_column('M:M', 10)
		worksheet.set_column('N:N', 25)
		worksheet.set_column('O:P', 15)
		worksheet.set_row(4, 40)
		worksheet.set_row(0, 25)
		worksheet.write('C1', 'FIXED',main_head)
		worksheet.write('D1', 'ASSET',main_head)
		worksheet.write('E1', 'DEPRECATION',main_head)
		worksheet.write('C2', 'INITIAL DATE',main_head)
		worksheet.write('E2', 'END DATE',main_head)
		worksheet.write('A5', 'QTY',main_heading)
		worksheet.write('B5', 'ASSET',main_heading)
		worksheet.write('C5', 'PURCHASE DATE',main_heading)
		worksheet.write('D5', 'ORIGINAL VALUE',main_heading)
		worksheet.write('E5', 'OLD FACTOR (UFC)',main_heading)
		worksheet.write('F5', 'ACTUAL FACTOR (UFC)',main_heading)
		worksheet.write('G5', 'CHANGE AMOUNT',main_heading)
		worksheet.write('H5', 'UPDATED AMOUNT',main_heading)
		worksheet.write('I5', 'OLD DEPRECATION',main_heading)
		worksheet.write('J5', 'CURRENT DEPRECATION',main_heading)
		worksheet.write('K5', 'TOTAL DEPRECATION',main_heading)
		worksheet.write('L5', 'NET ASSET VALUE',main_heading)
		worksheet.write('M5', '',main_heading)
		worksheet.write('N5', 'DEPRECATION FACTOR',main_heading)
		worksheet.write('O5', 'MONTHS',main_heading)
		worksheet.write_string (row+1, col+2,record_wizard.form,main_data)
		worksheet.write_string (row+1, col+4,record_wizard.to,main_data)

		print lisst
		for line in lisst:
			worksheet.write_string (row+4, col+1,line,main_cat)
			for data in records:
				if data.category_id.name == line:
					worksheet.write_string (row+5, col,'1',main_data)
					worksheet.write_string (row+5, col+1,data.name,main_data)
					worksheet.write_string (row+5, col+2,data.date,main_data)
					worksheet.write_string (row+5, col+3,'{:0,}'.format(int(float(data.value))),main_data)
					worksheet.write_string (row+5, col+4,'-',main_data)
					worksheet.write_string (row+5, col+5,'-',main_data)
					worksheet.write_string (row+5, col+6,'-',main_data)
					worksheet.write_string (row+5, col+7,'{:0,}'.format(int(float(data.value))),main_data)
					worksheet.write_string (row+5, col+8,'{:0,}'.format(int(float(old_dep(data.id)))),main_data)
					worksheet.write_string (row+5, col+9,'{:0,}'.format(int(float(current_dep(data.id)))),main_data)
					worksheet.write_string (row+5, col+10,'{:0,}'.format(int(float(old_dep(data.id)+current_dep(data.id)))),main_data)
					worksheet.write_string (row+5, col+11,'{:0,}'.format(int(float(gross_dep(data.id)))),main_data)
					worksheet.write_string (row+5, col+12,'-',main_data)
					worksheet.write_string (row+5, col+13,'s',main_data)
					worksheet.write_string (row+5, col+14,get_months(data.id),main_data)

					row += 1
			row += 1
		workbook.close()



		# dls = "file:///home/nayyab/customer_invoices.xlsx"
		# urllib.urlretrieve(dls, "%s/static/src/customer_invoices.xlxs" % dir_path[:-8])
		# if  not "%s/static/src/customer_invoices.xlxs" % dir_path[:-8]:
		#     os.system("mv  customer_invoices.xlxs %s/static/src/customer_invoices.xlxs" % dir_path[:-8])

		# url = "customer_invoices.xlsx"
		# webbrowser.open(url)
		# # # created_file = urllib.URLopener()
		# # # created_file.retrieve(url, 'CustomerInvoice.xlsx')
		# urllib.urlretrieve(url, 'CustomerInvoice.xlsx')
		# # # wget.download(url)
		# # print "xxxxxxxxxxxxxxxxxxxxxxxx"



