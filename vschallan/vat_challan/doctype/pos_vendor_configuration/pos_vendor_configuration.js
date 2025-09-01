// Copyright (c) 2025, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("POS Vendor Configuration", {
	refresh: function(frm) {
		frm.add_custom_button("Fetch Token", function() {
			frappe.call({
				method: "vschallan.vat_challan.doctype.pos_vendor_configuration.pos_vendor_configuration.fetch_pos_vendor_token",
				args: {},
				callback: function(r) {
					if (!r.exc) {
						frappe.msgprint("Access token fetched successfully!");
						frm.reload_doc();
					}
				}
			});
		});
	}
});
