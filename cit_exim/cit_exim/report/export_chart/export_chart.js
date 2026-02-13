// Copyright (c) 2026, craft and contributors
// For license information, please see license.txt

// frappe.query_reports["EXPORT CHART"] = {
// 	"filters": [

// 	]
// };


frappe.query_reports["EXPORT CHART"] = {
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
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        // {
        //     "fieldname": "agent",
        //     "label": __("Agent"),
        //     "fieldtype": "Link",
        //     "options": "Supplier" // Or "Customer" depending on your field setup
        // }
 {
    "fieldname": "agent",
    "label": __("Agent"),
    "fieldtype": "Link",
    "options": "Supplier",
    "get_query": function() {
        return {
            filters: {
                "custom_is_agent": 1
            }
        };
    }
}
    ]
};