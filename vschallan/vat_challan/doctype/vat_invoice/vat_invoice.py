# Copyright (c) 2025, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from vschallan.vschallan import VATSmartChallan


class VATInvoice(Document):
	def after_insert(self):
		self.sync_vat_invoice()

	def sync_vat_invoice(self):
		"""Sync VAT Invoice to external system"""
		vschallan = VATSmartChallan()
		vschallan.sync_vat_invoice(self)


@frappe.whitelist()
def sync_vat_invoice(vat_invoice_name):
	"""API method to sync VAT Invoice"""
	vat_invoice = frappe.get_doc("VAT Invoice", vat_invoice_name)
	vat_invoice.sync_vat_invoice()
	return {"success": True}
