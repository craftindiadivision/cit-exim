# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     raw_data = frappe.db.sql("""
#         SELECT 
#             si.posting_date,
#             si.custom_shipped_on_board_date,
#             sii.item_code,
#             sii.qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1
#         AND si.status != 'Paid'
#         ORDER BY si.posting_date ASC
#     """, as_dict=1)

#     grouped = {}
#     month_order = {}

#     for d in raw_data:

#         posting_date = getdate(d.posting_date)
#         shipped_date = getdate(d.custom_shipped_on_board_date or d.posting_date)

#         posting_month = posting_date.strftime('%b').upper()
#         shipped_month = shipped_date.strftime('%b').upper()

#         if posting_month == shipped_month and posting_date.year == shipped_date.year:
#             month_label = f"{posting_month}, {posting_date.year}"
#         else:
#             month_label = f"{posting_month}-{shipped_month}, {posting_date.year}"

#         if month_label not in month_order:
#             month_order[month_label] = posting_date

#         if month_label not in grouped:
#             grouped[month_label] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label]["60"] += qty

#         elif "62" in item:
#             grouped[month_label]["62"] += qty

#         elif "65" in item:
#             grouped[month_label]["65"] += qty

#         elif "FO" in item:
#             grouped[month_label]["FO"] += qty

#         elif "FSP" in item:
#             grouped[month_label]["FSP"] += qty

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         totals = grouped[month]

#         grand_total["60"] += totals["60"]
#         grand_total["62"] += totals["62"]
#         grand_total["65"] += totals["65"]
#         grand_total["FO"] += totals["FO"]
#         grand_total["FSP"] += totals["FSP"]

#         data.append({
#             "month": f"<b>{month}</b>",
#             "fm_60": f"<b>{blank_if_zero(totals['60'])}</b>" if totals["60"] else "",
#             "fm_62": f"<b>{blank_if_zero(totals['62'])}</b>" if totals["62"] else "",
#             "fm_65": f"<b>{blank_if_zero(totals['65'])}</b>" if totals["65"] else "",
#             "fo": f"<b>{blank_if_zero(totals['FO'])}</b>" if totals["FO"] else "",
#             "fsp": f"<b>{blank_if_zero(totals['FSP'])}</b>" if totals["FSP"] else ""
#         })

#     data.append({
#         "month": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else ""
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100}
#     ]




# import frappe
# from frappe.utils import getdate, nowdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     today = getdate(nowdate())

#     raw_data = frappe.db.sql("""
#         SELECT 
#             si.posting_date,
#             si.custom_shipped_on_board_date,
#             sii.item_code,
#             sii.qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1
#         AND si.status != 'Paid'
#         ORDER BY si.posting_date ASC
#     """, as_dict=1)

#     grouped = {}
#     month_order = {}

#     for d in raw_data:

#         posting_date = getdate(d.posting_date)
#         shipped_date = getdate(d.custom_shipped_on_board_date or d.posting_date)

#         posting_month = posting_date.strftime('%b').upper()
#         shipped_month = shipped_date.strftime('%b').upper()

#         if posting_month == shipped_month and posting_date.year == shipped_date.year:
#             month_label = f"{posting_month}, {posting_date.year}"
#         else:
#             month_label = f"{posting_month}-{shipped_month}, {posting_date.year}"

#         if month_label not in month_order:
#             month_order[month_label] = posting_date

#         if month_label not in grouped:
#             grouped[month_label] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0,
#                 "remarks": ""
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label]["60"] += qty
#         elif "62" in item:
#             grouped[month_label]["62"] += qty
#         elif "65" in item:
#             grouped[month_label]["65"] += qty
#         elif "FO" in item:
#             grouped[month_label]["FO"] += qty
#         elif "FSP" in item:
#             grouped[month_label]["FSP"] += qty

#         # Remarks condition (same logic as SQL CASE)
#         if posting_date < today:
#             grouped[month_label]["remarks"] = "Delayed"
#         elif posting_date == today:
#             grouped[month_label]["remarks"] = "Delaying"

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         totals = grouped[month]

#         grand_total["60"] += totals["60"]
#         grand_total["62"] += totals["62"]
#         grand_total["65"] += totals["65"]
#         grand_total["FO"] += totals["FO"]
#         grand_total["FSP"] += totals["FSP"]

#         data.append({
#             "month": month,
#             "fm_60": blank_if_zero(totals['60']),
#             "fm_62": blank_if_zero(totals['62']),
#             "fm_65": blank_if_zero(totals['65']),
#             "fo": blank_if_zero(totals['FO']),
#             "fsp": blank_if_zero(totals['FSP']),
#             "remarks": totals["remarks"]
#         })

#     # Grand Total row (ONLY this row bold)
#     data.append({
#         "month": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
#         "remarks": ""
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100},
#         {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 120}
#     ]







# import frappe
# from frappe.utils import getdate, nowdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     today = getdate(nowdate())

#     raw_data = frappe.db.sql("""
#         SELECT 
#             si.posting_date,
#             si.custom_shipped_on_board_date,
#             soi.item_code,
#             (soi.qty - IFNULL(SUM(sii.qty),0)) AS qty

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi
#             ON soi.parent = so.name

#         LEFT JOIN `tabSales Invoice Item` sii
#             ON sii.so_detail = soi.name

#         LEFT JOIN `tabSales Invoice` si
#             ON si.name = sii.parent
#             AND si.docstatus = 1

#         WHERE so.docstatus IN (0,1)

#         GROUP BY
#             soi.name,
#             si.posting_date,
#             si.custom_shipped_on_board_date,
#             soi.item_code

#         ORDER BY si.posting_date ASC
#     """, as_dict=1)

#     grouped = {}
#     month_order = {}

#     for d in raw_data:

#         if not d.posting_date:
#             continue

#         posting_date = getdate(d.posting_date)
#         shipped_date = getdate(d.custom_shipped_on_board_date or d.posting_date)

#         posting_month = posting_date.strftime('%b').upper()
#         shipped_month = shipped_date.strftime('%b').upper()

#         if posting_month == shipped_month and posting_date.year == shipped_date.year:
#             month_label = f"{posting_month}, {posting_date.year}"
#         else:
#             month_label = f"{posting_month}-{shipped_month}, {posting_date.year}"

#         if month_label not in month_order:
#             month_order[month_label] = posting_date

#         if month_label not in grouped:
#             grouped[month_label] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0,
#                 "remarks": ""
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label]["60"] += qty
#         elif "62" in item:
#             grouped[month_label]["62"] += qty
#         elif "65" in item:
#             grouped[month_label]["65"] += qty
#         elif "FO" in item:
#             grouped[month_label]["FO"] += qty
#         elif "FSP" in item:
#             grouped[month_label]["FSP"] += qty

#         # Remarks logic
#         if posting_date < today:
#             grouped[month_label]["remarks"] = "Delayed"
#         elif posting_date == today:
#             grouped[month_label]["remarks"] = "Delaying"

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         totals = grouped[month]

#         grand_total["60"] += totals["60"]
#         grand_total["62"] += totals["62"]
#         grand_total["65"] += totals["65"]
#         grand_total["FO"] += totals["FO"]
#         grand_total["FSP"] += totals["FSP"]

#         data.append({
#             "month": month,
#             "fm_60": blank_if_zero(totals['60']),
#             "fm_62": blank_if_zero(totals['62']),
#             "fm_65": blank_if_zero(totals['65']),
#             "fo": blank_if_zero(totals['FO']),
#             "fsp": blank_if_zero(totals['FSP']),
#             "remarks": totals["remarks"]
#         })

#     data.append({
#         "month": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
#         "remarks": ""
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100},
#         {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 120}
#     ]




# import frappe
# from frappe.utils import getdate, nowdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     today = getdate(nowdate())

#     raw_data = frappe.db.sql("""
#         SELECT 
#             css.start_date,
#             css.end_date,
#             soi.item_code,
#             (soi.qty - IFNULL(inv.invoiced_qty,0)) AS qty

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi
#             ON soi.parent = so.name

#         LEFT JOIN `tabShipment Schedule Child Table` css
#             ON css.parent = so.name

#         LEFT JOIN (
#             SELECT
#                 sii.so_detail,
#                 SUM(sii.qty) AS invoiced_qty
#             FROM `tabSales Invoice Item` sii
#             JOIN `tabSales Invoice` si
#                 ON si.name = sii.parent
#             WHERE si.docstatus = 1
#             GROUP BY sii.so_detail
#         ) inv
#             ON inv.so_detail = soi.name

#         WHERE so.docstatus IN (0,1)

#         ORDER BY css.start_date ASC
#     """, as_dict=1)

#     grouped = {}
#     month_order = {}

#     for d in raw_data:

#         if not d.start_date:
#             continue

#         start_date = getdate(d.start_date)
#         end_date = getdate(d.end_date or d.start_date)

#         start_month = start_date.strftime('%b').upper()
#         end_month = end_date.strftime('%b').upper()

#         if start_month == end_month and start_date.year == end_date.year:
#             month_label = f"{start_month}, {start_date.year}"
#         else:
#             month_label = f"{start_month}-{end_month}, {start_date.year}"

#         if month_label not in month_order:
#             month_order[month_label] = start_date

#         if month_label not in grouped:
#             grouped[month_label] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0,
#                 "remarks": ""
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label]["60"] += qty
#         elif "62" in item:
#             grouped[month_label]["62"] += qty
#         elif "65" in item:
#             grouped[month_label]["65"] += qty
#         elif "FO" in item:
#             grouped[month_label]["FO"] += qty
#         elif "FSP" in item:
#             grouped[month_label]["FSP"] += qty

#         # remarks logic
#         if start_date < today:
#             grouped[month_label]["remarks"] = "Delayed"
#         elif start_date == today:
#             grouped[month_label]["remarks"] = "Delaying"

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         totals = grouped[month]

#         grand_total["60"] += totals["60"]
#         grand_total["62"] += totals["62"]
#         grand_total["65"] += totals["65"]
#         grand_total["FO"] += totals["FO"]
#         grand_total["FSP"] += totals["FSP"]

#         data.append({
#             "month": month,
#             "fm_60": blank_if_zero(totals['60']),
#             "fm_62": blank_if_zero(totals['62']),
#             "fm_65": blank_if_zero(totals['65']),
#             "fo": blank_if_zero(totals['FO']),
#             "fsp": blank_if_zero(totals['FSP']),
#             "remarks": totals["remarks"]
#         })

#     data.append({
#         "month": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
#         "remarks": ""
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100},
#         {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 120}
#     ]





import frappe
from frappe.utils import getdate
from datetime import date


def execute(filters=None):
    columns, data = get_data()
    return columns, data


def get_data():

    records = frappe.db.sql("""
        SELECT
            soi.name AS so_item,
            soi.item_code,
            soi.item_name,
            soi.item_group,
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

            column_name = get_column_name(row, item_details)
            dynamic_columns.add(column_name)

            sort_key = get_sort_key(row.start_date, row.end_date)

            # MONTH ONLY
            if month not in month_map:
                month_map[month] = {
                    "month": month,
                    "sort_key": sort_key
                }

            month_map[month][column_name] = month_map[month].get(column_name, 0) + pending_qty

    # ---------------------------------------
    # COLUMNS
    # ---------------------------------------
    columns = [{
        "label": "Month",
        "fieldname": "month",
        "fieldtype": "Data",
        "width": 200
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

    # ✅ Remarks column
    columns.append({
        "label": "Remarks",
        "fieldname": "remarks",
        "fieldtype": "Data",
        "width": 150
    })

    # ---------------------------------------
    # FINAL DATA
    # ---------------------------------------
    final_data = list(month_map.values())
    final_data.sort(key=lambda x: x.get("sort_key") or "")

    for row in final_data:
        row.pop("sort_key", None)

    # ---------------------------------------
    # ROW GRAND TOTAL
    # ---------------------------------------
    for row in final_data:
        total = 0
        for col in dynamic_columns:
            total += row.get(col, 0) or 0
        row["grand_total"] = total

    # ---------------------------------------
    # REMARKS LOGIC (DELAY STATUS)
    # ---------------------------------------
    today = date.today()
    current_year = today.year
    current_month = today.month

    for row in final_data:

        month_label = row.get("month")

        if not month_label:
            row["remarks"] = ""
            continue

        try:
            parts = month_label.replace(",", "").split()

            month_part = parts[0]   # JAN or JAN-MAR
            year = int(parts[1])

            if "-" in month_part:
                start_m = month_part.split("-")[0]
            else:
                start_m = month_part

            month_number = list_months().index(start_m) + 1

            if year < current_year or (year == current_year and month_number < current_month):
                row["remarks"] = "Delayed"
            elif year == current_year and month_number == current_month:
                row["remarks"] = "Delaying"
            else:
                row["remarks"] = ""

        except Exception:
            row["remarks"] = ""

    # ---------------------------------------
    # FINAL GRAND TOTAL ROW
    # ---------------------------------------
    grand_row = {"month": "Grand Total", "remarks": ""}

    for col in dynamic_columns:
        grand_row[col] = sum(r.get(col, 0) or 0 for r in final_data)

    grand_row["grand_total"] = sum(r.get("grand_total", 0) or 0 for r in final_data)

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


def list_months():
    return [
        "JAN","FEB","MAR","APR","MAY","JUN",
        "JUL","AUG","SEP","OCT","NOV","DEC"
    ]