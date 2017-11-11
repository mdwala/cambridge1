from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql("""update tabAppointments set territory ='Dubai'""")