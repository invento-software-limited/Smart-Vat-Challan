# Smart VAT Challan for ERPNext 🚀

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

A production-ready **ERPNext app** that integrates with the **Government of Bangladesh National Board of Revenue (NBR) Smart VAT system** – making Smart VAT calculation, registration, challan generation, and analytics effortless inside ERPNext. 💼📊

---

## ✨ What’s New

- 🧾 **Exchange & Return VAT handling** with automated return payloads and Smart Challan sync
- 🔁 **Daily auto-sync scheduler** to keep VAT invoices up to date
- 📊 **Advanced VAT analytics reports**
  - Branch-wise performance dashboards
  - Service-type revenue insights
  - Enhanced VAT Invoice monitor with quick actions
- 📥 **Direct Smart Challan download buttons** from reports

---

## 🎯 Key Features

- 🔐 Secure integration with NBR Smart VAT APIs
- 🔄 Automatic access-token lifecycle management
- 🏢 Retailer & branch registration workflows
- 📦 Master data sync (zones, divisions, circles, VAT commission rates, service types)
- 🧮 Smart VAT calculation & challan generation from POS invoices
- 🧾 Comprehensive VAT invoice reports with filters, charts, and quick actions
- ⬇️ One-click challan download (PDF/XML) from synced invoices
- 🔄 Automated returns, partial returns, and re-sync capabilities
- 👤 Role-based access control aligned with ERPNext permissions

---

## 🎥 Demo Video

<p align="center">
  <a href="https://www.youtube.com/watch?v=VMNvvAvKBf8" target="_blank">
    <img src="https://img.youtube.com/vi/VMNvvAvKBf8/0.jpg" alt="Smart VAT Challan Demo" width="800">
  </a>
</p>

👉 Click the image to watch the full walkthrough.

---

## 📋 Requirements

- Frappe Framework **v15**
- ERPNext **v15**
- Python **3.10+** (recommend **3.12**)
- Valid NBR vendor credentials (**Client ID** & **Client Secret**)
- Internet access from the ERPNext server

---

## ⚙️ Installation

```bash
cd PATH_TO_YOUR_BENCH
bench get-app URL_OF_THIS_REPO --branch main
bench install-app vschallan
bench migrate
```

---

## 🔧 Configuration

**ERPNext Desk → VAT Challan → Settings → POS Vendor Configuration (Single)**

Fill in your NBR API credentials:

- Base URL (production/sandbox)
- Client ID & Client Secret
- Company ID (optional)

Save, then either refresh the access token manually or let the next API call refresh it automatically.

---

## 📡 Master Data Sync

Keep ERPNext aligned with NBR data:

- Zones
- Divisions
- Circles
- VAT Commission Rates
- Retailer Service Types

Trigger Sync actions from the VAT Challan module – the app fetches, inserts, and deduplicates records seamlessly.

---

## 🏬 Retailer & Branch Registration

- VAT Challan → Retailer Registration
- VAT Challan → Retailer Branch Registration

Submit details once – responses (IDs, numbers, messages) are stored on the doctype for full traceability.

---

## 🧾 VAT Invoice Lifecycle

- Generates VAT Invoice docs automatically on POS submit (`hooks.py ➜ doc_events`)
- Validates service types against retailer configuration
- Stores Smart Challan payloads and API responses for audit-ready tracking
- Supports manual re-sync, returns, and partial returns with full payload previews

---

## 📊 Reports & Dashboards

- VAT Invoice Monitor: buttons to Sync Now or Download Smart Challan per row
- Branch-wise Sales: branch ranking with charts and summary metrics
- Service-type Sales: revenue mapped to NBR service types with filter-aware charts

Access them under **VAT Challan → Reports**. 🧠📈

---

## ⬇️ Smart Challan Download

Open the VAT Invoice report, pick a synced record, hit **Download Schallan ✅**

---

## 🛠 Troubleshooting

- Verify credentials (base URL, client ID/secret)
- Ensure your server can reach NBR APIs
- Refresh access tokens on “Unauthorized” errors
- Check user permissions for VAT Challan doctypes
- Inspect stored API responses directly on VAT Invoice docs

---

## 🤝 Contributing

This repo uses **pre-commit** for linting & formatting:

```bash
cd apps/vschallan
pre-commit install
```

Configured hooks:

- `ruff` – Python linting & formatting
- `eslint` – JS/TS linting
- `prettier` – Frontend formatting
- `pyupgrade` – Python syntax upgrades

PRs and issues welcome! 🧑‍💻💡

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.

---

## 📞 Support

Developed & maintained by **Invento Software Limited**
🌍 [https://invento.com.bd](https://invento.com.bd)
✉️ hello@invento.com.bd

---

## ⚠️ Disclaimer

This app communicates with government systems. Always:

- Validate configuration thoroughly
- Test in sandbox before production rollout
- Follow latest NBR compliance guidelines
