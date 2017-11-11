from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql("""update `tabFollow up` set territory ='Dubai'""")