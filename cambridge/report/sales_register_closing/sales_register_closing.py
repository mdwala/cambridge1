# Copyright (c) 2013, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.utils import get_fullname
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = frappe._dict({})

	invoice_list = get_invoices(filters)
	columns, income_accounts, payment_accounts = get_columns(invoice_list)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_income_map = get_invoice_income_map(invoice_list)
	invoice_income_map, invoice_tax_map = get_invoice_tax_map(invoice_list,
		invoice_income_map, income_accounts)

	invoice_so_dn_map = get_invoice_so_dn_map(invoice_list)
	customer_map = get_customer_details(invoice_list)
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])
	frappe.errprint(mode_of_payments)

	data = []
	for inv in invoice_list:
		# invoice details
		sales_order = list(set(invoice_so_dn_map.get(inv.name, {}).get("sales_order", [])))
		delivery_note = list(set(invoice_so_dn_map.get(inv.name, {}).get("delivery_note", [])))

		row = [inv.name, inv.posting_date, inv.customer,
		customer_map.get(inv.customer, {}).get("registration")]

		if mode_of_payments.get(inv.name, 0):
			row += [mode_of_payments[inv.name].get('Cash', 0), mode_of_payments[inv.name].get('Credit Card', 0)]
		else:
			row += [0, 0]



		row += [inv.base_grand_total]
		row += [inv.discount_amount]
		# map income values
		base_net_total = 0
		for income_acc in income_accounts:
			income_amount = flt(invoice_income_map.get(inv.name, {}).get(income_acc))

			base_net_total += income_amount
			row.append(income_amount)

		# cash / credit cambridge



		# tax account


		# total tax, grand total, outstanding amount & rounded total

		row += [get_fullname(inv.owner)]


		data.append(row)

	return columns, data


def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Sales Invoice:120", _("Posting Date") + ":Date:80",
		_("Customer Name") + "::120",
		_("Registration") + ":Link/Registration:120",

	]

	income_accounts = payment_accounts = income_columns = pay_columns = []

	if invoice_list:
		income_accounts = frappe.db.sql_list("""select distinct income_account
			from `tabSales Invoice Item` where docstatus = 1 and parent in (%s)
			order by income_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		payment_accounts = 	frappe.db.sql_list("""select distinct mode_of_payment
			from `tabSales Invoice Payment` where parenttype = 'Sales Invoice'
			and docstatus = 1 and parent in (%s) order by mode_of_payment""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

	income_columns = [(account + ":Currency/currency:120") for account in income_accounts]
	pay_columns = [(payment + ":Currency/currency:120") for payment in payment_accounts]


	columns = columns + pay_columns + [ _("Grand Total") + ":Currency/currency:120"] + [ _("Discount") + ":Currency/currency:120"]  + income_columns +  [ _("Created By") + ":Link/User:120"]

	return columns, income_accounts, payment_accounts

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"
	if filters.get("user"): conditions += " and owner = %(user)s"

	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"


	if filters.get("mode_of_payment"):
		conditions += """ and exists(select name from `tabSales Invoice Payment`
			 where parent=`tabSales Invoice`.name
			 	and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = %(mode_of_payment)s)"""

	return conditions

def get_invoices(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date, debit_to, customer, remarks,
		base_net_total, base_grand_total, base_rounded_total, outstanding_amount, discount_amount, owner
		from `tabSales Invoice`
		where docstatus = 1 %s order by posting_date desc, name asc""" %
		conditions, filters, as_dict=1)

def get_invoice_income_map(invoice_list):
	income_details = frappe.db.sql("""select parent, income_account, sum(base_net_amount) as amount
		from `tabSales Invoice Item` where parent in (%s) group by parent, income_account""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_income_map = {}
	for d in income_details:
		invoice_income_map.setdefault(d.parent, frappe._dict()).setdefault(d.income_account, [])
		invoice_income_map[d.parent][d.income_account] = flt(d.amount)

	return invoice_income_map

def get_invoice_tax_map(invoice_list, invoice_income_map, income_accounts):
	tax_details = frappe.db.sql("""select parent, account_head,
		sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabSales Taxes and Charges` where parent in (%s) group by parent, account_head""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in income_accounts:
			if invoice_income_map[d.parent].has_key(d.account_head):
				invoice_income_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_income_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_income_map, invoice_tax_map

def get_invoice_so_dn_map(invoice_list):
	si_items = frappe.db.sql("""select parent, sales_order, delivery_note, so_detail
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(sales_order, '') != '' or ifnull(delivery_note, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_so_dn_map = {}
	for d in si_items:
		if d.sales_order:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault(
				"sales_order", []).append(d.sales_order)

		delivery_note_list = None
		if d.delivery_note:
			delivery_note_list = [d.delivery_note]
		elif d.sales_order:
			delivery_note_list = frappe.db.sql_list("""select distinct parent from `tabDelivery Note Item`
				where docstatus=1 and so_detail=%s""", d.so_detail)

		if delivery_note_list:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault("delivery_note", delivery_note_list)

	return invoice_so_dn_map

def get_customer_details(invoice_list):
	customer_map = {}
	customers = list(set([inv.customer for inv in invoice_list]))
	for cust in frappe.db.sql("""select name, registration, customer_group from `tabCustomer`
		where name in (%s)""" % ", ".join(["%s"]*len(customers)), tuple(customers), as_dict=1):
			customer_map.setdefault(cust.name, cust)

	return customer_map


def get_mode_of_payments(invoice_list):
	mode_of_payments = {}
	if invoice_list:
		inv_mop = frappe.db.sql("""select parent, mode_of_payment, amount
			from `tabSales Invoice Payment` where parent in (%s) group by parent, mode_of_payment""" %
			', '.join(['%s']*len(invoice_list)), tuple(invoice_list), as_dict=1)

		for d in inv_mop:
			mode_of_payments.setdefault(d.parent, {}).update({d.mode_of_payment:d.amount})

	return mode_of_payments
