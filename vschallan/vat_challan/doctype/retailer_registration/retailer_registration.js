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
	}
});

