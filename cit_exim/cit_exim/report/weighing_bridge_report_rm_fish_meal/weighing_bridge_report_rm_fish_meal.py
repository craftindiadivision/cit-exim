# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# Weighing Bridge Report - RM-Fish Meal

# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# Weighing Bridge Report - RM-Fish Meal

import frappe

RM_FISH_MEAL_PRODUCT = "RM-Fish Meal"

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Vehicle Queue", "fieldname": "vehicle_queue", "fieldtype": "Link", "options": "Vehicle Queue", "width": 180},
        {"label": "Unloading Location", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
        {"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": 90},
        {"label": "Token No", "fieldname": "token_number", "fieldtype": "Data", "width": 100},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "In Time", "fieldname": "in_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Out Time", "fieldname": "out_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Vehicle No", "fieldname": "vehicle_no", "fieldtype": "Data", "width": 130},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Supplier Invoice", "fieldname": "supplier_invoice_number", "fieldtype": "Data", "width": 140},
        {"label": "Supplier Invoice Qty", "fieldname": "invoice_qty", "fieldtype": "Float", "width": 90},
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
            vq.net_weight AS qty,
            vq.supplier_invoice_number,
            vq.invoice_qty
        FROM `tabVehicle Queue` vq

        LEFT JOIN `tabVehicle Queue Item` vqi
            ON vqi.parent = vq.name

        LEFT JOIN `tabPurchase Receipt` pr
            ON pr.custom_vehicle_queue = vq.name
            AND pr.docstatus = 1

        LEFT JOIN `tabPurchase Voucher` pv
            ON pv.vehicle_queue = vq.name
            AND pv.docstatus = 1

        WHERE
            vq.docstatus < 2
            AND vq.product = %(rm_fish_meal)s
            {conditions}

        ORDER BY
            vq.name,
            pr.posting_date
    """

    values["rm_fish_meal"] = RM_FISH_MEAL_PRODUCT

    data = frappe.db.sql(query, values, as_dict=True)

    return data