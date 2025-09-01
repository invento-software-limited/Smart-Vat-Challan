import frappe
import requests
from frappe.utils.password import get_decrypted_password
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from datetime import datetime


class VATSmartChallan:
	def __init__(self):
		# Get all configuration data in a single query
		config_data = frappe.db.get_value(
			"POS Vendor Configuration",
			{},
			["name", "base_url", "client_id", "access_token", "expiry_date", "company_id", "disabled"],
			as_dict=True
		)

		if not config_data:
			frappe.throw("No POS Vendor Configuration found")

		if config_data.disabled == 1:
			frappe.throw("POS Vendor Configuration is disabled")

		self.docname = config_data.name
		self.base_url = config_data.base_url
		self.client_id = config_data.client_id
		self.access_token = config_data.access_token
		self.expiry_date = config_data.expiry_date
		self.company_id = config_data.company_id
		self.client_secret = get_decrypted_password("POS Vendor Configuration", self.docname,
													"client_secret")

	def get_access_token(self, force_refresh=False):
		# Check if token is still valid (not expired)
		if self.access_token and not force_refresh and self.expiry_date:
			try:
				expiry_datetime = datetime.strptime(self.expiry_date, "%Y-%m-%d %H:%M:%S")
				if expiry_datetime > datetime.now():
					return {
						"access_token": self.access_token,
						"expiry_date": self.expiry_date,
						"company_id": self.company_id
					}
			except (ValueError, TypeError):
				# If date format is invalid, force refresh
				pass

		url = f"{self.base_url}/integration/vendor_authenticate"
		headers = {"Content-Type": "application/json"}

		try:
			response = requests.post(
				url,
				headers=headers,
				auth=HTTPBasicAuth(self.client_id, self.client_secret),
				timeout=30
			)
			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)

				# Extract elements
				access_token_elem = root.find(".//access_token")
				expiry_time_elem = root.find(".//expiry_time")
				company_id_elem = root.find(".//company_id")

				if access_token_elem is None:
					frappe.throw(f"No access_token found in response: {raw_content}")

				# Update instance variables
				self.access_token = access_token_elem.text
				self.expiry_date = expiry_time_elem.text if expiry_time_elem is not None else None
				self.company_id = company_id_elem.text if company_id_elem is not None else None

				# Save to database
				frappe.db.set_value(
					"POS Vendor Configuration",
					self.docname,
					{
						"access_token": self.access_token,
						"expiry_date": self.expiry_date,
						"company_id": self.company_id
					}
				)

				frappe.db.commit()

				return {
					"access_token": self.access_token,
					"expiry_date": self.expiry_date,
					"company_id": self.company_id
				}

			except ET.ParseError:
				frappe.throw(f"Failed to parse XML: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to authenticate vendor: {str(e)}")
