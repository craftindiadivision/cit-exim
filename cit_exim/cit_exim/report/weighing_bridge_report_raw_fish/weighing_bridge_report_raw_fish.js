// Copyright (c) 2026, craft and contributors
// For license information, please see license.txt
frappe.query_reports["Weighing Bridge Report-Raw Fish"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "vehicle_queue",
            label: __("Vehicle Queue"),
            fieldtype: "Link",
            options: "Vehicle Queue",
            get_query: function () {
                return {
                    filters: {
                        product: "Raw Fish"
                    }
                };
            }
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse"
        },
        {
            fieldname: "supplier",
            label: __("Supplier"),
            fieldtype: "Link",
            options: "Supplier"
        },
        {
            fieldname: "start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "end_date",
            label: __("End Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.get_today()
        }
    ]
};
