# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe import _

def execute(filters=None):
    if not filters: filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    # Adding "options": "currency" tells Frappe to look at the 'currency' field in each row
    return [
        {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
        {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("FO"), "fieldname": "fo", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "options": "currency", "width": 150},
    ]

def get_data(filters):
    conditions = ""
    
    if filters.get("company"):
        conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    
    if filters.get("from_date"):
        conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
        
    if filters.get("to_date"):
        conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
    else:
        conditions += " AND si.posting_date <= CURDATE()"

    query = f"""
        /* 1. Country-wise Rows (USD) */
        SELECT
            si.country_of_destination AS country,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount ELSE 0 END) AS fm_60,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount ELSE 0 END) AS fm_62,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount ELSE 0 END) AS fm_65,
            SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount ELSE 0 END) AS fo,
            SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount ELSE 0 END) AS fsp,
            SUM(sii.net_amount) AS grand_total,
            si.currency AS currency,
            0 as row_order
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1 
            AND IFNULL(si.custom_payment_status, 0) != 1
            AND si.country_of_destination IS NOT NULL
            {conditions}
        GROUP BY si.country_of_destination

        UNION ALL

        /* 2. Grand Total Row (USD) */
        SELECT
            'Grand Total' AS country,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount ELSE 0 END),
            SUM(sii.net_amount),
            MAX(si.currency),
            1 as row_order
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1 
            AND IFNULL(si.custom_payment_status, 0) != 1
            {conditions}

        UNION ALL

        /* 3. Total INR Row (Forced INR) */
        SELECT
            'TOTAL (INR)' AS country,
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
            SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
            SUM(sii.net_amount * si.conversion_rate),
            'INR',
            2 as row_order
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1 
            AND IFNULL(si.custom_payment_status, 0) != 1
            {conditions}
        
        ORDER BY row_order ASC, country ASC
    """
    
    return frappe.db.sql(query, as_dict=True)