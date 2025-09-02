# Copyright (c) 2025, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"fieldname": "name",
			"label": _("VAT Invoice Number"),
			"fieldtype": "Link",
			"options": "Vat Invoice",
			"width": 150
		},
		{
			"fieldname": "invoice_number",
			"label": _("Invoice Number"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "invoice_date",
			"label": _("Invoice Date"),
			"fieldtype": "Datetime",
			"width": 130
		},
		{
			"fieldname": "order_id",
			"label": _("Order ID"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "sync_now",
			"label": _("Sync Now"),
			"fieldtype": "Button",
			"width": 100
		},
		{
			"fieldname": "download_schallan",
			"label": _("Download Schallan"),
			"fieldtype": "Button",
			"width": 160
		}
	]
	return columns


def get_data(filters):
	# Build filter conditions
	filter_conditions = {}

	if filters.get("invoice_number"):
		filter_conditions["invoice_number"] = ["like", f"%{filters.invoice_number}%"]

	if filters.get("order_id"):
		filter_conditions["order_id"] = ["like", f"%{filters.order_id}%"]

	if filters.get("status"):
		filter_conditions["status"] = filters.status

	if filters.get("from_date") and filters.get("to_date"):
		filter_conditions["invoice_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.get("from_date"):
		filter_conditions["invoice_date"] = [">=", filters.from_date]
	elif filters.get("to_date"):
		filter_conditions["invoice_date"] = ["<=", filters.to_date]

	data = frappe.get_all(
		"Vat Invoice",
		fields=["name", "invoice_number", "invoice_date", "order_id", "status"],
		filters=filter_conditions,
		order_by="creation desc"
	)

	# Add sync_now button for each row
	for row in data:
		row["sync_now"] = f"<button class='btn btn-xs btn-primary' onclick='syncVatInvoice(\"{row.name}\")'>Sync Now</button>"
		row["download_schallan"] = f"<button class='btn btn-xs btn-primary' onclick='syncVatInvoice(\"{row.name}\")'>Download Schallan</button>"

	return data
