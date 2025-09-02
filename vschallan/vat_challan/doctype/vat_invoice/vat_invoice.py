# Copyright (c) 2025, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VatInvoice(Document):
	def sync_vat_invoice(self):
		"""Sync VAT Invoice to external system"""
		try:
			# Update status to indicate syncing
			self.status = "Syncing"
			self.save()

			# Here you would implement the actual sync logic
			# For now, we'll just simulate a successful sync
			# Replace this with your actual sync implementation

			# Example sync logic:
			# response = sync_to_external_system(self)

			# Update status to synced
			self.status = "Synced"
			self.save()

			frappe.msgprint("VAT Invoice synced successfully!")

		except Exception as e:
			# Update status to failed
			self.status = "Failed"
			self.save()

			frappe.throw(f"Failed to sync VAT Invoice: {str(e)}")


@frappe.whitelist()
def sync_vat_invoice(vat_invoice_name):
	"""API method to sync VAT Invoice"""
	vat_invoice = frappe.get_doc("Vat Invoice", vat_invoice_name)
	vat_invoice.sync_vat_invoice()
	return {"success": True}
