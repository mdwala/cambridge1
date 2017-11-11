from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql("""delete from `tabCustom Field` where dt in ('Follow up', 'Appointments', 'Registration')""")