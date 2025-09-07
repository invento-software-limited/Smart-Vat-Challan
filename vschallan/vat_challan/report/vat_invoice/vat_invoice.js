// Copyright (c) 2025, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.query_reports["VAT Invoice"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": 100,
            "default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": 100,
            "default": frappe.datetime.get_today()
		},
		{
			"fieldname": "invoice_number",
			"label": __("Invoice Number"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nPending\nSynced\nFailed",
			"width": 100
		},
	],
	get_datatable_options(options) {
		delete options['cellHeight'];
		return Object.assign(options, {
			cellHeight: 40
		});

	},
	"onload": function (report) {
		window.syncVatInvoice = function (vat_invoice_name) {
			frappe.call({
				method: "vschallan.vat_challan.doctype.vat_invoice.vat_invoice.sync_vat_invoice",
				args: {
					vat_invoice_name: vat_invoice_name
				},
				callback: function (r) {
					if (r.exc) {
						frappe.msgprint({
							title: __("Error"),
							message: __("Failed to sync VAT Invoice: ") + r.exc,
							indicator: "red"
						});
					} else {
						frappe.msgprint({
							title: __("Success"),
							message: __("VAT Invoice synced successfully!"),
							indicator: "green"
						});
						// Refresh the report
						report.refresh();
					}
				}
			});
		};
	}
};
