// Copyright (c) 2016, vivek and contributors
// For license information, please see license.txt



frappe.ui.form.on('Class Schedule', {
	validate: function(frm) {
		frm.doc.class_title = moment(frm.doc.schedule_date + 'T' + frm.doc.from_time).format('MMM:Do, hh:mm a') + "/" + frm.doc.session_type + "/" + frm.doc.language + "/ R: " + frm.doc.occupancy;
		frm.doc.title = frm.doc.session_type + "/ R: " + frm.doc.occupancy;

	}
});

frappe.ui.form.on("Class Schedule", "birth_date", function(frm, doctype, name) {
  var v1 = 0;
  v1 = frappe.datetime.get_diff(frappe.datetime.get_today(), frm.doc.birth_date);
  frm.doc.age = Math.floor((v1).toFixed(2) / 365.25);
  refresh_field("age");
});


frappe.ui.form.on("Class Schedule", "max_occupancy", function(frm, doctype, name) {

  frm.doc.occupancy = frm.doc.max_occupancy;
	frm.doc.class_title = frm.doc.max_occupancy;
  refresh_field("occupancy");
	refresh_field("class_title");
});
