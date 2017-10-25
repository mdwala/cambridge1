# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr, flt, getdate, validate_email_add, today, add_years
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, validate_email_add, today, add_years
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils import flt, get_datetime, format_datetime

class Registration(Document):
	def validate(self):
		pass



	def referral(self):
		if self.referred_by !=None:
			ref = frappe.new_doc("Referral")
			ref.customer = self.referred_by
			ref.date = self.registration_date
			ref.registration = self.name
			ref.status = "To Pay"
			ref.save()

	def disable_customer(self):
		if self.customer and self.status=="On Hold":
			cust = frappe.get_doc("Customer", self.customer)
			cust.disabled = 1
			cust.save()

	def enable_customer(self):
		if (self.status!="On Hold" and self.registration_payment=="Complete"):
			cust = frappe.get_doc("Customer", self.customer)
			cust.disabled = 0
			cust.save()



@frappe.whitelist()
def make_appointment(frm):
    appointment = get_mapped_doc("Registration", frm, 	{
		"Registration": {
			"doctype": "Appointments"
			}
		  })
    return appointment



@frappe.whitelist()
def delete_registration():
	frappe.db.sql('delete from tabRegistration')


@frappe.whitelist()
def make_customer(frm):
	reg = frappe.get_doc("Registration", frm)
	if reg.registration_partner:
		ref = frappe.get_doc("Registration", reg.registration_partner)
		ref.registration_payment = "Complete"
		ref.status = "Active"
		ref.save()
		cust = frappe.new_doc("Customer")
		cust.first_name = ref.first_name
		cust.last_name = ref.last_name
		#cust.customer_name = str(ref.first_name) + ' ' + str(ref.last_name)
		cust.customer_name = str(ref.customer_name)
		cust.customer_group = "Individual"
		cust.customer_type = "Individual"
		cust.territory = ref.emirates
		cust.telephone_no = ref.telephone_no
		cust.height = ref.height
		cust.weight = ref.weight
		cust.registration = frm
		cust.insert()
		rlist = []
		rlist.append(ref.telephone_no)
		send_sms(rlist, "You have been registered successfully as " + test.registration +  " for Cambridge Diet Plan", "Cambridge")

	test = frappe.new_doc("Customer")
	test.first_name = reg.first_name
	test.last_name = reg.last_name
	#test.customer_name = str(reg.first_name) + ' ' + str(reg.last_name)
	test.customer_name = str(reg.customer_name)
	test.customer_group = "Individual"
	test.customer_type = "Individual"
	test.territory = reg.emirates
	test.sex = reg.sex
	test.age = reg.age
	test.telephone_no = reg.telephone_no
	test.height = reg.height
	test.weight = reg.weight
	test.registration = frm
	test.insert()
	rlist = []
	rlist.append(reg.telephone_no)
	send_sms(rlist, "You have been registered successfully as " + test.registration +  " for Cambridge Diet Plan", "Cambridge")
	if reg.registration_payment == "Free":
		reg.registration_payment = "Complete"
		reg.save()
		return test
	if reg.registration_payment	== "Pending":
		si = frappe.new_doc("Sales Invoice")
		si.customer = test.name
		si.is_pos = 1
		si.is_registration = 1
		si.debit_to = "Registrations - CHFDXB"
		si.append("items", {
		"item_code": "SIRG",
		"qty": 1,
		"income_account": "Registrations - CHFDXB"
		})
		si.set_missing_values()
		return si


#@frappe.whitelist()
#def on_hold(frm, reg):
#	cust = frappe.get_doc("Customer", frm)	cust.disabled = 1
#	cust.save()


#@frappe.whitelist()
#def un_hold(frm, reg):
#	reg = frappe.get_doc("Registration", reg)
#	if reg.registration_payment=="Complete":
#		reg.status="Active"
#		cust = frappe.get_doc("Customer", frm)
#		cust.disabled = 0
#		cust.save()
#	else:
#		reg.status="Draft"
#	reg.save()
#	return cust





@frappe.whitelist()
def validate_mobile(frm):
	list = frappe.get_all('Registration', filters={'telephone_no':frm}, fields=['first_name', 'last_name', 'telephone_no'])
	return list

@frappe.whitelist()
def validate_name(first_name, last_name):
	list = frappe.get_all('Registration', filters={'first_name':first_name, 'last_name':last_name}, fields=['first_name', 'last_name', 'telephone_no'])
	return list
