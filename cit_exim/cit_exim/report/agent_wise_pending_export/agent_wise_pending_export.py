# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



# import frappe
# from frappe import _

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Link", "options": "Supplier", "width": 150},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Float", "width": 100},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Float", "width": 100},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Float", "width": 100},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Float", "width": 100},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Float", "width": 100},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Float", "width": 120},
#     ]

# def get_data(filters):
#     conditions = ""
    
#     # 1. Filter by Agent (Supplier)
#     if filters.get("agent"):
#         conditions += " AND si.custom_agent = %(agent)s"
    
#     # 2. Filter by Date Range
#     if filters.get("from_date"):
#         conditions += " AND si.posting_date >= %(from_date)s"
    
#     if filters.get("to_date"):
#         conditions += " AND si.posting_date <= %(to_date)s"

#     query = f"""
#         SELECT
#             si.custom_agent AS agent,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.qty ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.qty ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.qty ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.qty ELSE 0 END) AS fo,
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.qty ELSE 0 END) AS fsp,
#             SUM(CASE WHEN sii.item_group = 'FG-Fish Meal' THEN sii.qty ELSE 0 END) AS grand_total
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE
#             si.docstatus = 1
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             AND si.custom_agent IS NOT NULL
#             AND si.custom_agent != ''
#             {conditions}
#         GROUP BY
#             si.custom_agent
#     """
    
#     return frappe.db.sql(query, filters, as_dict=True)




# import frappe
# from frappe import _
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters: filters = {}
    
#     columns = get_columns()
#     data = get_data(filters)
    
#     # Calculate and append the bold Grand Total row
#     if data:
#         total_row = calculate_totals(data)
#         data.append(total_row)
        
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 110},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 110},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 110},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 110},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 110},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 140},
#     ]

# def get_data(filters):
#     conditions = ""
#     if filters.get("agent"):
#         conditions += " AND si.custom_agent = %(agent)s"
#     if filters.get("from_date"):
#         conditions += " AND si.posting_date >= %(from_date)s"
#     if filters.get("to_date"):
#         conditions += " AND si.posting_date <= %(to_date)s"

#     query = f"""
#         SELECT
#             si.custom_agent AS agent,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.qty ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.qty ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.qty ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.qty ELSE 0 END) AS fo,
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.qty ELSE 0 END) AS fsp,
#             SUM(CASE WHEN sii.item_group = 'FG-Fish Meal' THEN sii.qty ELSE 0 END) AS grand_total
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE
#             si.docstatus = 1
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             AND si.custom_agent IS NOT NULL
#             AND si.custom_agent != ''
#             {conditions}
#         GROUP BY
#             si.custom_agent
#         ORDER BY 
#             si.custom_agent ASC
#     """
#     return frappe.db.sql(query, filters, as_dict=True)

# def calculate_totals(data):
#     # Temp counters
#     sum_fm_60 = 0.0
#     sum_fm_62 = 0.0
#     sum_fm_65 = 0.0
#     sum_fo = 0.0
#     sum_fsp = 0.0
#     sum_grand = 0.0
    
#     for row in data:
#         sum_fm_60 += flt(row.get("fm_60", 0))
#         sum_fm_62 += flt(row.get("fm_62", 0))
#         sum_fm_65 += flt(row.get("fm_65", 0))
#         sum_fo += flt(row.get("fo", 0))
#         sum_fsp += flt(row.get("fsp", 0))
#         sum_grand += flt(row.get("grand_total", 0))
        
#     # Create the bold row
#     # We use f-strings to wrap the numbers in <b> tags
#     totals = {
#         "agent": f"<b>{_('Grand Total')}</b>",
#         "fm_60": f"<b>{sum_fm_60:,.2f}</b>",
#         "fm_62": f"<b>{sum_fm_62:,.2f}</b>",
#         "fm_65": f"<b>{sum_fm_65:,.2f}</b>",
#         "fo": f"<b>{sum_fo:,.2f}</b>",
#         "fsp": f"<b>{sum_fsp:,.2f}</b>",
#         "grand_total": f"<b>{sum_grand:,.2f}</b>"
#     }
    
#     return totals





import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    raw_data = get_data(filters)

    data = []

    # Format normal rows
    for row in raw_data:
        format_row(row)
        data.append(row)

    # Add Grand Total row
    if data:
        total_row = calculate_totals(data)
        data.append(total_row)  # removed format_row(total_row)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Agent"),
            "fieldname": "agent",
            "fieldtype": "Data",
            "width": 180
        },
        {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 110},
        {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 110},
        {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 110},
        {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 110},
        {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 110},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 140},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("agent"):
        conditions += " AND si.custom_agent = %(agent)s"

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"

    query = f"""
        SELECT
            si.custom_agent AS agent,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.qty ELSE 0 END) AS fm_60,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.qty ELSE 0 END) AS fm_62,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.qty ELSE 0 END) AS fm_65,
            SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.qty ELSE 0 END) AS fo,
            SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.qty ELSE 0 END) AS fsp,
            SUM(CASE WHEN sii.item_group = 'FG-Fish Meal' THEN sii.qty ELSE 0 END) AS grand_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            AND IFNULL(si.custom_payment_status, 0) != 1
            AND si.custom_agent IS NOT NULL
            AND si.custom_agent != ''
            {conditions}
        GROUP BY
            si.custom_agent
        ORDER BY
            si.custom_agent ASC
    """

    return frappe.db.sql(query, filters, as_dict=True)


def format_row(row):
    numeric_fields = ["fm_60", "fm_62", "fm_65", "fo", "fsp", "grand_total"]

    for field in numeric_fields:
        value = flt(row.get(field))

        if value == 0:
            row[field] = ""
        else:
            row[field] = value


def calculate_totals(data):
    totals = {
        "agent": "<b>" + _("Grand Total") + "</b>",
        "fm_60": 0,
        "fm_62": 0,
        "fm_65": 0,
        "fo": 0,
        "fsp": 0,
        "grand_total": 0
    }

    for row in data:
        totals["fm_60"] += flt(row.get("fm_60", 0))
        totals["fm_62"] += flt(row.get("fm_62", 0))
        totals["fm_65"] += flt(row.get("fm_65", 0))
        totals["fo"] += flt(row.get("fo", 0))
        totals["fsp"] += flt(row.get("fsp", 0))
        totals["grand_total"] += flt(row.get("grand_total", 0))

    # Make totals bold
    totals["fm_60"] = f"<b>{totals['fm_60']}</b>" if totals["fm_60"] else ""
    totals["fm_62"] = f"<b>{totals['fm_62']}</b>" if totals["fm_62"] else ""
    totals["fm_65"] = f"<b>{totals['fm_65']}</b>" if totals["fm_65"] else ""
    totals["fo"] = f"<b>{totals['fo']}</b>" if totals["fo"] else ""
    totals["fsp"] = f"<b>{totals['fsp']}</b>" if totals["fsp"] else ""
    totals["grand_total"] = f"<b>{totals['grand_total']}</b>" if totals["grand_total"] else ""

    return totals