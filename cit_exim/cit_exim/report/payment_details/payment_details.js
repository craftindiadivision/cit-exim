
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
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("End Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "workflow_status",
            "label": __("WorkFlow"),
            "fieldtype": "Select",
            "options": " \nTo Be Tested\nUnder Testing\nTested and Report Passed\nLoading In-progress\nShipment Under Process\nBL Pending\nBL Issued\nDocument Checks In-progress\nDocument Submitted & Awaiting Payments\nCompleted Shipment"
        }
    ]
};