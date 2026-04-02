# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt





# import frappe

# def execute(filters=None):
#     items = get_items()
#     columns = get_columns(items)
#     data = get_data(items)

#     return columns, data

# def get_items():
#     return frappe.db.sql("""
#         SELECT DISTINCT soi.item_code, i.item_name
#         FROM `tabSales Order Item` soi
#         JOIN `tabSales Order` so ON so.name = soi.parent
#         JOIN `tabItem` i ON i.name = soi.item_code
#         WHERE so.docstatus = 1
#         -- Only fetch items for orders that HAVE a consignee
#         AND so.custom_consignee IS NOT NULL 
#         AND so.custom_consignee <> ''
#         ORDER BY i.item_name
#     """, as_dict=1)

# def get_columns(items):
#     columns = [
#         {
#             "label": "Consignee",
#             "fieldname": "consignee",
#             "fieldtype": "Data",
#             "width": 220
#         }
#     ]

#     for item in items:
#         columns.append({
#             "label": item.item_name,
#             "fieldname": frappe.scrub(item.item_code),
#             "fieldtype": "Float",
#             "width": 120
#         })

#     columns.append({
#         "label": "Grand Total",
#         "fieldname": "grand_total",
#         "fieldtype": "Float",
#         "width": 140
#     })

#     return columns

# def get_data(items):
#     # Added WHERE conditions to exclude null or empty custom_consignee
#     rows = frappe.db.sql("""
#         SELECT
#             so.custom_consignee AS consignee,
#             soi.item_code,
#             SUM(soi.qty) AS so_qty,
#             IFNULL(SUM(sii.qty),0) AS si_qty
#         FROM `tabSales Order` so
#         JOIN `tabSales Order Item` soi
#             ON soi.parent = so.name
#         LEFT JOIN `tabSales Invoice Item` sii
#             ON sii.sales_order = so.name
#             AND sii.item_code = soi.item_code
#             AND sii.docstatus = 1
#         WHERE so.docstatus = 1
#             AND so.custom_consignee IS NOT NULL
#             AND so.custom_consignee <> ''
#         GROUP BY so.custom_consignee, soi.item_code
#     """, as_dict=1)

#     result = {}
#     column_totals = {}

#     for r in rows:
#         pending = r.so_qty - r.si_qty

#         if pending <= 0:
#             continue

#         consignee = r.consignee

#         if consignee not in result:
#             result[consignee] = {"consignee": consignee, "grand_total": 0}

#         fieldname = frappe.scrub(r.item_code)

#         result[consignee][fieldname] = result[consignee].get(fieldname, 0) + pending
#         result[consignee]["grand_total"] += pending

#         column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

#     data = list(result.values())

#     # Grand Total row
#     total_row = {"consignee": "Grand Total"}
#     grand_total_sum = 0

#     for field in column_totals:
#         total_row[field] = column_totals[field]
#         grand_total_sum += column_totals[field]

#     total_row["grand_total"] = grand_total_sum

#     if data:
#         data.append(total_row)

#     return data




import frappe

def execute(filters=None):
    items = get_items()
    columns = get_columns(items)
    data = get_data(items)

    return columns, data


# -------------------------------------------------
# 1. GET DISTINCT ITEMS (ONLY WITH CONSIGNEE)
# -------------------------------------------------
def get_items():
    return frappe.db.sql("""
        SELECT DISTINCT soi.item_code, i.item_name
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON so.name = soi.parent
        JOIN `tabItem` i ON i.name = soi.item_code
        WHERE so.docstatus = 1
            AND so.custom_consignee IS NOT NULL 
            AND so.custom_consignee <> ''
        ORDER BY i.item_name
    """, as_dict=1)


# -------------------------------------------------
# 2. COLUMNS
# -------------------------------------------------
def get_columns(items):
    columns = [
        {
            "label": "Consignee",
            "fieldname": "consignee",
            "fieldtype": "Data",
            "width": 220
        }
    ]

    for item in items:
        columns.append({
            "label": item.item_name,
            "fieldname": frappe.scrub(item.item_code),
            "fieldtype": "Float",
            "width": 120
        })

    columns.append({
        "label": "Grand Total",
        "fieldname": "grand_total",
        "fieldtype": "Float",
        "width": 140
    })

    return columns


# -------------------------------------------------
# 3. DATA (DELIVERY PENDING)
# -------------------------------------------------
def get_data(items):

    rows = frappe.db.sql("""
        SELECT
            so.custom_consignee AS consignee,
            soi.item_code,
            SUM(soi.qty) AS so_qty,
            SUM(IFNULL(soi.delivered_qty, 0)) AS delivered_qty
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi
            ON soi.parent = so.name
        WHERE so.docstatus = 1
            AND so.custom_consignee IS NOT NULL
            AND so.custom_consignee <> ''
        GROUP BY so.custom_consignee, soi.item_code
    """, as_dict=1)

    result = {}
    column_totals = {}

    for r in rows:
        # ✅ DELIVERY PENDING LOGIC
        pending = (r.so_qty or 0) - (r.delivered_qty or 0)

        if pending <= 0:
            continue

        consignee = r.consignee

        if consignee not in result:
            result[consignee] = {
                "consignee": consignee,
                "grand_total": 0
            }

        fieldname = frappe.scrub(r.item_code)

        # Item-wise pending
        result[consignee][fieldname] = result[consignee].get(fieldname, 0) + pending

        # Row total
        result[consignee]["grand_total"] += pending

        # Column totals
        column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

    data = list(result.values())

    # -------------------------------------------------
    # 4. GRAND TOTAL ROW
    # -------------------------------------------------
    if data:
        total_row = {"consignee": "Grand Total"}
        grand_total_sum = 0

        for field in column_totals:
            total_row[field] = column_totals[field]
            grand_total_sum += column_totals[field]

        total_row["grand_total"] = grand_total_sum
        data.append(total_row)

    return data