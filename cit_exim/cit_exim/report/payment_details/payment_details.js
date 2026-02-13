
// Copyright (c) 2024, Your Name/Company and contributors
// For license information, please see license.txt

frappe.query_reports["PAYMENT DETAILS"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "workflow_status",
            "label": __("WorkFlow"),
            "fieldtype": "Select",
            "options": "\nShipment Under Process\nBL Issued\nDocument Submitted & Awaiting Payments"
        }
    ]
};