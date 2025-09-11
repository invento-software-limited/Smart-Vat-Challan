import os
import frappe
import requests
import xmltodict
import json
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
		Initialize the client using configuration stored in POS Vendor Configuration (Single Doctype).

		Loads and validates configuration, decrypts secrets, sets up token and cache directory.

		Raises:
			frappe.ValidationError: If configuration is missing or disabled.
		"""
		config_data = frappe.db.get_singles_dict("POS Vendor Configuration")

		if not config_data:
			frappe.throw("No POS Vendor Configuration found")

		if config_data.get("disabled") == 1:
			frappe.throw("POS Vendor Configuration is disabled")

		self.docname = "POS Vendor Configuration"  # single doctypes always use their own name
		self.base_url = config_data.get("base_url")
		self.client_id = config_data.get("client_id")
		self.access_token = config_data.get("access_token")
		self.expiry_date = config_data.get("expiry_date")
		self.company_id = config_data.get("company_id")
		self.client_secret = get_decrypted_password(
			"POS Vendor Configuration", self.docname, "client_secret"
		)

	def get_access_token(self, force_refresh=False):
		"""
		Get a valid access token, refreshing if needed.
		Handles both XML and JSON responses from the API.

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
		# Return cached token if valid
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
			raw_content = response.text.strip()

			# Detect response format
			if raw_content.startswith("{") or raw_content.startswith("["):
				# JSON response
				try:
					data = json.loads(raw_content)
					self.access_token = data.get("access_token")
					self.expiry_date = data.get("expiry_time")
					self.company_id = data.get("company_id")
				except Exception as e:
					frappe.throw(f"Failed to parse JSON response: {raw_content}\nError: {str(e)}")
			else:
				# XML response
				try:
					root = ET.fromstring(raw_content)
					access_token_elem = root.find(".//access_token")
					expiry_time_elem = root.find(".//expiry_time")
					company_id_elem = root.find(".//company_id")

					if access_token_elem is None:
						frappe.throw(f"No access_token found in XML response: {raw_content}")

					self.access_token = access_token_elem.text
					self.expiry_date = expiry_time_elem.text if expiry_time_elem is not None else None
					self.company_id = company_id_elem.text if company_id_elem is not None else None

				except ET.ParseError:
					frappe.throw(f"Failed to parse XML response: {raw_content}")

			# Save to Single Doc
			frappe.db.set_single_value("POS Vendor Configuration", "access_token",
									   self.access_token)
			frappe.db.set_single_value("POS Vendor Configuration", "expiry_date", self.expiry_date)
			frappe.db.set_single_value("POS Vendor Configuration", "company_id", self.company_id)
			frappe.db.commit()

			return {
				"access_token": self.access_token,
				"expiry_date": self.expiry_date,
				"company_id": self.company_id
			}

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
			- Uses common parser to handle XML/JSON.
			- Inserts missing records into "VC Zone" by unique zone_id.
		"""
		url = f"{self.base_url}/integration/zone"
		parsed_data = self.get_response_data(url, "GET")

		zones = []
		if isinstance(parsed_data, dict):
			data = parsed_data.get("data") or parsed_data
			zone_data = data.get("zone")
			if isinstance(zone_data, list):
				zones = zone_data
			elif isinstance(zone_data, dict):
				zones = [zone_data]

		for z in zones:
			zone_id = z.get("id")
			zone_name = z.get("name")

			if zone_id and zone_name:
				if not frappe.db.exists("VC Zone", {"zone_id": zone_id}):
					doc = frappe.get_doc({
						"doctype": "VC Zone",
						"zone_id": zone_id,
						"zone_name": zone_name
					})
					doc.insert(ignore_permissions=True)
					frappe.db.commit()

	def get_vat_commission_rate(self):
		"""
		Fetch and upsert VAT commission rates from the API.

		Behavior:
			- Calls /integration/vat_commissionrate.
			- Uses common parser (XML/JSON).
			- Inserts missing "VC VAT Commission Rate" records by vat_commission_rate_id.
			- Links each rate to its "VC Zone" using zone_id.
		"""
		url = f"{self.base_url}/integration/vat_commissionrate"
		parsed_data = self.get_response_data(url, "GET")

		rates = []
		if isinstance(parsed_data, dict):
			data = parsed_data.get("data") or parsed_data
			rate_data = data.get("vat_commissionrate")
			if isinstance(rate_data, list):
				rates = rate_data
			elif isinstance(rate_data, dict):
				rates = [rate_data]

		for r in rates:
			rate_id = r.get("id")
			name = r.get("name")
			zone_id_elem = r.get("zone_id")

			if rate_id and name and zone_id_elem:
				if not frappe.db.exists("VC VAT Commission Rate",
										{"vat_commission_rate_id": rate_id}):
					zone_doc = frappe.get_value("VC Zone", {"zone_id": zone_id_elem}, "name")

					doc = frappe.get_doc({
						"doctype": "VC VAT Commission Rate",
						"vat_commission_rate_id": rate_id,
						"vat_commission_rate_name": name,
						"zone": zone_doc
					})
					doc.insert(ignore_permissions=True)
					frappe.db.commit()

	def get_division(self):
		"""
		Fetch divisions from API and save them in VC Division doctype.
		Avoid duplicates based on division ID.
		Link each division to VC Zone and VC VAT Commission Rate.
		"""
		url = f"{self.base_url}/integration/division"
		parsed_data = self.get_response_data(url, "GET")

		divisions = []
		if isinstance(parsed_data, dict):
			data = parsed_data.get("data") or parsed_data
			div_data = data.get("division")
			if isinstance(div_data, list):
				divisions = div_data
			elif isinstance(div_data, dict):
				divisions = [div_data]

		for d in divisions:
			div_id = d.get("id")
			name = d.get("name")
			zone_id = d.get("zone_id")
			vat_commissionrate_id_elem = d.get("vat_commissionrate_id")

			if div_id and name and zone_id and vat_commissionrate_id_elem:
				if not frappe.db.exists("VC Division", {"division_id": div_id}):
					zone_doc = frappe.get_value("VC Zone", {"zone_id": zone_id}, "name")
					vat_rate_doc = frappe.get_value(
						"VC VAT Commission Rate",
						{"vat_commission_rate_id": vat_commissionrate_id_elem},
						"name"
					)

					doc = frappe.get_doc({
						"doctype": "VC Division",
						"division_id": div_id,
						"division_name": name,
						"zone": zone_doc,
						"vat_commission_rate": vat_rate_doc
					})
					doc.insert(ignore_permissions=True)
					frappe.db.commit()

	def get_circle(self):
		"""
		Fetch circles from API and save them in VC Circle doctype.
		Avoid duplicates based on circle ID.
		Link each circle to VC Division, VC Zone, and VC VAT Commission Rate.
		"""
		url = f"{self.base_url}/integration/circle"
		parsed_data = self.get_response_data(url, "GET")

		circles = []
		if isinstance(parsed_data, dict):
			data = parsed_data.get("data")
			if data:
				circle_data = data.get("circle")
				if isinstance(circle_data, list):
					circles = circle_data
				elif isinstance(circle_data, dict):
					circles = [circle_data]

		for c in circles:
			circle_id = c.get("id")
			name = c.get("name")
			zone_id = c.get("zone_id")
			vat_commissionrate_id = c.get("vat_commissionrate_id")
			division_id_elem = c.get("division_id")

			if not (circle_id and name and division_id_elem):
				continue  # skip invalid record

			# Skip if already exists
			if frappe.db.exists("VC Circle", {"circle_id": circle_id}):
				continue

			division_doc = frappe.get_value("VC Division",
											{"division_id": division_id_elem},
											"name")
			zone_doc = frappe.get_value("VC Zone",
										{"zone_id": zone_id},
										"name")
			vat_rate_doc = frappe.get_value("VC VAT Commission Rate",
											{"vat_commission_rate_id": vat_commissionrate_id},
											"name")

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

	def get_service_types(self):
		"""
		Fetch Retailer Service Types from API and save them in VC Service Type doctype.
		Avoid duplicates based on service_id.
		"""
		url = f"{self.base_url}/integration/retailer_service_type"
		parsed_data = self.get_response_data(url, "GET")

		services = []
		if isinstance(parsed_data, dict):
			# Handle {"data": {"retailer_service_types": [...]}}
			data = parsed_data.get("data")
			if data:
				service_data = data.get("retailer_service_types")
				if isinstance(service_data, list):
					services = service_data
				elif isinstance(service_data, dict):
					services = [service_data]

		for service in services:
			service_id = service.get("id")
			heading_code = service.get("heading_code")
			service_code = service.get("service_code")
			service_name = service.get("service_name")
			vat_rate = service.get("vat_rate")

			if not (service_id and service_name):
				continue  # skip invalid

			# Check if service already exists
			exists = frappe.db.exists("VC Service Type", {"service_id": service_id})
			if exists:
				continue

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

	def register_retailer(self, doc):
		"""
		Register a retailer via external API using RetailerRegistration doc fields.
		Handles both XML and JSON responses.
		"""
		url = f"{self.base_url}/integration/retail_registration"

		# Collect service types
		type_of_business_list = []
		if hasattr(doc, "service_types") and doc.service_types:
			for row in doc.service_types:
				if row.type_id:
					type_of_business_list.append(row.type_id)

		# Prepare payload
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
			"circle_id": doc.circle_id,
		}

		try:
			parsed_data = self.get_response_data(url, "POST", payload)
			doc.db_set("server_response", json.dumps(parsed_data, indent=2))
			status_code = str(parsed_data.get("status_code"))
			success = parsed_data.get("success")
			error_msg = parsed_data.get("error")
			data_elem = parsed_data.get("data")

			if status_code == "200" and data_elem:
				message = data_elem.get("message")
				retailer_id = data_elem.get("retailer_id")
				retailer_number = data_elem.get("retailer_number")

				if retailer_id and retailer_number:
					doc.db_set("status_code", status_code)
					doc.db_set("retailer_id", retailer_id)
					frappe.msgprint(f"Retailer registered successfully: {retailer_number}")

				else:
					retailer_details = data_elem.get("retailer_details")
					if retailer_details:
						existing_id = retailer_details.get("retailer_id")
						existing_number = retailer_details.get("retailer_number")
						doc.db_set("status_code", status_code)
						doc.db_set("retailer_id", existing_id)

						frappe.msgprint(
							f"Retailer already exists ({message}): {existing_number}"
						)
					else:
						frappe.throw(
							f"Retailer registration failed: {message or 'Unknown error'}"
						)

			elif success == "0":
				frappe.throw(f"Retailer registration failed: {error_msg or 'Unknown error'}")

			else:
				frappe.throw("Unexpected response format from API")

		except requests.exceptions.HTTPError as e:
			frappe.throw(f"HTTP Error: {str(e)}")
		except requests.exceptions.RequestException as e:
			frappe.throw(f"Request Error: {str(e)}")

	def parse_xml_to_json(self, xml_string):
		"""
		Convert XML string to JSON dict
		"""
		try:
			return xmltodict.parse(xml_string)
		except Exception as e:
			frappe.throw(f"Failed to convert XML to JSON: {str(e)}")

	def detect_response_format(self, response_text: str) -> str:
		"""
		Detects if a response string is in XML or JSON format.

		Returns:
			"json" if JSON,
			"xml" if XML,
			"unknown" if neither.
		"""
		response_text = response_text.strip()

		# Try JSON
		try:
			json.loads(response_text)
			return "json"
		except (json.JSONDecodeError, TypeError):
			pass

		# Try XML
		try:
			ET.fromstring(response_text)
			return "xml"
		except ET.ParseError:
			pass

		return "unknown"

	def get_response_data(self, url: str, request_type: str, payload: dict = None,
						  files: dict = None):
		"""
		Perform an authenticated HTTP request and return parsed response data.

		Behavior:
		- Sends GET or POST requests with Authorization headers.
		- Automatically refreshes the access token and retries once on HTTP 401.
		- Detects response format (XML/JSON) and returns a parsed Python dict.
		  For XML responses, the "ObjectNode" element is extracted after conversion.
		- Supports file uploads via multipart/form-data if `files` is provided.

		Args:
			url (str): The API endpoint URL.
			request_type (str): "GET" or "POST".
			payload (dict, optional): JSON-serializable body for POST requests.
			files (dict, optional): Dictionary of files for multipart upload, e.g. {"file": open("path", "rb")}.

		Returns:
			dict | list | None: Parsed response content. For XML, the value of "ObjectNode".
								For JSON, the decoded JSON structure.

		Raises:
			frappe.ValidationError: If request_type is invalid or if response format is unknown.
			requests.exceptions.RequestException: For network/HTTP errors (after retry logic).
		"""
		headers = self.get_header()

		try:
			# Determine request method
			if request_type == "GET":
				response = requests.get(url, headers=headers, timeout=30)
			elif request_type == "POST":
				if files:
					response = requests.post(url, headers=headers, data=payload, files=files,
											 timeout=30)
				else:
					response = requests.post(url, headers=headers, json=payload, timeout=30)
			else:
				frappe.throw("Invalid request type")

			# Retry if unauthorized
			if response.status_code == 401:
				self.get_access_token(force_refresh=True)
				headers = self.get_header()
				if request_type == "GET":
					response = requests.get(url, headers=headers, timeout=30)
				elif request_type == "POST":
					if files:
						response = requests.post(url, headers=headers, data=payload, files=files,
												 timeout=30)
					else:
						response = requests.post(url, headers=headers, json=payload, timeout=30)

			response.raise_for_status()
			raw_content = response.text
			format_type = self.detect_response_format(raw_content)

			# Parse response
			if format_type == "xml":
				converted_data = self.parse_xml_to_json(raw_content)
				parsed_data = converted_data.get("ObjectNode", converted_data)
			elif format_type == "json":
				parsed_data = json.loads(raw_content)
			else:
				frappe.throw("Unknown response format from API")

			return parsed_data

		except requests.exceptions.RequestException as e:
			frappe.throw(str(e))
		finally:
			if files:
				for f in files.values():
					f.close()

	def upload_file(self, document_category_key: str, file_path: str, retailer_id: str):
		"""
		Upload a document file for a retailer to the NBR API using common response handling.

		Args:
			document_category_key (str): Document category key.
			file_path (str): Local file path to upload.
			retailer_id (str): Retailer's ID.

		Returns:
			dict: API response containing message and uploaded file URL.

		Raises:
			frappe.ValidationError: On upload failure or invalid response.
		"""
		absolute_file_path = frappe.get_site_path("public", file_path.lstrip("/"))

		if not os.path.exists(absolute_file_path):
			frappe.throw(f"File does not exist: {absolute_file_path}")

		url = f"{self.base_url}/integration/upload_file"

		files = {"file": open(absolute_file_path, "rb")}
		payload = {
			"retailer_id": retailer_id,
			"document_category_key": document_category_key
		}

		try:
			parsed_data = self.get_response_data(url, request_type="POST", payload=payload,
												 files=files)

			# Handle response
			status_code = str(parsed_data.get("status_code") or parsed_data.get("code"))
			if status_code == "200":
				data = parsed_data.get("data", {})
				message = data.get("message")
				file_url = data.get("upload_file_url")
				frappe.msgprint(f"{message}: {file_url}")
				return data
			else:
				error_msg = parsed_data.get("message") or parsed_data.get(
					"error") or "Unknown error"
				frappe.throw(f"File upload failed: {error_msg}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Request Error: {str(e)}")
