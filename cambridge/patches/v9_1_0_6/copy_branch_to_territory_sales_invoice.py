from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql("""update `tabSales Invoice` set territory ='Dubai'""")