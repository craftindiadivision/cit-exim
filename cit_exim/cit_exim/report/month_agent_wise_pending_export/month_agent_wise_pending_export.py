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



# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns = get_columns()
#     data = []

#     raw_data = frappe.db.sql("""
#         SELECT 
#             ss.start_date,
#             ss.end_date,
#             so.custom_agent,
#             soi.item_code,
#             (soi.qty - IFNULL(inv.invoiced_qty,0)) AS qty

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi 
#             ON soi.parent = so.name

#         LEFT JOIN `tabShipment Schedule Child Table` ss
#             ON ss.parent = so.name

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

#         ORDER BY ss.start_date ASC
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

#         if qty <= 0:
#             continue

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



# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
#     columns, data = get_data()
#     return columns, data


# # ---------------------------------------
# # MAIN FUNCTION
# # ---------------------------------------
# def get_data():

#     records = frappe.db.sql("""
#         SELECT
#             so.name AS sales_order,
#             so.custom_agent AS agent,
#             soi.item_code,
#             soi.item_name,
#             soi.item_group,
#             css.planned_qty,
#             css.start_date,
#             css.end_date
#         FROM `tabSales Order` so
#         JOIN `tabSales Order Item` soi ON soi.parent = so.name
#         JOIN `tabShipment Schedule Child Table` css ON css.parent = so.name
#         WHERE so.docstatus = 1
#     """, as_dict=1)

#     month_map = {}
#     dynamic_columns = set()

#     # ---------------------------------------
#     # PRE-FETCH ITEM DATA
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
#     # PROCESS DATA
#     # ---------------------------------------
#     for row in records:

#         pending_qty = row.planned_qty or 0
#         if pending_qty <= 0:
#             continue

#         month = format_month(row.start_date, row.end_date)

#         # ✅ CLEAN AGENT
#         agent = (row.agent or "").strip() or "No Agent"

#         column_name = get_column_name(row, item_details)
#         dynamic_columns.add(column_name)

#         sort_key = get_sort_key(row.start_date, row.end_date)

#         # -----------------------------
#         # MONTH ROW
#         # -----------------------------
#         if month not in month_map:
#             month_map[month] = {
#                 "month_agent": month,
#                 "parent": None,
#                 "sort_key": sort_key
#             }

#         month_map[month][column_name] = month_map[month].get(column_name, 0) + pending_qty

#         # -----------------------------
#         # AGENT ROW
#         # -----------------------------
#         agent_key = f"{month}::{agent}"

#         if agent_key not in month_map:
#             month_map[agent_key] = {
#                 "month_agent": agent,
#                 "parent": month,
#                 "sort_key": sort_key
#             }

#         month_map[agent_key][column_name] = month_map[agent_key].get(column_name, 0) + pending_qty

#     # ---------------------------------------
#     # BUILD COLUMNS
#     # ---------------------------------------
#     columns = [
#         {
#             "label": "Month / Agent",
#             "fieldname": "month_agent",
#             "fieldtype": "Data",
#             "width": 250
#         }
#     ]

#     for col in sorted(dynamic_columns):
#         columns.append({
#             "label": col,
#             "fieldname": col,
#             "fieldtype": "Float",
#             "width": 150
#         })

#     # ---------------------------------------
#     # PROPER TREE ORDER
#     # ---------------------------------------
#     final_data = []

#     # Get only month rows
#     months = [k for k, v in month_map.items() if not v.get("parent")]

#     # Sort months properly
#     months.sort(key=lambda m: month_map[m].get("sort_key") or "")

#     for month in months:

#         # Add month row
#         month_row = month_map[month].copy()
#         month_row.pop("sort_key", None)
#         final_data.append(month_row)

#         # Add agents under month
#         agents = [
#             (k, v) for k, v in month_map.items()
#             if v.get("parent") == month
#         ]

#         agents.sort(key=lambda x: x[1].get("month_agent"))

#         for _, agent_row in agents:
#             agent_row = agent_row.copy()
#             agent_row.pop("sort_key", None)
#             final_data.append(agent_row)

#     return columns, final_data


# # ---------------------------------------
# # COLUMN NAME LOGIC
# # ---------------------------------------
# def get_column_name(row, item_details):

#     if row.item_group == "FG-Fish Meal":

#         item = item_details.get(row.item_code)

#         if item:
#             min_p = item.get("custom_minimum_protein_content_range")
#             max_p = item.get("custom_maximum_protein_content_range")

#             if min_p and max_p:
#                 return item.get("item_name")

#         return row.item_group or "Others"

#     return row.item_group or "Others"


# # ---------------------------------------
# # MONTH FORMAT
# # ---------------------------------------
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

#     start_month = start.strftime("%b").upper()
#     end_month = end.strftime("%b").upper()
#     year = start.strftime("%Y")

#     if start.month == end.month:
#         return f"{start_month}, {year}"
#     else:
#         return f"{start_month}-{end_month}, {year}"


# # ---------------------------------------
# # SORT KEY (FINAL FIX)
# # ---------------------------------------
# def get_sort_key(start_date, end_date):

#     # No Schedule → always last
#     if not start_date and not end_date:
#         return "9999-99-9"

#     if not start_date:
#         return "9999-99-9"

#     try:
#         start = getdate(start_date)
#         end = getdate(end_date) if end_date else start
#     except Exception:
#         return "9999-99-9"

#     base = start.strftime("%Y-%m")

#     # Same month
#     if start.month == end.month:
#         return f"{base}-1"

#     # Cross month
#     return f"{base}-2"





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
#     # GROUP BY SO ITEM (IMPORTANT)
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

#         # Sort schedules by date
#         rows.sort(key=lambda x: getdate(x.start_date) if x.start_date else getdate("2099-12-31"))

#         for row in rows:

#             planned = row.planned_qty or 0

#             # Apply FIFO
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

#             # -----------------------------
#             # NORMAL REPORT BUILD
#             # -----------------------------
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

#     return columns, final_data


# # ---------------------------------------d
# # HELPERS (same as before)
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

            # MONTH
            if month not in month_map:
                month_map[month] = {
                    "month_agent": month,
                    "parent": None,
                    "sort_key": sort_key
                }

            month_map[month][column_name] = month_map[month].get(column_name, 0) + pending_qty

            # AGENT
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

    # ✅ ADD GRAND TOTAL COLUMN
    columns.append({
        "label": "Grand Total",
        "fieldname": "grand_total",
        "fieldtype": "Float",
        "width": 150
    })

    # ---------------------------------------
    # TREE
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
    # CALCULATE GRAND TOTAL COLUMN (ROW-WISE)
    # ---------------------------------------
    for row in final_data:
        total = 0
        for col in dynamic_columns:
            total += row.get(col, 0) or 0
        row["grand_total"] = total

    # ---------------------------------------
    # ADD FINAL GRAND TOTAL ROW
    # ---------------------------------------
    grand_row = {"month_agent": "Grand Total"}

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