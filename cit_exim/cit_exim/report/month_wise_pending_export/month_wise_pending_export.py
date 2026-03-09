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




import frappe
from frappe.utils import getdate, nowdate


def execute(filters=None):
    columns = get_columns()
    data = []

    today = getdate(nowdate())

    raw_data = frappe.db.sql("""
        SELECT 
            si.posting_date,
            si.custom_shipped_on_board_date,
            sii.item_code,
            sii.qty
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1
        AND si.status != 'Paid'
        ORDER BY si.posting_date ASC
    """, as_dict=1)

    grouped = {}
    month_order = {}

    for d in raw_data:

        posting_date = getdate(d.posting_date)
        shipped_date = getdate(d.custom_shipped_on_board_date or d.posting_date)

        posting_month = posting_date.strftime('%b').upper()
        shipped_month = shipped_date.strftime('%b').upper()

        if posting_month == shipped_month and posting_date.year == shipped_date.year:
            month_label = f"{posting_month}, {posting_date.year}"
        else:
            month_label = f"{posting_month}-{shipped_month}, {posting_date.year}"

        if month_label not in month_order:
            month_order[month_label] = posting_date

        if month_label not in grouped:
            grouped[month_label] = {
                "60": 0,
                "62": 0,
                "65": 0,
                "FO": 0,
                "FSP": 0,
                "remarks": ""
            }

        item = d.item_code or ""
        qty = d.qty or 0

        if "60" in item:
            grouped[month_label]["60"] += qty
        elif "62" in item:
            grouped[month_label]["62"] += qty
        elif "65" in item:
            grouped[month_label]["65"] += qty
        elif "FO" in item:
            grouped[month_label]["FO"] += qty
        elif "FSP" in item:
            grouped[month_label]["FSP"] += qty

        # Remarks condition (same logic as SQL CASE)
        if posting_date < today:
            grouped[month_label]["remarks"] = "Delayed"
        elif posting_date == today:
            grouped[month_label]["remarks"] = "Delaying"

    sorted_months = sorted(month_order, key=lambda x: month_order[x])

    grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

    for month in sorted_months:

        totals = grouped[month]

        grand_total["60"] += totals["60"]
        grand_total["62"] += totals["62"]
        grand_total["65"] += totals["65"]
        grand_total["FO"] += totals["FO"]
        grand_total["FSP"] += totals["FSP"]

        data.append({
            "month": month,
            "fm_60": blank_if_zero(totals['60']),
            "fm_62": blank_if_zero(totals['62']),
            "fm_65": blank_if_zero(totals['65']),
            "fo": blank_if_zero(totals['FO']),
            "fsp": blank_if_zero(totals['FSP']),
            "remarks": totals["remarks"]
        })

    # Grand Total row (ONLY this row bold)
    data.append({
        "month": "<b>Grand Total</b>",
        "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
        "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
        "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
        "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
        "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
        "remarks": ""
    })

    return columns, data


def blank_if_zero(value):
    return "" if value == 0 else value


def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 200},
        {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
        {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
        {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
        {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
        {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 120}
    ]