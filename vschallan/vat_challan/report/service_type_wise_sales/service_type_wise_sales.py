# Copyright (c) 2025, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

# Demo VAT Invoice data (replace this with real frappe calls later)
demo_vat_invoices = [
    {
        "name": "VATINV-0001",
        "invoice_number": "INV-001",
        "invoice_date": "2025-09-01",
        "branch": "Branch A",
        "customer_id": "CUST-001",
        "retailer_id": "RET-001",
        "txn_amount": 1200,
        "total_sd_percentage": 5,
        "total_sd_amount": 60,
        "total_discount_amount": 50,
        "total_service_charges_amount": 30,
        "total_amount": 1240,
        "payment_method": "Cash",
        "order_id": "ORD-001",
        "status": "Pending",
        "service_type": "Service A"
    },
    {
        "name": "VATINV-0002",
        "invoice_number": "INV-002",
        "invoice_date": "2025-09-02",
        "branch": "Branch B",
        "customer_id": "CUST-002",
        "retailer_id": "RET-002",
        "txn_amount": 1500,
        "total_sd_percentage": 10,
        "total_sd_amount": 150,
        "total_discount_amount": 100,
        "total_service_charges_amount": 50,
        "total_amount": 1600,
        "payment_method": "Card",
        "order_id": "ORD-002",
        "status": "Synced",
        "service_type": "Service B"
    },
    {
        "name": "VATINV-0003",
        "invoice_number": "INV-003",
        "invoice_date": "2025-09-03",
        "branch": "Branch A",
        "customer_id": "CUST-003",
        "retailer_id": "RET-003",
        "txn_amount": 800,
        "total_sd_percentage": 5,
        "total_sd_amount": 40,
        "total_discount_amount": 20,
        "total_service_charges_amount": 10,
        "total_amount": 830,
        "payment_method": "Cash",
        "order_id": "ORD-003",
        "status": "Failed",
        "service_type": "Service A"
    }
]

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_report_summary(data)
    service_chart = get_service_type_chart(data)
    return columns, data, None, service_chart, summary


def get_columns():
    return [
        {"fieldname": "name", "label": _("VAT Invoice Number"), "fieldtype": "Data", "width": 150},
        {"fieldname": "invoice_number", "label": _("Invoice Number"), "fieldtype": "Data", "width": 120},
        {"fieldname": "invoice_date", "label": _("Invoice Date"), "fieldtype": "Datetime", "width": 130},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Data", "width": 120},
        {"fieldname": "customer_id", "label": _("Customer ID"), "fieldtype": "Data", "width": 120},
        {"fieldname": "retailer_id", "label": _("Retailer ID"), "fieldtype": "Data", "width": 120},
        {"fieldname": "txn_amount", "label": _("Transaction Amount"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "total_sd_percentage", "label": _("SD %"), "fieldtype": "Percent", "width": 90},
        {"fieldname": "total_sd_amount", "label": _("SD Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_discount_amount", "label": _("Discount Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_service_charges_amount", "label": _("Service Charges"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "total_amount", "label": _("Total Amount"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "payment_method", "label": _("Payment Method"), "fieldtype": "Data", "width": 120},
        {"fieldname": "order_id", "label": _("Order ID"), "fieldtype": "Data", "width": 120},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "service_type", "label": _("Service Type"), "fieldtype": "Data", "width": 120}
    ]


def get_data(filters=None):
    # For demo purposes, return the demo JSON
    return demo_vat_invoices


def get_report_summary(data):
    total_invoices = len(data)
    pending = len([d for d in data if d["status"] == "Pending"])
    synced = len([d for d in data if d["status"] == "Synced"])
    failed = len([d for d in data if d["status"] == "Failed"])
    total_txn = sum(d["txn_amount"] for d in data)
    total_sales = sum(d["total_amount"] for d in data)
    total_vat = sum(d["total_sd_amount"] for d in data)
    total_discount = sum(d["total_discount_amount"] for d in data)
    unique_customers = len(set(d["customer_id"] for d in data))

    return [
        {"value": total_invoices, "label": "Total Invoices", "datatype": "Int", "indicator": "blue"},
        {"value": pending, "label": "Pending", "datatype": "Int", "indicator": "orange"},
        {"value": synced, "label": "Synced", "datatype": "Int", "indicator": "green"},
        {"value": failed, "label": "Failed", "datatype": "Int", "indicator": "red"},
        {"value": total_txn, "label": "Transaction Amount", "datatype": "Currency", "indicator": "blue"},
        {"value": total_sales, "label": "Total Sales", "datatype": "Currency", "indicator": "green"},
        {"value": total_vat, "label": "Total VAT Amount", "datatype": "Currency", "indicator": "orange"},
        {"value": total_discount, "label": "Total Discount", "datatype": "Currency", "indicator": "red"},
        {"value": unique_customers, "label": "Unique Customers", "datatype": "Int", "indicator": "purple"}
    ]


def get_service_type_chart(data):
    service_totals = {}
    for d in data:
        stype = d["service_type"] or "Unknown"
        service_totals[stype] = service_totals.get(stype, 0) + d["txn_amount"]

    labels = list(service_totals.keys())
    values = list(service_totals.values())

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Transaction Amount", "values": values}]
        },
        "type": "bar",
        "height": 300
    }
