// Copyright (c) 2016, vivek and contributors
// For license information, please see license.txt

frappe.ui.form.on('Follow up', {
	refresh: function(frm) {



	}
});


frappe.ui.form.on("Follow up", "registration", function(frm, doctype, name) {



					frappe.call({
 			     'method': "cambridge.cambridge.doctype.follow_up.follow_up.get_all_follow_up",
 			     'args': {
 			       "frm" : frm.doc.registration,
 			     },
 			     'callback': function(res){

 			         var template = "<table class=\"table\"> <tbody> <tr> <th>Series</th> <th>Date</th> <th>Current Weight</th><th>Comment</th></tr> {% for row in rows %} <tr><td>{{row[0]}}</td><td>{{ moment(row[1]).format('DD-MM-YY') }}</td><td>{{row[2]}}</td><td>{{row[3]}}</td></tr> {% endfor %}</tbody></table>";
 			        frm.set_df_property('old_table', 'options', frappe.render(template, {rows: res.message}));
 			        frm.refresh_field('old_table');
 			     }
 			   });

				 frm.doc.consultant = frappe.session.user;
				 frm.doc.consultant_name = frappe.user_info().fullname;
				 console.log(frappe.session.user);
				 frm.refresh_field('consultant');
				 frm.refresh_field('consultant_name');


			});
