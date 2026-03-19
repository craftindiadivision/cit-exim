# # Copyright (c) 2026, craft and contributors
# # For license information, please see license.txt




# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns, data = get_data()
#     return columns, data


# def get_data():

#     records = frappe.db.sql("""
#         SELECT
#             so.name AS sales_order,
#             so.custom_agent AS agent,
#             soi.name AS so_item,
#             soi.item_code,
#             soi.item_name,
#             soi.item_group,
#             css.name AS schedule_row,
#             css.planned_qty,
#             css.start_date,
#             css.end_date
#         FROM `tabSales Order` so
#         JOIN `tabSales Order Item` soi ON soi.parent = so.name
#         JOIN `tabShipment Schedule Child Table` css ON css.parent = so.name
#         WHERE so.docstatus = 1
#         ORDER BY soi.name, css.start_date
#     """, as_dict=1)

#     # ---------------------------------------
#     # FETCH INVOICED QTY
#     # ---------------------------------------
#     invoiced_data = frappe.db.sql("""
#         SELECT
#             sii.so_detail,
#             SUM(sii.qty) AS invoiced_qty
#         FROM `tabSales Invoice Item` sii
#         JOIN `tabSales Invoice` si ON si.name = sii.parent
#         WHERE si.docstatus = 1
#         GROUP BY sii.so_detail
#     """, as_dict=1)

#     invoiced_map = {d.so_detail: d.invoiced_qty for d in invoiced_data}

#     # ---------------------------------------
#     # GROUP BY SO ITEM
#     # ---------------------------------------
#     grouped = {}
#     for row in records:
#         grouped.setdefault(row.so_item, []).append(row)

#     month_map = {}
#     dynamic_columns = set()

#     # ---------------------------------------
#     # ITEM DETAILS
#     # ---------------------------------------
#     item_codes = list({row.item_code for row in records if row.item_code})

#     item_details = {}
#     if item_codes:
#         items = frappe.get_all(
#             "Item",
#             filters={"name": ["in", item_codes]},
#             fields=[
#                 "name",
#                 "item_name",
#                 "custom_minimum_protein_content_range",
#                 "custom_maximum_protein_content_range"
#             ]
#         )
#         item_details = {item.name: item for item in items}

#     # ---------------------------------------
#     # FIFO DISTRIBUTION
#     # ---------------------------------------
#     for so_item, rows in grouped.items():

#         invoiced_qty = invoiced_map.get(so_item, 0) or 0

#         rows.sort(key=lambda x: getdate(x.start_date) if x.start_date else getdate("2099-12-31"))

#         for row in rows:

#             planned = row.planned_qty or 0

#             if invoiced_qty > 0:
#                 if invoiced_qty >= planned:
#                     invoiced_qty -= planned
#                     pending_qty = 0
#                 else:
#                     pending_qty = planned - invoiced_qty
#                     invoiced_qty = 0
#             else:
#                 pending_qty = planned

#             if pending_qty <= 0:
#                 continue

#             month = format_month(row.start_date, row.end_date)
#             agent = (row.agent or "").strip() or "No Agent"

#             column_name = get_column_name(row, item_details)
#             dynamic_columns.add(column_name)

#             sort_key = get_sort_key(row.start_date, row.end_date)

#             # MONTH
#             if month not in month_map:
#                 month_map[month] = {
#                     "month_agent": month,
#                     "parent": None,
#                     "sort_key": sort_key
#                 }

#             month_map[month][column_name] = month_map[month].get(column_name, 0) + pending_qty

#             # AGENT
#             agent_key = f"{month}::{agent}"

#             if agent_key not in month_map:
#                 month_map[agent_key] = {
#                     "month_agent": agent,
#                     "parent": month,
#                     "sort_key": sort_key
#                 }

#             month_map[agent_key][column_name] = month_map[agent_key].get(column_name, 0) + pending_qty

#     # ---------------------------------------
#     # COLUMNS
#     # ---------------------------------------
#     columns = [{
#         "label": "Month / Agent",
#         "fieldname": "month_agent",
#         "fieldtype": "Data",
#         "width": 250
#     }]

#     for col in sorted(dynamic_columns):
#         columns.append({
#             "label": col,
#             "fieldname": col,
#             "fieldtype": "Float",
#             "width": 150
#         })

#     # ✅ ADD GRAND TOTAL COLUMN
#     columns.append({
#         "label": "Grand Total",
#         "fieldname": "grand_total",
#         "fieldtype": "Float",
#         "width": 150
#     })

#     # ---------------------------------------
#     # TREE
#     # ---------------------------------------
#     final_data = []

#     months = [k for k, v in month_map.items() if not v.get("parent")]
#     months.sort(key=lambda m: month_map[m].get("sort_key") or "")

#     for month in months:

#         row = month_map[month].copy()
#         row.pop("sort_key", None)
#         final_data.append(row)

#         agents = [
#             v for v in month_map.values()
#             if v.get("parent") == month
#         ]

#         agents.sort(key=lambda x: x.get("month_agent"))

#         for a in agents:
#             a = a.copy()
#             a.pop("sort_key", None)
#             final_data.append(a)

#     # ---------------------------------------
#     # CALCULATE GRAND TOTAL COLUMN (ROW-WISE)
#     # ---------------------------------------
#     for row in final_data:
#         total = 0
#         for col in dynamic_columns:
#             total += row.get(col, 0) or 0
#         row["grand_total"] = total

#     # ---------------------------------------
#     # ADD FINAL GRAND TOTAL ROW
#     # ---------------------------------------
#     grand_row = {"month_agent": "Grand Total"}

#     for col in dynamic_columns:
#         grand_row[col] = sum(r.get(col, 0) or 0 for r in final_data)

#     grand_row["grand_total"] = sum(r.get("grand_total", 0) or 0 for r in final_data)

#     final_data.append(grand_row)

#     return columns, final_data


# # ---------------------------------------
# # HELPERS
# # ---------------------------------------
# def get_column_name(row, item_details):

#     if row.item_group == "FG-Fish Meal":
#         item = item_details.get(row.item_code)

#         if item:
#             if item.get("custom_minimum_protein_content_range") and item.get("custom_maximum_protein_content_range"):
#                 return item.get("item_name")

#         return row.item_group or "Others"

#     return row.item_group or "Others"


# def format_month(start_date, end_date):

#     if not start_date and not end_date:
#         return "No Schedule"

#     if not start_date:
#         start_date = end_date

#     if not end_date:
#         end_date = start_date

#     try:
#         start = getdate(start_date)
#         end = getdate(end_date)
#     except Exception:
#         return "Invalid Date"

#     sm = start.strftime("%b").upper()
#     em = end.strftime("%b").upper()
#     year = start.strftime("%Y")

#     if start.month == end.month:
#         return f"{sm}, {year}"
#     else:
#         return f"{sm}-{em}, {year}"


# def get_sort_key(start_date, end_date):

#     if not start_date:
#         return "9999-99"

#     try:
#         start = getdate(start_date)
#         end = getdate(end_date) if end_date else start
#     except Exception:
#         return "9999-99"

#     base = start.strftime("%Y-%m")

#     if start.month == end.month:
#         return f"{base}-1"
#     return f"{base}-2"







import frappe
from frappe.utils import getdate


def execute(filters=None):
    columns, data = get_data()
    return columns, data


def get_data():

    records = frappe.db.sql("""
        SELECT
            so.name AS sales_order,
            so.custom_agent AS agent,
            soi.name AS so_item,
            soi.item_code,
            soi.item_name,
            soi.item_group,
            css.name AS schedule_row,
            css.planned_qty,
            css.start_date,
            css.end_date
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi ON soi.parent = so.name
        JOIN `tabShipment Schedule Child Table` css ON css.parent = so.name
        WHERE so.docstatus = 1
        ORDER BY soi.name, css.start_date
    """, as_dict=1)

    # ---------------------------------------
    # FETCH INVOICED QTY
    # ---------------------------------------
    invoiced_data = frappe.db.sql("""
        SELECT
            sii.so_detail,
            SUM(sii.qty) AS invoiced_qty
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
        GROUP BY sii.so_detail
    """, as_dict=1)

    invoiced_map = {d.so_detail: d.invoiced_qty for d in invoiced_data}

    # ---------------------------------------
    # GROUP BY SO ITEM
    # ---------------------------------------
    grouped = {}
    for row in records:
        grouped.setdefault(row.so_item, []).append(row)

    month_map = {}
    dynamic_columns = set()

    # ---------------------------------------
    # ITEM DETAILS
    # ---------------------------------------
    item_codes = list({row.item_code for row in records if row.item_code})

    item_details = {}
    if item_codes:
        items = frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=[
                "name",
                "item_name",
                "custom_minimum_protein_content_range",
                "custom_maximum_protein_content_range"
            ]
        )
        item_details = {item.name: item for item in items}

    # ---------------------------------------
    # FIFO DISTRIBUTION
    # ---------------------------------------
    for so_item, rows in grouped.items():

        invoiced_qty = invoiced_map.get(so_item, 0) or 0

        rows.sort(key=lambda x: getdate(x.start_date) if x.start_date else getdate("2099-12-31"))

        for row in rows:

            planned = row.planned_qty or 0

            if invoiced_qty > 0:
                if invoiced_qty >= planned:
                    invoiced_qty -= planned
                    pending_qty = 0
                else:
                    pending_qty = planned - invoiced_qty
                    invoiced_qty = 0
            else:
                pending_qty = planned

            if pending_qty <= 0:
                continue

            month = format_month(row.start_date, row.end_date)
            agent = (row.agent or "").strip() or "No Agent"

            column_name = get_column_name(row, item_details)
            dynamic_columns.add(column_name)

            sort_key = get_sort_key(row.start_date, row.end_date)

            # MONTH ROW
            if month not in month_map:
                month_map[month] = {
                    "month_agent": month,
                    "parent": None,
                    "sort_key": sort_key
                }

            month_map[month][column_name] = month_map[month].get(column_name, 0) + pending_qty

            # AGENT ROW
            agent_key = f"{month}::{agent}"

            if agent_key not in month_map:
                month_map[agent_key] = {
                    "month_agent": agent,
                    "parent": month,
                    "sort_key": sort_key
                }

            month_map[agent_key][column_name] = month_map[agent_key].get(column_name, 0) + pending_qty

    # ---------------------------------------
    # COLUMNS
    # ---------------------------------------
    columns = [{
        "label": "Month / Agent",
        "fieldname": "month_agent",
        "fieldtype": "Data",
        "width": 250
    }]

    for col in sorted(dynamic_columns):
        columns.append({
            "label": col,
            "fieldname": col,
            "fieldtype": "Float",
            "width": 150
        })

    columns.append({
        "label": "Grand Total",
        "fieldname": "grand_total",
        "fieldtype": "Float",
        "width": 150
    })

    # ---------------------------------------
    # BUILD TREE DATA
    # ---------------------------------------
    final_data = []

    months = [k for k, v in month_map.items() if not v.get("parent")]
    months.sort(key=lambda m: month_map[m].get("sort_key") or "")

    for month in months:

        row = month_map[month].copy()
        row.pop("sort_key", None)
        final_data.append(row)

        agents = [
            v for v in month_map.values()
            if v.get("parent") == month
        ]

        agents.sort(key=lambda x: x.get("month_agent"))

        for a in agents:
            a = a.copy()
            a.pop("sort_key", None)
            final_data.append(a)

    # ---------------------------------------
    # ROW-WISE GRAND TOTAL
    # ---------------------------------------
    for row in final_data:
        total = 0
        for col in dynamic_columns:
            total += row.get(col, 0) or 0
        row["grand_total"] = total

    # ---------------------------------------
    # FINAL GRAND TOTAL ROW (FIXED)
    # ---------------------------------------
    grand_row = {"month_agent": "Grand Total"}

    # ✅ ONLY MONTH ROWS (NO AGENTS)
    parent_rows = [r for r in final_data if not r.get("parent")]

    for col in dynamic_columns:
        grand_row[col] = sum(r.get(col, 0) or 0 for r in parent_rows)

    grand_row["grand_total"] = sum(r.get("grand_total", 0) or 0 for r in parent_rows)

    final_data.append(grand_row)

    return columns, final_data


# ---------------------------------------
# HELPERS
# ---------------------------------------
def get_column_name(row, item_details):

    if row.item_group == "FG-Fish Meal":
        item = item_details.get(row.item_code)

        if item:
            if item.get("custom_minimum_protein_content_range") and item.get("custom_maximum_protein_content_range"):
                return item.get("item_name")

        return row.item_group or "Others"

    return row.item_group or "Others"


def format_month(start_date, end_date):

    if not start_date and not end_date:
        return "No Schedule"

    if not start_date:
        start_date = end_date

    if not end_date:
        end_date = start_date

    try:
        start = getdate(start_date)
        end = getdate(end_date)
    except Exception:
        return "Invalid Date"

    sm = start.strftime("%b").upper()
    em = end.strftime("%b").upper()
    year = start.strftime("%Y")

    if start.month == end.month:
        return f"{sm}, {year}"
    else:
        return f"{sm}-{em}, {year}"


def get_sort_key(start_date, end_date):

    if not start_date:
        return "9999-99"

    try:
        start = getdate(start_date)
        end = getdate(end_date) if end_date else start
    except Exception:
        return "9999-99"

    base = start.strftime("%Y-%m")

    if start.month == end.month:
        return f"{base}-1"
    return f"{base}-2"