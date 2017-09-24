# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, format_datetime
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms

class Appointments(Document):
	def validate(self):
		cs = frappe.get_doc("Class Schedule", self.class_slot)
		if self.booked == "No":
			if self.status == "Seat Reserved":
				cs.occupancy = cs.occupancy - 1
				self.booked = "Yes"
		if self.booked == "Yes":
			if self.status == "Cancel":
				cs.occupancy = cs.occupancy + 1
				self.booked = "No"
		cs.title =  str(cs.from_time) + ' / R: ' + str(cs.occupancy)
		cs.class_title = str(cs.from_time) + '/' + str(cs.session_type) + '/' + str(cs.language) + '/ R: ' + str(cs.occupancy)
		cs.save()

		if self.registration:
			reg = frappe.get_doc("Registration", self.registration)
			reg.status = "Appointed"
			rlist = []
			rlist.append(reg.telephone_no)
			send_sms(rlist, "Appointment fixed for " + self.schedule_date + " at " + self.time  , "Cambridge")
			reg.appointment_status = self.status
			reg.save()


	def after_insert(self):
		reg = frappe.get_doc("Registration", self.registration)
		reg.appointment = self.name
		reg.save()
		if self.status == "Seat Confirmed":
			todo = frappe.new_doc("ToDo")
			todo.description = "Call: " + self.first_name + "on " + str(self.telephone_no)
			todo.call_back = "Yes"
			todo.reference_type = "Appointments"
			todo.reference_name = self.name
			todo.owner = self.owner
			todo.date = get_datetime(self.schedule_date) - datetime.timedelta(days= 1)
			todo.save()


@frappe.whitelist()
def get_appointment_schedule_events(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Appointments", filters)

	data = frappe.db.sql("""select name,
			timestamp(schedule_date, time) as from_datetime,
			timestamp(schedule_date, to_time) as to_datetime,
			CONCAT_WS(' ',first_name,last_name,telephone_no,lanugage) as language, 0 as 'allDay'
		from `tabAppointments`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(conditions=conditions), {
			"start": start,
			"end": end
			}, as_dict=True, update={"allDay": 0})

	return data
