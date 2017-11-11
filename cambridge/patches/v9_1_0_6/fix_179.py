from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql("""update `tabSales Invoice Item` set income_account = 'Registrations - CHFDXB' where item_code = 'SIRG' and income_account = 'Sales - CHFDXB'""")