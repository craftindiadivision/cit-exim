// Copyright (c) 2026, craft and contributors
// For license information, please see license.txt

// frappe.query_reports["PAYMENT DETAILS"] = {
// 	"filters": [

// 	]
// };


frappe.query_reports["PAYMENT DETAILS"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        },
		{
			"fieldname": "custom_work_flow_status",
			"label": __("Workflow Status"),
			"fieldtype": "Select",
			"options": "\nShipment Under Process\nBL Issued\nDocument Submitted & Awaiting Payments\nCompleted Shipment",
			"default": "BL Issued"
		}

    ]
};