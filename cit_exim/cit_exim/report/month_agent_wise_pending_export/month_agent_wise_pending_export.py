# # Copyright (c) 2026, craft and contributors
# # For license information, please see license.txt

# # import frappe


# # def execute(filters=None):
# # 	columns, data = [], []
# # 	return columns, data

# import frappe
# from frappe.utils import getdate

# def execute(filters=None):
#     columns = get_columns()
#     data = []
    
#     # Fetch joined data: Invoice + Items
#     # Filtering for docstatus 1 and status != Paid
#     raw_data = frappe.db.sql("""
#         SELECT 
#             si.posting_date, 
#             si.custom_shipped_on_board_date, 
#             si.custom_agent,
#             sii.item_code,
#             sii.qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1 
#           AND si.status != 'Paid'
#         ORDER BY si.posting_date DESC
#     """, as_dict=1)

#     # Dictionary to hold grouped totals: { "MAR, 2026": { "Agent Name": { "FM 60%": 0, ... } } }
#     grouped = {}

#     for d in raw_data:
#         # --- Month Logic ---
#         p_date = getdate(d.posting_date)
#         s_date = getdate(d.custom_shipped_on_board_date or d.posting_date)
#         p_month = p_date.strftime('%b').upper()
#         s_month = s_date.strftime('%b').upper()
        
#         if p_month == s_month and p_date.year == s_date.year:
#             month_label = f"{p_month}, {p_date.year}"
#         else:
#             month_label = f"{p_month}-{s_month}, {p_date.year}"

#         # Initialize Month and Agent in dictionary
#         if month_label not in grouped:
#             grouped[month_label] = {}
        
#         agent = d.custom_agent or "NO AGENT"
#         if agent not in grouped[month_label]:
#             grouped[month_label][agent] = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#         # --- Aggregate Quantities based on Item Code ---
#         item = d.item_code or ""
#         qty = d.qty or 0
        
#         if "60" in item: grouped[month_label][agent]["60"] += qty
#         elif "62" in item: grouped[month_label][agent]["62"] += qty
#         elif "65" in item: grouped[month_label][agent]["65"] += qty
#         elif "FO" in item: grouped[month_label][agent]["FO"] += qty
#         elif "FSP" in item: grouped[month_label][agent]["FSP"] += qty

#     # --- Format Data for Report Grid ---
#     for month in grouped:
#         # Parent Row: Month
#         data.append({
#             "month_agent": f"<b>{month}</b>",
#             "indent": 0
#         })
        
#         for agent, totals in grouped[month].items():
#             # Child Row: Agent + Totals
#             data.append({
#                 "month_agent": agent,
#                 "fm_60": totals["60"],
#                 "fm_62": totals["62"],
#                 "fm_65": totals["65"],
#                 "fo": totals["FO"],
#                 "fsp": totals["FSP"],
#                 "indent": 1
#             })

#     return columns, data

# def get_columns():
#     return [
#         {"label": "Month / Agent", "fieldname": "month_agent", "fieldtype": "Data", "width": 200},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Float", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Float", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Float", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Float", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Float", "width": 100}
#     ]

# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt
# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     raw_data = frappe.db.sql("""
#         SELECT 
#             si.posting_date,
#             si.custom_shipped_on_board_date,
#             si.custom_agent,
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
#             grouped[month_label] = {}

#         agent = d.custom_agent or "NO AGENT"

#         if agent not in grouped[month_label]:
#             grouped[month_label][agent] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label][agent]["60"] += qty
#         elif "62" in item:
#             grouped[month_label][agent]["62"] += qty
#         elif "65" in item:
#             grouped[month_label][agent]["65"] += qty
#         elif "FO" in item:
#             grouped[month_label][agent]["FO"] += qty
#         elif "FSP" in item:
#             grouped[month_label][agent]["FSP"] += qty

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     # GRAND TOTAL INITIALIZE
#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         month_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#         for agent, totals in grouped[month].items():
#             month_total["60"] += totals["60"]
#             month_total["62"] += totals["62"]
#             month_total["65"] += totals["65"]
#             month_total["FO"] += totals["FO"]
#             month_total["FSP"] += totals["FSP"]

#         # ADD TO GRAND TOTAL
#         grand_total["60"] += month_total["60"]
#         grand_total["62"] += month_total["62"]
#         grand_total["65"] += month_total["65"]
#         grand_total["FO"] += month_total["FO"]
#         grand_total["FSP"] += month_total["FSP"]

#         # MONTH ROW
#         data.append({
#             "month_agent": f"<b>{month}</b>",
#             "fm_60": f"<b>{blank_if_zero(month_total['60'])}</b>" if month_total["60"] else "",
#             "fm_62": f"<b>{blank_if_zero(month_total['62'])}</b>" if month_total["62"] else "",
#             "fm_65": f"<b>{blank_if_zero(month_total['65'])}</b>" if month_total["65"] else "",
#             "fo": f"<b>{blank_if_zero(month_total['FO'])}</b>" if month_total["FO"] else "",
#             "fsp": f"<b>{blank_if_zero(month_total['FSP'])}</b>" if month_total["FSP"] else "",
#             "indent": 0
#         })

#         # AGENT ROWS
#         for agent, totals in grouped[month].items():
#             data.append({
#                 "month_agent": agent,
#                 "fm_60": blank_if_zero(totals["60"]),
#                 "fm_62": blank_if_zero(totals["62"]),
#                 "fm_65": blank_if_zero(totals["65"]),
#                 "fo": blank_if_zero(totals["FO"]),
#                 "fsp": blank_if_zero(totals["FSP"]),
#                 "indent": 1
#             })

#     # GRAND TOTAL ROW
#     data.append({
#         "month_agent": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
#         "indent": 0
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month / Agent", "fieldname": "month_agent", "fieldtype": "Data", "width": 220},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100}
#     ]






# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     raw_data = frappe.db.sql("""
#         SELECT 
#             COALESCE(si.posting_date, so.transaction_date) AS posting_date,
#             si.custom_shipped_on_board_date,
#             so.custom_agent,
#             soi.item_code,
#             (soi.qty - IFNULL(inv.invoiced_qty,0)) AS qty

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi 
#             ON soi.parent = so.name

#         LEFT JOIN (
#             SELECT
#                 sii.so_detail,
#                 SUM(sii.qty) AS invoiced_qty,
#                 MAX(si.posting_date) AS posting_date,
#                 MAX(si.custom_shipped_on_board_date) AS custom_shipped_on_board_date
#             FROM `tabSales Invoice Item` sii
#             JOIN `tabSales Invoice` si 
#                 ON si.name = sii.parent
#             WHERE si.docstatus = 1
#             GROUP BY sii.so_detail
#         ) inv
#             ON inv.so_detail = soi.name

#         LEFT JOIN `tabSales Invoice` si
#             ON si.posting_date = inv.posting_date

#         WHERE so.docstatus IN (0,1)

#         ORDER BY posting_date ASC
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
#             grouped[month_label] = {}

#         agent = d.custom_agent or "NO AGENT"

#         if agent not in grouped[month_label]:
#             grouped[month_label][agent] = {
#                 "60": 0,
#                 "62": 0,
#                 "65": 0,
#                 "FO": 0,
#                 "FSP": 0
#             }

#         item = d.item_code or ""
#         qty = d.qty or 0

#         if "60" in item:
#             grouped[month_label][agent]["60"] += qty
#         elif "62" in item:
#             grouped[month_label][agent]["62"] += qty
#         elif "65" in item:
#             grouped[month_label][agent]["65"] += qty
#         elif "FO" in item:
#             grouped[month_label][agent]["FO"] += qty
#         elif "FSP" in item:
#             grouped[month_label][agent]["FSP"] += qty

#     sorted_months = sorted(month_order, key=lambda x: month_order[x])

#     grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#     for month in sorted_months:

#         month_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

#         for agent, totals in grouped[month].items():
#             month_total["60"] += totals["60"]
#             month_total["62"] += totals["62"]
#             month_total["65"] += totals["65"]
#             month_total["FO"] += totals["FO"]
#             month_total["FSP"] += totals["FSP"]

#         grand_total["60"] += month_total["60"]
#         grand_total["62"] += month_total["62"]
#         grand_total["65"] += month_total["65"]
#         grand_total["FO"] += month_total["FO"]
#         grand_total["FSP"] += month_total["FSP"]

#         data.append({
#             "month_agent": f"<b>{month}</b>",
#             "fm_60": f"<b>{blank_if_zero(month_total['60'])}</b>" if month_total["60"] else "",
#             "fm_62": f"<b>{blank_if_zero(month_total['62'])}</b>" if month_total["62"] else "",
#             "fm_65": f"<b>{blank_if_zero(month_total['65'])}</b>" if month_total["65"] else "",
#             "fo": f"<b>{blank_if_zero(month_total['FO'])}</b>" if month_total["FO"] else "",
#             "fsp": f"<b>{blank_if_zero(month_total['FSP'])}</b>" if month_total["FSP"] else "",
#             "indent": 0
#         })

#         for agent, totals in grouped[month].items():
#             data.append({
#                 "month_agent": agent,
#                 "fm_60": blank_if_zero(totals["60"]),
#                 "fm_62": blank_if_zero(totals["62"]),
#                 "fm_65": blank_if_zero(totals["65"]),
#                 "fo": blank_if_zero(totals["FO"]),
#                 "fsp": blank_if_zero(totals["FSP"]),
#                 "indent": 1
#             })

#     data.append({
#         "month_agent": "<b>Grand Total</b>",
#         "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
#         "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
#         "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
#         "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
#         "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
#         "indent": 0
#     })

#     return columns, data


# def blank_if_zero(value):
#     return "" if value == 0 else value


# def get_columns():
#     return [
#         {"label": "Month / Agent", "fieldname": "month_agent", "fieldtype": "Data", "width": 220},
#         {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
#         {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
#         {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
#         {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
#         {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100}
#     ]



import frappe
from frappe.utils import getdate


def execute(filters=None):
    columns = get_columns()
    data = []

    raw_data = frappe.db.sql("""
        SELECT 
            ss.start_date,
            ss.end_date,
            so.custom_agent,
            soi.item_code,
            (soi.qty - IFNULL(inv.invoiced_qty,0)) AS qty

        FROM `tabSales Order` so

        JOIN `tabSales Order Item` soi 
            ON soi.parent = so.name

        LEFT JOIN `tabShipment Schedule Child Table` ss
            ON ss.parent = so.name

        LEFT JOIN (
            SELECT
                sii.so_detail,
                SUM(sii.qty) AS invoiced_qty
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si 
                ON si.name = sii.parent
            WHERE si.docstatus = 1
            GROUP BY sii.so_detail
        ) inv
            ON inv.so_detail = soi.name

        WHERE so.docstatus IN (0,1)

        ORDER BY ss.start_date ASC
    """, as_dict=1)

    grouped = {}
    month_order = {}

    for d in raw_data:

        if not d.start_date:
            continue

        start_date = getdate(d.start_date)
        end_date = getdate(d.end_date or d.start_date)

        start_month = start_date.strftime('%b').upper()
        end_month = end_date.strftime('%b').upper()

        if start_month == end_month and start_date.year == end_date.year:
            month_label = f"{start_month}, {start_date.year}"
        else:
            month_label = f"{start_month}-{end_month}, {start_date.year}"

        if month_label not in month_order:
            month_order[month_label] = start_date

        if month_label not in grouped:
            grouped[month_label] = {}

        agent = d.custom_agent or "NO AGENT"

        if agent not in grouped[month_label]:
            grouped[month_label][agent] = {
                "60": 0,
                "62": 0,
                "65": 0,
                "FO": 0,
                "FSP": 0
            }

        item = d.item_code or ""
        qty = d.qty or 0

        if qty <= 0:
            continue

        if "60" in item:
            grouped[month_label][agent]["60"] += qty
        elif "62" in item:
            grouped[month_label][agent]["62"] += qty
        elif "65" in item:
            grouped[month_label][agent]["65"] += qty
        elif "FO" in item:
            grouped[month_label][agent]["FO"] += qty
        elif "FSP" in item:
            grouped[month_label][agent]["FSP"] += qty

    sorted_months = sorted(month_order, key=lambda x: month_order[x])

    grand_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

    for month in sorted_months:

        month_total = {"60": 0, "62": 0, "65": 0, "FO": 0, "FSP": 0}

        for agent, totals in grouped[month].items():
            month_total["60"] += totals["60"]
            month_total["62"] += totals["62"]
            month_total["65"] += totals["65"]
            month_total["FO"] += totals["FO"]
            month_total["FSP"] += totals["FSP"]

        grand_total["60"] += month_total["60"]
        grand_total["62"] += month_total["62"]
        grand_total["65"] += month_total["65"]
        grand_total["FO"] += month_total["FO"]
        grand_total["FSP"] += month_total["FSP"]

        data.append({
            "month_agent": f"<b>{month}</b>",
            "fm_60": f"<b>{blank_if_zero(month_total['60'])}</b>" if month_total["60"] else "",
            "fm_62": f"<b>{blank_if_zero(month_total['62'])}</b>" if month_total["62"] else "",
            "fm_65": f"<b>{blank_if_zero(month_total['65'])}</b>" if month_total["65"] else "",
            "fo": f"<b>{blank_if_zero(month_total['FO'])}</b>" if month_total["FO"] else "",
            "fsp": f"<b>{blank_if_zero(month_total['FSP'])}</b>" if month_total["FSP"] else "",
            "indent": 0
        })

        for agent, totals in grouped[month].items():
            data.append({
                "month_agent": agent,
                "fm_60": blank_if_zero(totals["60"]),
                "fm_62": blank_if_zero(totals["62"]),
                "fm_65": blank_if_zero(totals["65"]),
                "fo": blank_if_zero(totals["FO"]),
                "fsp": blank_if_zero(totals["FSP"]),
                "indent": 1
            })

    data.append({
        "month_agent": "<b>Grand Total</b>",
        "fm_60": f"<b>{blank_if_zero(grand_total['60'])}</b>" if grand_total["60"] else "",
        "fm_62": f"<b>{blank_if_zero(grand_total['62'])}</b>" if grand_total["62"] else "",
        "fm_65": f"<b>{blank_if_zero(grand_total['65'])}</b>" if grand_total["65"] else "",
        "fo": f"<b>{blank_if_zero(grand_total['FO'])}</b>" if grand_total["FO"] else "",
        "fsp": f"<b>{blank_if_zero(grand_total['FSP'])}</b>" if grand_total["FSP"] else "",
        "indent": 0
    })

    return columns, data


def blank_if_zero(value):
    return "" if value == 0 else value


def get_columns():
    return [
        {"label": "Month / Agent", "fieldname": "month_agent", "fieldtype": "Data", "width": 220},
        {"label": "FM 60%", "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
        {"label": "FM 62%", "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
        {"label": "FM 65%", "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
        {"label": "FO", "fieldname": "fo", "fieldtype": "Data", "width": 100},
        {"label": "FSP", "fieldname": "fsp", "fieldtype": "Data", "width": 100}
    ]