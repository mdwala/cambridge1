// Copyright (c) 2016, vivek and contributors
// For license information, please see license.txt


frappe.listview_settings['Class Schedule'] = {
	onload: function(listview) {
		if (!frappe.route_options){ //remove this condition if not required
			frappe.route_options = {
				"schedule_date": ["=", get_today()]
			};
		}
	}
};
