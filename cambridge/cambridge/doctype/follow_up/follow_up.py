# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate

class Followup(Document):

	def validate(self):
		self.input_values()
		self.calculate_actual_weight_loss()
		self.calculate_suggested_weight_loss()
		self.calculate_difference()


	def input_values(self):
		self.calorie_intake = frappe.db.get_value("Diet Plan", self.diet_plan, "intake")
		self.physical_activity = frappe.db.get_value("Registration", self.registration, "y21")
		self.pratio = frappe.db.get_value("Physical Activity", self.physical_activity, "ratio")
		self.no_of_days = (frappe.utils.data.getdate(self.date) - frappe.utils.data.getdate(self.last_followup_date)).days

	def calculate_actual_weight_loss(self):
		self.actual_weight_loss = flt(self.previous_weight) - flt(self.current_kg)

	def calculate_suggested_weight_loss(self):
		if self.age and self.height:
			if self.sex == "Male":
					self.bmr = (10 * self.current_kg) + (6.25 * float(self.height)) + (5 * float(self.age)) + 5;
			if self.sex == "Female":
					self.bmr = (10 * self.current_kg) + (6.25 * float(self.height)) + (5 * float(self.age)) - 161;

			self.suggested_weight_loss = (((flt(self.bmr) * flt(self.pratio)) - flt(self.calorie_intake)) / 1000) * (flt(self.no_of_days) / 7)

	def calculate_difference(self):
		if (self.height and self.current_kg) > 0:
			self.difference = flt(self.suggested_weight_loss) - flt(self.actual_weight_loss)
			hs = (float(self.height) * float(self.height)) * 0.0001
			self.current_bmi = float(self.current_kg) / hs

@frappe.whitelist()
def get_last_follow_up(frm):
	list = frappe.db.sql("""select current_kg, date, diet_plan from `tabFollow up` where registration=%s order by date desc limit 2""", frm)
	return list


@frappe.whitelist()
def get_all_follow_up(frm):
	list = frappe.db.sql("""select name, date, current_kg, comments from `tabFollow up` where registration=%s order by date desc""", frm)
	return list
