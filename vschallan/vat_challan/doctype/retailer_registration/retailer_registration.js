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
		submit_document(frm.doc.nid_document, frm.doc.retailer_id, "nid_document");
	},
	bin_document: function (frm){
		submit_document(frm.doc.bin_document, frm.doc.retailer_id, "business_identification_number");
	},
	trade_document: function (frm){
		submit_document(frm.doc.trade_document, frm.doc.retailer_id, "trade_license");
	},
	tin_document: function (frm){
		submit_document(frm.doc.tin_document, frm.doc.retailer_id, "tax_identification");
	}
});

function submit_document(file_path, retailer_id, document_category_key) {
	if (file_path) {
		frappe.call({
			method: "vschallan.vat_challan.doctype.retailer_registration.retailer_registration.upload_file",
			args: {
				file_path: file_path,
				retailer_id: retailer_id,
				document_category_key: document_category_key
			},
			callback: function (r) {
				// if (r.message) {
				// 	frappe.msgprint(`${r.message.message}: ${r.message.file_url}`);
				// }
			}
		});

	}
}

