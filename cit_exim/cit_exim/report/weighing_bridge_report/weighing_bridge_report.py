# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Location",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 140
        },
        {
            "label": "Type",
            "fieldname": "type",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Token No",
            "fieldname": "token_number",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": "Vehicle No",
            "fieldname": "vehicle_no",
            "fieldtype": "Data",
            "width": 130
        },
        {
            "label": "Supplier / Customer",
            "fieldname": "party",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 160
        },
        {
            "label": "Purchase Receipt",
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 160
        },
        {
            "label": "In Time",
            "fieldname": "in_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": "Out Time",
            "fieldname": "out_time",
            "fieldtype": "Time",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("start_date"):
        conditions += " AND vq.date >= %(start_date)s"
        values["start_date"] = filters.get("start_date")

    if filters.get("end_date"):
        conditions += " AND vq.date <= %(end_date)s"
        values["end_date"] = filters.get("end_date")

    query = f"""
        SELECT
            vq.warehouse,
            vq.type,
            vq.token_number,
            vq.date,
            vq.vehicle_no,
            CASE
                WHEN vq.type = 'Inward' THEN vq.supplier
                WHEN vq.type = 'Outward' THEN vq.customer
                ELSE ''
            END AS party,
            vqi.item,
            pr.name AS purchase_receipt,
            vq.in_time,
            vq.out_time
        FROM `tabVehicle Queue` vq
        LEFT JOIN `tabVehicle Queue Item` vqi
            ON vqi.parent = vq.name
        LEFT JOIN `tabPurchase Receipt` pr
            ON pr.custom_vehicle_queue = vq.name
            AND pr.docstatus < 2
        WHERE
            vq.docstatus < 2
            {conditions}
        ORDER BY vq.date DESC, vq.in_time DESC
    """

    return frappe.db.sql(query, values, as_dict=True)