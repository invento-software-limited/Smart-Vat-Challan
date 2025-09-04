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
		},
		{
			"fieldname": "name",
			"label": _("VAT Invoice Number"),
			"fieldtype": "Link",
			"options": "VAT Invoice",
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
			"fieldname": "customer_id",
			"label": _("Customer ID"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "retailer_id",
			"label": _("Retailer ID"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "txn_amount",
			"label": _("Transaction Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_sd_percentage",
			"label": _("SD %"),
			"fieldtype": "Percent",
			"width": 90
		},
		{
			"fieldname": "total_sd_amount",
			"label": _("SD Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "total_discount_amount",
			"label": _("Discount Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "total_service_charges_amount",
			"label": _("Service Charges"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "payment_method",
			"label": _("Payment Method"),
			"fieldtype": "Data",
			"width": 120
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
		}
	]
	return columns


def get_data(filters):
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
		"VAT Invoice",
		fields=[
			"name",
			"invoice_number",
			"invoice_date",
			"customer_id",
			"retailer_id",
			"txn_amount",
			"total_sd_percentage",
			"total_sd_amount",
			"total_discount_amount",
			"total_service_charges_amount",
			"total_amount",
			"payment_method",
			"order_id",
			"status"
		],
		filters=filter_conditions,
		order_by="creation desc"
	)

	for row in data:
		row["sync_now"] = f"<button class='btn btn-xs btn-primary' onclick='syncVatInvoice(\"{row.name}\")'>Sync Now</button>"
		row["download_schallan"] = f"<button class='btn btn-xs btn-primary' onclick='downloadVatChallan(\"{row.name}\")'>Download Schallan</button>"

	return data
