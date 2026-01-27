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
        {"label": "Location", "fieldname": "warehouse", "fieldtype": "Link", "options": "warehouse", "width": 160},
        {"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": 90},
        {"label": "Token No", "fieldname": "token_number", "fieldtype": "Data", "width": 100},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "In Time", "fieldname": "in_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Out Time", "fieldname": "out_time", "fieldtype": "DateTime", "width": 90},
        {"label": "Vehicle No", "fieldname": "vehicle_no", "fieldtype": "Data", "width": 130},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Supplier Invoice", "fieldname": "supplier_invoice_number", "fieldtype": "Data", "width": 140},
        {"label": "Invoice Qty", "fieldname": "invoice_qty", "fieldtype": "Float", "width": 90},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": "Purchase Receipt", "fieldname": "purchase_receipt", "fieldtype": "Link", "options": "Purchase Receipt", "width": 160},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 90},
        
    ]

def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("company"):
        conditions += " AND vq.company = %(company)s"
        values["company"] = filters["company"]

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
            vq.warehouse AS location,
            vq.type,
            vq.token_number,
            vq.date,
            vq.in_time,
            vq.out_time,
            vq.vehicle_no,
            vq.supplier,
            pri.item_code AS item,
            pr.name AS purchase_receipt,
            pri.qty,
            vq.supplier_invoice_number,
            vq.invoice_qty
        FROM `tabVehicle Queue` vq
        LEFT JOIN `tabPurchase Receipt` pr
            ON pr.custom_vehicle_queue = vq.name
            AND pr.docstatus = 1
        LEFT JOIN `tabPurchase Receipt Item` pri
            ON pri.parent = pr.name
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
    return add_vehicle_queue_totals(data)

def add_vehicle_queue_totals(data):
    result = []
    current_vq = None
    current_pr = None
    total_qty = 0
    total_invoice_qty = 0

    for row in data:
        # New Vehicle Queue
        if current_vq != row["vehicle_queue"]:
            if current_vq:
                result.append({
                    "vehicle_queue": "Total",
                    "qty": total_qty,
                    "invoice_qty": total_invoice_qty
                })
                total_qty = 0
                total_invoice_qty = 0

            current_vq = row["vehicle_queue"]
            current_pr = row["purchase_receipt"]
            total_qty += row.get("qty") or 0
            total_invoice_qty += row.get("invoice_qty") or 0
            result.append(row)
            continue

        # Same Vehicle Queue
        total_qty += row.get("qty") or 0
        total_invoice_qty += row.get("invoice_qty") or 0

        # Hide repeated fields
        row["vehicle_queue"] = ""
        row["loading_location"] = ""
        row["type"] = ""
        row["token_number"] = ""
        row["date"] = ""
        row["in_time"] = ""
        row["out_time"] = ""
        row["vehicle_no"] = ""
        row["supplier"] = ""

        # Same Purchase Receipt → hide PR field
        if current_pr == row["purchase_receipt"]:
            row["purchase_receipt"] = ""
        else:
            current_pr = row["purchase_receipt"]

        # Only hide supplier_invoice_number for repeated PRs (optional)
        row["supplier_invoice_number"] = ""

        result.append(row)

    # Final Vehicle Queue total
    if current_vq:
        result.append({
            "vehicle_queue": "Total",
            "qty": total_qty,
            "invoice_qty": total_invoice_qty
        })

    return result
