# Copyright (c) 2025, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from vschallan.vschallan import VATSmartChallan


class RetailerRegistration(Document):
	def before_submit(self):
		vschallan = VATSmartChallan()
		vschallan.register_retailer(self)


@frappe.whitelist()
def get_service_types(force_refresh=False):
	vschallan = VATSmartChallan()
	result = vschallan.get_service_types(force_refresh=frappe.utils.cint(force_refresh))
	return result


@frappe.whitelist()
def get_zone(force_refresh=False):
	vschallan = VATSmartChallan()
	result = vschallan.get_zone(force_refresh=frappe.utils.cint(force_refresh))
	return result


@frappe.whitelist()
def get_vat_commission_rate(force_refresh=False, zone_id=None):
	vschallan = VATSmartChallan()
	result = vschallan.get_vat_commission_rate(
		force_refresh=frappe.utils.cint(force_refresh),
		zone_id=zone_id
	)
	return result


@frappe.whitelist()
def get_division(force_refresh=False, vat_commissionrate_id=None):
	vschallan = VATSmartChallan()
	result = vschallan.get_division(
		force_refresh=frappe.utils.cint(force_refresh),
		vat_commissionrate_id=vat_commissionrate_id
	)
	return result


@frappe.whitelist()
def get_circle(force_refresh=False, division_id=None):
	vschallan = VATSmartChallan()
	result = vschallan.get_circle(
		force_refresh=frappe.utils.cint(force_refresh),
		division_id=division_id
	)
	return result
