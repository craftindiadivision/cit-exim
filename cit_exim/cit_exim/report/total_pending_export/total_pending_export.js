// Copyright (c) 2026, craft and contributors
// For license information, please see license.txt

frappe.query_reports["Total Pending Export"] = {
    "filters": [
	        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            // "reqd": 1
        },

        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": ""
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },

    ]
};
