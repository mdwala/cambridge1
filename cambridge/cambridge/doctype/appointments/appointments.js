// Copyright (c) 2016, vivek and contributors
// For license information, please see license.txt
frappe.ui.form.on("Appointments", "onload", function(frm){

	if (frm.doc.from_datetime && frm.doc.to_datetime) {
		var from_datetime = moment(frm.doc.from_datetime);
		var to_datetime = moment(frm.doc.to_datetime);
		frm.doc.schedule_date = from_datetime.format(moment.defaultFormat);
		frm.doc.time = from_datetime.format("HH:mm:ss");
		frm.doc.to_time = to_datetime.format("HH:mm:ss");
	}
	cur_frm.set_query("class_slot", function(){
		return {
			"filters": [
				["schedule_date", ">=", frm.doc.date],
        		["occupancy", ">", 0]
			]
		}
	});
});
