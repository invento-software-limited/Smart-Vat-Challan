# Smart VAT Challan for ERPNext

<p align="center">
  <a href="https://nbr.gov.bd" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_Seal_of_Bangladesh.svg/2048px-Government_Seal_of_Bangladesh.svg.png" alt="Government of Bangladesh" height="96">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://invento.com.bd" target="_blank">
    <img src="./invento-logo.png" alt="Invento Software Limited" height="48">
  </a>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15-green)](https://erpnext.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A production-ready **ERPNext app** that integrates with the **Government of Bangladesh National Board of Revenue (NBR) Smart VAT system**.

It streamlines **Smart VAT calculation, retailer & branch registration, VAT challan generation, and reporting** directly inside ERPNext.

---

## 🚀 Key Features

- 🔐 **Secure Integration** with NBR Smart VAT APIs
- 🔄 **Automatic Access Token** management
- 🏢 **Retailer & Branch Registration** (NBR retailer, additional branches)
- 📦 **Master Data Sync** (Zones, Divisions, Circles, VAT Commission Rates, Service Types)
- 💰 **Smart VAT Calculation & Challan Generation** directly from ERPNext
- 📑 **VAT Invoice Reports** with filters (date range, retailer, status, etc.)
- ⬇️ **Challan Download** (PDF/XML from NBR portal, directly from VAT Invoice)
- 🛡 **Duplicate-Safe Data Upserts** into ERPNext doctypes
- 👤 **Role-based Access Control** using ERPNext's permission model

---
## 🎥 Demo Video

<p align="center">
  <a href="https://www.youtube.com/watch?v=VMNvvAvKBf8" target="_blank">
    <img src="https://img.youtube.com/vi/VMNvvAvKBf8/0.jpg" alt="Smart VAT Challan Demo" width="800">
  </a>
</p>

👉 Click the image to watch the full demo video.

---

## 📋 Requirements

- Frappe Framework **v15**
- ERPNext **v15**
- Python **3.10+** (recommended **3.12**)
- Valid NBR Vendor Credentials (**Client ID** and **Client Secret**)
- Internet access from ERPNext server

---

## ⚙️ Installation

```bash
cd PATH_TO_YOUR_BENCH
bench get-app URL_OF_THIS_REPO --branch main
bench install-app vschallan
bench migrate
```

# 🔧 Configuration
Go to ERPNext Desk → VAT Challan → Settings → POS Vendor Configuration (Single)

Fill in your NBR API credentials:
- Base URL (production/sandbox provided by NBR)
- Client ID
- Client Secret
- Company ID (if applicable)

Save the configuration.

Refresh or generate a new access token manually, or allow the system to do so on the first API call.

## 📡 Master Data Synchronization
Keep ERPNext in sync with NBR Smart VAT:
- Zones
- Divisions
- Circles
- VAT Commission Rates
- Retailer Service Types

From the VAT Challan module, trigger "Sync" actions. The app will:
- Fetch latest data from NBR
- Insert new records
- Avoid creating duplicates

## 🏬 Retailer & Branch Registration
Open VAT Challan → Retailer Registration to register new retailers.

Fill in required business and owner details, select service types, and submit.

Responses (retailer number, messages) are saved in ERPNext.

For multiple outlets/branches:
- Open VAT Challan → Retailer Branch Registration
- Link branches to the parent retailer
- Submit to register branch info with NBR

## 📑 VAT Invoice Reports
Analyze VAT Invoices directly in ERPNext:
- Filter by Invoice Number, Order ID, Status, Date Range
- Metrics include:
  - Total Invoices
  - Pending / Synced / Failed Invoices
  - Unique Customers
  - Transaction Amount, Total Sales, VAT Amount, Discounts
- Built-in Sales Trends Chart for daily sales amounts

## ⬇️ Challan Download
For any synced VAT Invoice:
- Open the VAT Invoice Report
- Click "Download Challan" button
- System fetches the challan PDF from NBR and downloads it locally

## 🛠 Troubleshooting
- Check credentials (Client ID/Secret, Base URL)
- Ensure server can reach NBR API endpoints
- "Unauthorized" errors → refresh access token
- Verify ERPNext user permissions for VAT Challan doctypes

## 🤝 Contributing
This app uses pre-commit for formatting and linting.

```bash
cd apps/vschallan
pre-commit install
```

## 🤝 Contributing

This app uses pre-commit for formatting and linting with the following configured tools:

- **ruff** - Python linting and formatting
- **eslint** - JavaScript/TypeScript linting
- **prettier** - Code formatting
- **pyupgrade** - Python syntax upgrades

Pull requests and issues are welcome ✅

## 📄 License

MIT License – see [LICENSE](LICENSE) file for details.

## 📞 Support

Developed and maintained by **Invento Software Limited**

🌍 Website: [https://invento.com.bd](https://invento.com.bd)
✉️ Email: [info@invento.com.bd](mailto:info@invento.com.bd)

## ⚠️ Disclaimer

This app communicates with government systems. Always:

- Validate configuration thoroughly
- Test in sandbox environment before production deployment
- Follow latest NBR compliance rules and regulations
