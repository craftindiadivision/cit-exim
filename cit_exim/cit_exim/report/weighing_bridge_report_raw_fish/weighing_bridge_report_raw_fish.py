# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# Copyright (c) 2026
# Weighing Bridge Report - Raw Fish

import frappe

RAW_FISH_PRODUCT = "Raw Fish"


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Vehicle Queue", "fieldname": "vehicle_queue", "fieldtype": "Link", "options": "Vehicle Queue", "width": 180},
        {"label": "Loading Location", "fieldname": "loading_location", "fieldtype": "Link", "options": "Loading Location", "width": 160},
        {"label": "Unloading Location", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
        {"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": 90},
        {"label": "Token No", "fieldname": "token_number", "fieldtype": "Data", "width": 100},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "In Time", "fieldname": "in_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Out Time", "fieldname": "out_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Vehicle No", "fieldname": "vehicle_no", "fieldtype": "Data", "width": 130},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 90},
        {"label": "Purchase Receipt", "fieldname": "purchase_receipt", "fieldtype": "Link", "options": "Purchase Receipt", "width": 160},

    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("company"):
        conditions += " AND vq.company = %(company)s"
        values["company"] = filters["company"]

    if filters.get("warehouse"):
        conditions += " AND vq.warehouse = %(warehouse)s"
        values["warehouse"] = filters["warehouse"]

    if filters.get("vehicle_queue"):
        conditions += " AND vq.name = %(vehicle_queue)s"
        values["vehicle_queue"] = filters["vehicle_queue"]

    if filters.get("supplier"):
        conditions += " AND vq.supplier = %(supplier)s"
        values["supplier"] = filters["supplier"]

    if filters.get("start_date"):
        conditions += " AND vq.date >= %(start_date)s"
        values["start_date"] = filters["start_date"]

    if filters.get("end_date"):
        conditions += " AND vq.date <= %(end_date)s"
        values["end_date"] = filters["end_date"]

    query = f"""
        SELECT
            vq.name AS vehicle_queue,
            vq.loading_location,
            vq.warehouse,
            vq.type,
            vq.token_number,
            vq.date,
            vq.in_time,
            vq.out_time,
            vq.vehicle_no,
            vq.supplier,
            vqi.item AS item,
            pr.name AS purchase_receipt,
            vqi.net_wt AS qty
        FROM `tabVehicle Queue` vq

        LEFT JOIN `tabVehicle Queue Item` vqi
            ON vqi.parent = vq.name

        LEFT JOIN `tabPurchase Receipt` pr
            ON pr.custom_vehicle_queue = vq.name
            AND pr.docstatus = 1

        WHERE
            vq.docstatus < 2
            AND vq.product = %(raw_fish)s
            {conditions}

        ORDER BY
            vq.name
    """

    values["raw_fish"] = RAW_FISH_PRODUCT

    data = frappe.db.sql(query, values, as_dict=True)

    return format_data(data)


def format_data(data):
    result = []
    current_vq = None
    current_pr = None

    for row in data:

        # New Vehicle Queue
        if current_vq != row["vehicle_queue"]:
            current_vq = row["vehicle_queue"]
            current_pr = row["purchase_receipt"]
            result.append(row)
            continue

        # Hide repeated Vehicle Queue fields
        row["vehicle_queue"] = ""
        row["loading_location"] = ""
        row["warehouse"] = ""
        row["type"] = ""
        row["token_number"] = ""
        row["date"] = ""
        row["in_time"] = ""
        row["out_time"] = ""
        row["vehicle_no"] = ""
        row["supplier"] = ""

        # Hide repeated Purchase Receipt
        if current_pr == row["purchase_receipt"]:
            row["purchase_receipt"] = ""
        else:
            current_pr = row["purchase_receipt"]

        result.append(row)

    return result