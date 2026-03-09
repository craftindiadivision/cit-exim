# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    # Convert zeros to blank
    numeric_fields = ["fm_60", "fm_62", "fm_65", "fo", "fsp", "grand_total"]

    for row in data:
        for field in numeric_fields:
            if flt(row.get(field)) == 0:
                row[field] = ""

    # Add Grand Total row
    if data:
        total_row = calculate_totals(data)
        data.append(total_row)

    return columns, data


def get_columns():
    return [
        {"label": _("Consignee"), "fieldname": "consignee", "fieldtype": "Data", "width": 200},
        {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 100},
        {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 100},
        {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 100},
        {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 100},
        {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 100},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):

    posting_date = filters.get("posting_date") or frappe.utils.today()

    query = """
        SELECT
            si.custom_consignee AS consignee,
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
            AND si.custom_consignee IS NOT NULL
            AND si.posting_date <= %s
        GROUP BY si.custom_consignee
    """

    return frappe.db.sql(query, (posting_date,), as_dict=True)


def calculate_totals(data):

    totals = {
        "consignee": "<b>" + _("Grand Total") + "</b>",
        "fm_60": 0,
        "fm_62": 0,
        "fm_65": 0,
        "fo": 0,
        "fsp": 0,
        "grand_total": 0
    }

    for row in data:
        totals["fm_60"] += flt(row.get("fm_60"))
        totals["fm_62"] += flt(row.get("fm_62"))
        totals["fm_65"] += flt(row.get("fm_65"))
        totals["fo"] += flt(row.get("fo"))
        totals["fsp"] += flt(row.get("fsp"))
        totals["grand_total"] += flt(row.get("grand_total"))

    # Bold totals
    for key in ["fm_60","fm_62","fm_65","fo","fsp","grand_total"]:
        totals[key] = f"<b>{totals[key]}</b>" if totals[key] else ""

    return totals