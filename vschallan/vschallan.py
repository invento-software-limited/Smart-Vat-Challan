import os
import frappe
import requests
from frappe.utils.password import get_decrypted_password
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from datetime import datetime


class VATSmartChallan:
	"""
	Service client for integrating with the VAT Smart Challan API.

	This class:
	- Reads API configuration from the "POS Vendor Configuration" doctype.
	- Manages access tokens (retrieve, cache, and refresh on expiry/401).
	- Calls API endpoints to fetch master data (zones, divisions, circles, VAT commission rates,
	  and retailer service types).
	- Persists responses into respective Frappe doctypes while preventing duplicates.
	"""

	def __init__(self):
		"""
		Initialize the client using configuration stored in POS Vendor Configuration.

		Loads and validates configuration, decrypts secrets, sets up token and cache directory.

		Raises:
			frappe.ValidationError: If configuration is missing or disabled.
		"""
		config_data = frappe.db.get_value(
			"POS Vendor Configuration",
			{},
			["name", "base_url", "client_id", "expiry_date", "company_id", "disabled"],
			as_dict=True
		)

		if not config_data:
			frappe.throw("No POS Vendor Configuration found")

		if config_data.disabled == 1:
			frappe.throw("POS Vendor Configuration is disabled")

		self.docname = config_data.name
		self.base_url = config_data.base_url
		self.client_id = config_data.client_id
		self.access_token = get_decrypted_password("POS Vendor Configuration", self.docname,
												   "access_token")
		self.expiry_date = config_data.expiry_date
		self.company_id = config_data.company_id
		self.client_secret = get_decrypted_password("POS Vendor Configuration", self.docname,
													"client_secret")

		self.cache_dir = os.path.join(frappe.get_site_path(), "cache")
		if not os.path.exists(self.cache_dir):
			os.makedirs(self.cache_dir)

	def get_access_token(self, force_refresh=False):
		"""
		Get a valid access token, refreshing if needed.

		Args:
			force_refresh (bool): If True, forces a fresh token request regardless of current state.

		Returns:
			dict: {
				"access_token": str,
				"expiry_date": str | None (format: "%Y-%m-%d %H:%M:%S"),
				"company_id": str | None
			}

		Raises:
			frappe.ValidationError: If token retrieval fails or response parsing fails.
		"""
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

				access_token_elem = root.find(".//access_token")
				expiry_time_elem = root.find(".//expiry_time")
				company_id_elem = root.find(".//company_id")

				if access_token_elem is None:
					frappe.throw(f"No access_token found in response: {raw_content}")

				self.access_token = access_token_elem.text
				self.expiry_date = expiry_time_elem.text if expiry_time_elem is not None else None
				self.company_id = company_id_elem.text if company_id_elem is not None else None

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

	def get_header(self):
		"""
		Build request headers for authenticated API calls.

		Returns:
			dict: Headers including Authorization, companyID and Content-Type.
		"""
		return {
			"Authorization": f"Token {self.access_token}",
			"companyID": self.company_id,
			"Content-Type": "application/json"
		}

	def get_zone(self):
		"""
		Fetch and upsert zones from the API.

		Behavior:
			- Calls /integration/zone.
			- Refreshes token and retries on 401.
			- Parses XML and inserts missing records into "VC Zone" by unique zone_id.

		Raises:
			frappe.ValidationError: On HTTP failure or XML parsing issues.
		"""

		def fetch_zones():
			url = f"{self.base_url}/integration/zone"
			headers = self.get_header()
			response = requests.get(url, headers=headers, timeout=30)
			return response

		try:
			response = fetch_zones()

			if response.status_code == 401:
				# Refresh token if unauthorized
				self.get_access_token(force_refresh=True)
				response = fetch_zones()

			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)
				for zone in root.findall(".//zone"):
					zone_id = zone.find("id").text if zone.find("id") is not None else None
					zone_name = zone.find("name").text if zone.find("name") is not None else None

					if zone_id and zone_name:
						# Check if zone already exists
						exists = frappe.db.exists("VC Zone", {"zone_id": zone_id})
						if not exists:
							# Create new VC Zone
							doc = frappe.get_doc({
								"doctype": "VC Zone",
								"zone_id": zone_id,
								"zone_name": zone_name
							})
							doc.insert(ignore_permissions=True)
							frappe.db.commit()

			except ET.ParseError:
				frappe.throw(f"Failed to parse XML response: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to fetch zones: {str(e)}")

	def get_vat_commission_rate(self):
		"""
		Fetch and upsert VAT commission rates from the API.

		Behavior:
			- Calls /integration/vat_commissionrate.
			- Refreshes token and retries on 401.
			- Parses XML and inserts missing "VC VAT Commission Rate" records by vat_commission_rate_id.
			- Links each rate to its "VC Zone" using zone_id.

		Raises:
			frappe.ValidationError: On HTTP failure or XML parsing issues.
		"""
		url = f"{self.base_url}/integration/vat_commissionrate"
		headers = self.get_header()

		try:
			response = requests.get(url, headers=headers, timeout=30)

			if response.status_code == 401:
				# Refresh token if unauthorized
				self.get_access_token(force_refresh=True)
				headers = self.get_header()
				response = requests.get(url, headers=headers, timeout=30)

			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)

				for rate in root.findall(".//data/vat_commissionrate"):
					rate_id = rate.find("id").text if rate.find("id") is not None else None
					name = rate.find("name").text if rate.find("name") is not None else None
					zone_id_elem = rate.find("zone_id").text if rate.find(
						"zone_id") is not None else None

					if rate_id and name and zone_id_elem:
						exists = frappe.db.exists("VC VAT Commission Rate",
												  {"vat_commission_rate_id": rate_id})
						if not exists:
							zone_doc = frappe.get_value("VC Zone", {"zone_id": zone_id_elem},
														"name")

							doc = frappe.get_doc({
								"doctype": "VC VAT Commission Rate",
								"vat_commission_rate_id": rate_id,
								"vat_commission_rate_name": name,
								"zone": zone_doc
							})
							doc.insert(ignore_permissions=True)
							frappe.db.commit()


			except ET.ParseError:
				frappe.throw(f"Failed to parse XML response: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to fetch VAT commission rates: {str(e)}")

	def get_division(self):
		"""
		Fetch divisions from API and save them in VC Division doctype.
		Avoid duplicates based on division ID.
		Link each division to VC Zone and VC VAT Commission Rate.
		"""
		url = f"{self.base_url}/integration/division"
		headers = self.get_header()

		try:
			response = requests.get(url, headers=headers, timeout=30)

			if response.status_code == 401:
				self.get_access_token(force_refresh=True)
				headers = self.get_header()
				response = requests.get(url, headers=headers, timeout=30)

			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)

				for div in root.findall(".//data/division"):
					div_id = div.find("id").text if div.find("id") is not None else None
					name = div.find("name").text if div.find("name") is not None else None
					zone_id = div.find("zone_id").text if div.find("zone_id") is not None else None
					vat_commissionrate_id_elem = div.find(
						"vat_commissionrate_id").text if div.find(
						"vat_commissionrate_id") is not None else None

					if div_id and name and zone_id and vat_commissionrate_id_elem:
						exists = frappe.db.exists("VC Division", {"division_id": div_id})
						if not exists:
							zone_doc = frappe.get_value("VC Zone", {"zone_id": zone_id}, "name")
							vat_rate_doc = frappe.get_value("VC VAT Commission Rate", {
								"vat_commission_rate_id": vat_commissionrate_id_elem}, "name")

							doc = frappe.get_doc({
								"doctype": "VC Division",
								"division_id": div_id,
								"division_name": name,
								"zone": zone_doc,
								"vat_commission_rate": vat_rate_doc
							})
							doc.insert(ignore_permissions=True)
							frappe.db.commit()

			except ET.ParseError:
				frappe.throw(f"Failed to parse XML response: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to fetch divisions: {str(e)}")

	def get_circle(self):
		"""
		Fetch circles from API and save them in VC Circle doctype.
		Avoid duplicates based on circle ID.
		Link each circle to VC Division, VC Zone, and VC VAT Commission Rate.
		"""
		url = f"{self.base_url}/integration/circle"
		headers = self.get_header()

		try:
			response = requests.get(url, headers=headers, timeout=30)

			if response.status_code == 401:
				self.get_access_token(force_refresh=True)
				headers = self.get_header()
				response = requests.get(url, headers=headers, timeout=30)

			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)

				for c in root.findall(".//data/circle"):
					circle_id = c.find("id").text if c.find("id") is not None else None
					name = c.find("name").text if c.find("name") is not None else None
					zone_id = c.find("zone_id").text if c.find("zone_id") is not None else None
					vat_commissionrate_id = c.find("vat_commissionrate_id").text if c.find(
						"vat_commissionrate_id") is not None else None
					division_id_elem = c.find("division_id").text if c.find(
						"division_id") is not None else None

					if circle_id and name and division_id_elem:
						# Check if circle already exists
						exists = frappe.db.exists("VC Circle", {"circle_id": circle_id})
						if not exists:
							# Get linked VC Division
							division_doc = frappe.get_value("VC Division",
															{"division_id": division_id_elem},
															"name")
							zone_doc = None
							if division_doc:
								zone_doc = frappe.get_value("VC Division", division_doc, "zone")
							vat_rate_doc = None
							if division_doc:
								vat_rate_doc = frappe.get_value("VC Division", division_doc,
																"vat_commission_rate")

							doc = frappe.get_doc({
								"doctype": "VC Circle",
								"circle_id": circle_id,
								"circle_name": name,
								"division": division_doc,
								"zone": zone_doc,
								"vat_commission_rate": vat_rate_doc
							})
							doc.insert(ignore_permissions=True)
							frappe.db.commit()

			except ET.ParseError:
				frappe.throw(f"Failed to parse XML response: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to fetch circles: {str(e)}")

	def get_service_types(self):
		"""
		Fetch Retailer Service Types from API and save them in VC Service Type doctype.
		Avoid duplicates based on service_id.
		"""
		url = f"{self.base_url}/integration/retailer_service_type"
		headers = self.get_header()

		try:
			response = requests.get(url, headers=headers, timeout=30)

			if response.status_code == 401:
				# Refresh token if unauthorized
				self.get_access_token(force_refresh=True)
				headers = self.get_header()
				response = requests.get(url, headers=headers, timeout=30)

			response.raise_for_status()
			raw_content = response.text

			try:
				root = ET.fromstring(raw_content)
				for service in root.findall(".//retailer_service_types"):
					service_id = service.findtext("id")
					heading_code = service.findtext("heading_code")
					service_code = service.findtext("service_code")
					service_name = service.findtext("service_name")
					vat_rate = service.findtext("vat_rate")

					if service_id and service_name:
						# Check if service already exists
						exists = frappe.db.exists("VC Service Type", {"service_id": service_id})
						if not exists:
							doc = frappe.get_doc({
								"doctype": "VC Service Type",
								"service_id": service_id,
								"heading_code": heading_code,
								"service_code": service_code,
								"service_name": service_name,
								"vat_rate": vat_rate
							})
							doc.insert(ignore_permissions=True)
							frappe.db.commit()

			except ET.ParseError:
				frappe.throw(f"Failed to parse XML response: {raw_content}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Failed to fetch Retailer Service Types: {str(e)}")

	def register_retailer(self, doc):
		"""
		Register a retailer via external API using RetailerRegistration doc fields
		"""
		url = f"{self.base_url}/integration/retail_registration"

		type_of_business_list = []
		if hasattr(doc, "service_types") and doc.service_types:
			for row in doc.service_types:
				if row.type_id:
					type_of_business_list.append(row.type_id)

		payload = {
			"owner_full_name": doc.owner_full_name,
			"owner_cc": doc.owner_cc,
			"owner_mobile": doc.owner_mobile,
			"owner_email": doc.owner_email,
			"owner_nid": doc.owner_nid,
			"business_name": doc.business_name,
			"business_address": doc.business_address,
			"business_logo": doc.business_logo,
			"business_website": doc.business_website,
			"business_ecom": doc.business_ecom,
			"business_app": doc.business_app,
			"bin": doc.bin,
			"trade_license_number": doc.trade_license_number,
			"tin": doc.tin,
			"type_of_business_list": type_of_business_list,
			"zone_id": doc.zone_id,
			"vat_commissionrate_id": doc.vat_commissionrate_id,
			"division_id": doc.division_id,
			"circle_id": doc.circle_id
		}

		try:
			response = requests.post(url, headers=self.get_header(), json=payload, timeout=30)
			if response.status_code == 401:
				self.get_access_token(force_refresh=True)
				response = requests.post(url, headers=self.get_header(), json=payload, timeout=30)
			response.raise_for_status()
			raw_content = response.text

			root = ET.fromstring(raw_content)

			status_code = root.findtext("status_code")
			success = root.findtext("success")
			error_msg = root.findtext("error")
			data_elem = root.find("data")

			if status_code == "200" and data_elem is not None:
				message = data_elem.findtext("message")


				retailer_id = data_elem.findtext("retailer_id")
				retailer_number = data_elem.findtext("retailer_number")

				if retailer_id and retailer_number:
					doc.db_set("status_code", status_code)
					doc.db_set("retailer_id", retailer_id)
					frappe.msgprint(f"Retailer registered successfully: {retailer_number}")

				else:
					retailer_details = data_elem.find("retailer_details")
					if retailer_details is not None:
						existing_id = retailer_details.findtext("retailer_id")
						existing_number = retailer_details.findtext("retailer_number")
						doc.db_set("status_code", status_code)
						doc.db_set("retailer_id", existing_id)

						frappe.msgprint(
							f"Retailer already exists ({message}): {existing_number}"
						)
					else:
						frappe.throw(f"Retailer registration failed: {message or 'Unknown error'}")

			elif success == "0":
				frappe.throw(f"Retailer registration failed: {error_msg or 'Unknown error'}")

			else:
				frappe.throw("Unexpected response format from API")

		except ET.ParseError:
			frappe.throw(f"Failed to parse XML response: {raw_content}")
		except requests.exceptions.HTTPError as e:
			frappe.throw(f"HTTP Error: {str(e)}")
		except requests.exceptions.RequestException as e:
			frappe.throw(f"Request Error: {str(e)}")


