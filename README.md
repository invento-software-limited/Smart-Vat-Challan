# Smart VAT Challan for ERPNext

<p align="center">
  <a href="https://nbr.gov.bd" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_Seal_of_Bangladesh.svg/2048px-Government_Seal_of_Bangladesh.svg.png" alt="Government of Bangladesh" height="96">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://invento.com.bd" target="_blank">
    <img src="https://invento.com.bd/wp-content/uploads/2023/11/invento-logo-color.svg" alt="Invento Software Limited" height="48">
  </a>
</p>

A production-ready ERPNext app that integrates with the Government of Bangladesh National Board of Revenue (NBR) Smart VAT services. It streamlines Smart VAT calculation, retailer registration, and challan generation directly from ERPNext.

## Key Features

- Secure integration with NBR Smart VAT APIs
- Access token management with automatic refresh
- Retailer registration and status handling
- Master data sync (Zones, Divisions, Circles, VAT Commission Rates, Retailer Service Types)
- Smart VAT calculation and challan generation
- Duplicate-safe data upserts into ERPNext doctypes
- Clear errors and messages for operators
- Works with ERPNext roles and permissions

## Requirements

- Frappe Framework v15
- ERPNext v15
- Python 3.10+ (recommended 3.12)
- Valid NBR vendor credentials (Client ID and Client Secret)
- Internet access from the ERPNext server

## Installation

Install using the Bench CLI:
```bash
bash cd PATH_TO_YOUR_BENCH
bench get-appURL_OF_THIS_REPO --branch main
bench install-app vschallan
bench migrate

```
If you are using a multi-tenant setup, install the app on the desired site(s).

## Configuration

1. Open ERPNext Desk and go to:
   - VAT Challan module → Settings → POS Vendor Configuration (Single)
2. Fill in your NBR API credentials and settings:
   - Base URL (production or sandbox endpoint provided by NBR)
   - Client ID
   - Client Secret
   - Company ID (if applicable)
3. Save the configuration.
4. Generate or refresh the access token from the configuration (if a button is provided) or allow the system to fetch it automatically during the first API call.

## Master Data Synchronization

Keep your ERPNext master records in sync with NBR:

- Zones
- Divisions
- Circles
- VAT Commission Rates
- Retailer Service Types

You can trigger synchronization from the VAT Challan module (e.g., via “Sync” actions). The app will:
- Fetch the latest data from NBR
- Insert new records
- Avoid creating duplicates

## Retailer Registration

Register retailers with NBR from ERPNext:

- Open VAT Challan → Retailer Registration
- Fill in the required business and owner details
- Select service types
- Submit/Save to send the registration to NBR
- The response (including retailer number or any existing record message) will be stored with the document

## Challan Generation and VAT Calculation

- From relevant transactions or VAT-specific forms in the VAT Challan module, generate the Smart VAT challan.
- The system will compute VAT as per the configured commission rates and service types, and communicate with NBR to record the challan.
- Print or export the challan for compliance and audit.

Note: Exact forms and actions may vary based on your ERPNext setup and user permissions.

## Troubleshooting

- Ensure credentials (Client ID/Secret, Base URL) are correct and active.
- Check that your server can reach the NBR API endpoints.
- If you see “Unauthorized” errors, refresh the access token from configuration and retry.
- Verify user permissions to access VAT Challan doctypes and actions.

## Contributing

This app uses pre-commit for code formatting and linting.
```bash
cd apps/vschallan pre-commit install
```


Tools configured:
- ruff
- eslint
- prettier
- pyupgrade

We welcome issues and pull requests.

## License

MIT

## Support

Developed and maintained by Invento Software Limited.
- Website: https://invento.com.bd
- Email: info@invento.com.bd

## Disclaimer

This app communicates with government systems. Always validate configuration and test in a sandbox/non-production environment before going live. Compliance requirements may change; consult official NBR documentation for the latest rules and endpoints.
