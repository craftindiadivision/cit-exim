// Copyright (c) 2026, craft and contributors
// For license information, please see license.txt

frappe.query_reports["Weighing Bridge Report"] = {
    filters: [
        {
            fieldname: "start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "end_date",
            label: __("End Date"),
            fieldtype: "Date",
            reqd: 1
        }
    ]
};