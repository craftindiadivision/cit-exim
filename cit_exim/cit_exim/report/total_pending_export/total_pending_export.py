# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Data", "width": 120},
        {"label": _("Buyer Name"), "fieldname": "buyer_name", "fieldtype": "Data", "width": 150},
        {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
        {"label": _("New Inv"), "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Com"), "fieldname": "com", "fieldtype": "Percent", "width": 80},
        {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
        {"label": _("Product"), "fieldname": "product", "fieldtype": "Data", "width": 120},
        {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 120},
        {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 100},
        {"label": _("Submission Dt."), "fieldname": "submission_dt", "fieldtype": "Data", "width": 120},
        {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
    ]

def get_data(filters):
    # This query matches your logic: Submitted (docstatus=1) AND (Unpaid OR Custom Payment Status != 1)
    # Grouping by si_item.name ensures you get unique item rows
    
    query = """
        SELECT
            si.custom_agent AS agent,
            si.customer AS buyer_name,
            si_item.sales_order AS lc_po,
            si.name AS new_inv,
            si_item.qty AS qty,
            si_item.rate AS rate,
            si_item.amount AS amount, 
            si.commission_rate AS com,
            MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\\\.[0-9]+)?%')) AS cp,
            si.custom_item_group AS product,
            si.final_destination AS pod, 
            si.country_of_destination AS country,
            si.custom_work_flow_status AS submission_dt,
            si.custom_shipped_on_board_date AS etd
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Item` si_item ON si.name = si_item.parent
        LEFT JOIN
            `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = si.name 
            AND cqs.parenttype = 'Sales Invoice' 
            AND cqs.test = 'PROTEIN'
        WHERE
            si.docstatus = 1 
            AND (si.status = 'Unpaid' OR si.custom_payment_status != 1)
        GROUP BY
            si_item.name
        ORDER BY 
            si.posting_date DESC
    """
    
    return frappe.db.sql(query, as_dict=True)