// Copyright (c) 2025, Invento Software Limited and contributors
// For license information, please see license.txt


frappe.ui.form.on("Retailer Registration", {
	zone: function (frm) {
		if (frm.doc.zone) {
			frm.set_query("vat_commission_rate", function () {
				return {
					filters: {
						"zone": frm.doc.zone
					}
				};
			});
		}
	},
	vat_commission_rate: function (frm) {
		if (frm.doc.vat_commission_rate && frm.doc.zone) {
			frm.set_query("division", function () {
				return {
					filters: {
						"zone": frm.doc.zone,
						"vat_commission_rate": frm.doc.vat_commission_rate
					}
				};
			});
		}
	},
	division: function (frm) {
		if (frm.doc.division && frm.doc.vat_commission_rate && frm.doc.zone) {
			frm.set_query("circle", function () {
				return {
					filters: {
						"zone": frm.doc.zone,
						"vat_commission_rate": frm.doc.vat_commission_rate,
						'division': frm.doc.division
					}
				};
			});
		}
	},
	nid_document: function (frm) {
		if (frm.doc.nid_document) {
			frappe.call({
				method: "vschallan.vat_challan.doctype.retailer_registration.retailer_registration.upload_file",
				args: {
					file_path: frm.doc.nid_document,
					retailer_id: frm.doc.retailer_id,
					document_category_key: "nid_document"
				},
				callback: function (r) {
					if (r.message) {
						frappe.msgprint("File uploaded successfully");
					}
				}
			});

		}
	}
});

