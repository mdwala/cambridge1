frappe.views.calendar["Appointments"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_datetime",
		"end": "to_datetime",
		"id": "name",
		"title": "language",
		"allDay": "allDay"
	},
	gantt: false,
	textColor: 'black',
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "registration",
			"options": "Registration",
			"label": __("Registration")
		},
		{
			"fieldtype": "Link",
			"fieldname": "class-schedule",
			"options": "Class Schedule",
			"label": __("Class")
		}
	],
	get_events_method: "cambridge.cambridge.doctype.appointments.appointments.get_appointment_schedule_events"
}
