# # Copyright (c) 2026, craft and contributors
# # For license information, please see license.txt

# # import frappe


# # def execute(filters=None):
# # 	columns, data = [], []
# # 	return columns, data





# import frappe

# def execute(filters=None):
#     if not filters:
#         filters = {}
        
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": "POL", "fieldname": "pol", "fieldtype": "Data", "width": 120},
#         {"label": "AGENT", "fieldname": "agent", "fieldtype": "Link", "options": "Customer", "width": 120},
#         {"label": "BUYER", "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 150},
#         {"label": "LC/PO", "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
#         {"label": "PO", "fieldname": "po_no", "fieldtype": "Data", "width": 100},
#         {"label": "NEW INV", "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
#         {"label": "QTY", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "RATE", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
#         {"label": "COMM", "fieldname": "commission_rate", "fieldtype": "Percent", "width": 80},
#         {"label": "CP", "fieldname": "cp", "fieldtype": "Data", "width": 80},
#         {"label": "PRODUCT", "fieldname": "product", "fieldtype": "Data", "width": 120},
#         {"label": "AMOUNT", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
#         {"label": "POD", "fieldname": "pod", "fieldtype": "Data", "width": 120},
#         {"label": "COUNTRY", "fieldname": "country", "fieldtype": "Data", "width": 120},
#         {"label": "SUBMISSION DT.", "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
#         {"label": "ETD", "fieldname": "etd", "fieldtype": "Date", "width": 110},
#         {"label": "BANK", "fieldname": "bank_name", "fieldtype": "Data", "width": 150},
#         {"label": "DHL", "fieldname": "dhl", "fieldtype": "Data", "width": 110},
#         {"label": "REACHING DT / PAYMENT RECEIPT DATE", "fieldname": "payment_receipt_date", "fieldtype": "Date", "width": 150},
#         {"label": "BANK REFERENCE NO.", "fieldname": "bank_ref_no", "fieldtype": "Data", "width": 160},
#     ]

# def get_data(filters):
#     # Initialize conditions with the docstatus and the default workflow status
#     conditions = "si.docstatus IN (0, 1)"
    
#     # Apply filter if selected, otherwise default to 'BL Issued'
#     status = filters.get("custom_work_flow_status") or "BL Issued"
#     conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(status)}"

#     return frappe.db.sql(f"""
#         SELECT
#             si.port_of_loading AS pol,
#             si.custom_agent AS agent,
#             si.customer AS buyer,
#             items.sales_order AS lc_po,
#             so.po_no AS po_no,
#             si.name AS new_inv,
#             items.qty AS qty,
#             items.rate AS rate,
#             si.commission_rate AS commission_rate,
#             MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\\\.[0-9]+)?%')) AS cp,
#             si.custom_item_group AS product,
#             items.amount AS amount,
#             si.port_of_discharge AS pod,
#             si.country_of_destination AS country,
#             si.custom_submission_date AS submission_dt,
#             si.custom_shipped_on_board_date AS etd,
#             bank.bank_name AS bank_name,
#             pe.custom_date AS payment_receipt_date,
#             pe.custom_inward_remittance_no AS bank_ref_no,
#             si.custom_dhl AS dhl
#         FROM
#             `tabSales Invoice` si
#         JOIN
#             `tabSales Invoice Item` items ON items.parent = si.name
#         LEFT JOIN
#             `tabSales Order` so ON items.sales_order = so.name
#         LEFT JOIN
#             `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = si.name 
#             AND cqs.parenttype = 'Sales Invoice' 
#             AND cqs.test = 'PROTEIN'
#         LEFT JOIN
#             `tabPayment Entry Reference` per ON per.reference_name = si.name
#         LEFT JOIN
#             `tabPayment Entry` pe ON pe.name = per.parent
#         LEFT JOIN
#             `tabBank Account` ba ON pe.bank_account = ba.name
#         LEFT JOIN
#             `tabBank` bank ON ba.bank = bank.name
#         WHERE
#             {conditions}
#         GROUP BY 
#             items.name
#         ORDER BY 
#             si.posting_date DESC
#     """, as_dict=1)



# import frappe
# from frappe.utils import today

# def execute(filters=None):
#     if not filters:
#         filters = {}
        
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": "POL", "fieldname": "pol", "fieldtype": "Data", "width": 120},
#         {"label": "AGENT", "fieldname": "agent", "fieldtype": "Link", "options": "Customer", "width": 120},
#         {"label": "BUYER", "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 150},
#         {"label": "LC/PO", "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
#         {"label": "PO", "fieldname": "po_no", "fieldtype": "Data", "width": 100},
#         {"label": "NEW INV", "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
#         {"label": "QTY", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "RATE", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
#         {"label": "COMM", "fieldname": "commission_rate", "fieldtype": "Percent", "width": 80},
#         {"label": "CP", "fieldname": "cp", "fieldtype": "Data", "width": 80},
#         {"label": "PRODUCT", "fieldname": "product", "fieldtype": "Data", "width": 120},
#         {"label": "AMOUNT", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
#         {"label": "POD", "fieldname": "pod", "fieldtype": "Data", "width": 120},
#         {"label": "COUNTRY", "fieldname": "country", "fieldtype": "Data", "width": 120},
#         {"label": "SUBMISSION DT.", "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
#         {"label": "ETD", "fieldname": "etd", "fieldtype": "Date", "width": 110},
#         {"label": "BANK", "fieldname": "bank_name", "fieldtype": "Data", "width": 150},
#         {"label": "DHL", "fieldname": "dhl", "fieldtype": "Data", "width": 110},
#         {"label": "REACHING DT / PAYMENT RECEIPT DATE", "fieldname": "payment_receipt_date", "fieldtype": "Date", "width": 150},
#         {"label": "BANK REFERENCE NO.", "fieldname": "bank_ref_no", "fieldtype": "Data", "width": 160},
#         # New Column Added
#         {"label": "AGING DAYS", "fieldname": "aging_days", "fieldtype": "Int", "width": 100},
#     ]

# def get_data(filters):
#     conditions = "si.docstatus IN (0, 1)"
#     status = filters.get("custom_work_flow_status") or "BL Issued"
#     conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(status)}"
    
#     # Get current date for the calculation when no payment exists
#     current_date = today()

#     return frappe.db.sql(f"""
#         SELECT
#             si.port_of_loading AS pol,
#             si.custom_agent AS agent,
#             si.customer AS buyer,
#             items.sales_order AS lc_po,
#             so.po_no AS po_no,
#             si.name AS new_inv,
#             items.qty AS qty,
#             items.rate AS rate,
#             si.commission_rate AS commission_rate,
#             MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\\\.[0-9]+)?%')) AS cp,
#             si.custom_item_group AS product,
#             items.amount AS amount,
#             si.port_of_discharge AS pod,
#             si.country_of_destination AS country,
#             si.custom_submission_date AS submission_dt,
#             si.custom_shipped_on_board_date AS etd,
#             bank.bank_name AS bank_name,
#             pe.custom_date AS payment_receipt_date,
#             pe.custom_inward_remittance_no AS bank_ref_no,
#             si.custom_dhl AS dhl,
#             /* Aging Calculation Logic */
#             DATEDIFF(
#                 COALESCE(pe.custom_date, '{current_date}'), 
#                 si.custom_submission_date
#             ) AS aging_days
#         FROM
#             `tabSales Invoice` si
#         JOIN
#             `tabSales Invoice Item` items ON items.parent = si.name
#         LEFT JOIN
#             `tabSales Order` so ON items.sales_order = so.name
#         LEFT JOIN
#             `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = si.name 
#             AND cqs.parenttype = 'Sales Invoice' 
#             AND cqs.test = 'PROTEIN'
#         LEFT JOIN
#             `tabPayment Entry Reference` per ON per.reference_name = si.name
#         LEFT JOIN
#             `tabPayment Entry` pe ON pe.name = per.parent
#         LEFT JOIN
#             `tabBank Account` ba ON pe.bank_account = ba.name
#         LEFT JOIN
#             `tabBank` bank ON ba.bank = bank.name
#         WHERE
#             {conditions}
#         GROUP BY 
#             items.name
#         ORDER BY 
#             si.posting_date DESC
#     """, as_dict=1)




import frappe
from frappe.utils import today

def execute(filters=None):
    if not filters:
        filters = {}
        
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "POL", "fieldname": "pol", "fieldtype": "Data", "width": 120},
        {"label": "AGENT", "fieldname": "agent", "fieldtype": "Link", "options": "Customer", "width": 120},
        {"label": "BUYER", "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "LC/PO", "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
        {"label": "PO", "fieldname": "po_no", "fieldtype": "Data", "width": 100},
        {"label": "NEW INV", "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
        {"label": "QTY", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "RATE", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": "COMM", "fieldname": "commission_rate", "fieldtype": "Percent", "width": 80},
        {"label": "CP", "fieldname": "cp", "fieldtype": "Data", "width": 80},
        {"label": "PRODUCT", "fieldname": "product", "fieldtype": "Data", "width": 120},
        {"label": "AMOUNT", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "POD", "fieldname": "pod", "fieldtype": "Data", "width": 120},
        {"label": "COUNTRY", "fieldname": "country", "fieldtype": "Data", "width": 120},
        {"label": "SUBMISSION DT.", "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
        {"label": "ETD", "fieldname": "etd", "fieldtype": "Date", "width": 110},
        {"label": "BANK", "fieldname": "bank_name", "fieldtype": "Data", "width": 150},
        {"label": "DHL", "fieldname": "dhl", "fieldtype": "Data", "width": 110},
        {"label": "REACHING DT / PAYMENT RECEIPT DATE", "fieldname": "payment_receipt_date", "fieldtype": "Date", "width": 150},
        {"label": "BANK REFERENCE NO.", "fieldname": "bank_ref_no", "fieldtype": "Data", "width": 160},
        {"label": "AGING DAYS", "fieldname": "aging_days", "fieldtype": "Int", "width": 100},
        # New Column Added
        {"label": "REMARKS", "fieldname": "remarks", "fieldtype": "Small Text", "width": 200},
    ]

def get_data(filters):
    conditions = "si.docstatus IN (0, 1)"
    status = filters.get("custom_work_flow_status") or "BL Issued"
    conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(status)}"
    
    current_date = today()

    return frappe.db.sql(f"""
        SELECT
            si.port_of_loading AS pol,
            si.custom_agent AS agent,
            si.customer AS buyer,
            items.sales_order AS lc_po,
            so.po_no AS po_no,
            si.name AS new_inv,
            items.qty AS qty,
            items.rate AS rate,
            si.commission_rate AS commission_rate,
            MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\\\.[0-9]+)?%')) AS cp,
            si.custom_item_group AS product,
            items.amount AS amount,
            si.port_of_discharge AS pod,
            si.country_of_destination AS country,
            si.custom_submission_date AS submission_dt,
            si.custom_shipped_on_board_date AS etd,
            bank.bank_name AS bank_name,
            pe.custom_date AS payment_receipt_date,
            pe.custom_inward_remittance_no AS bank_ref_no,
            si.custom_dhl AS dhl,
            /* Fetching the Remarks field */
            si.custom_bl_issued_remarks AS remarks,
            /* Aging Calculation */
            DATEDIFF(
                COALESCE(pe.custom_date, '{current_date}'), 
                si.custom_submission_date
            ) AS aging_days
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` items ON items.parent = si.name
        LEFT JOIN
            `tabSales Order` so ON items.sales_order = so.name
        LEFT JOIN
            `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = si.name 
            AND cqs.parenttype = 'Sales Invoice' 
            AND cqs.test = 'PROTEIN'
        LEFT JOIN
            `tabPayment Entry Reference` per ON per.reference_name = si.name
        LEFT JOIN
            `tabPayment Entry` pe ON pe.name = per.parent
        LEFT JOIN
            `tabBank Account` ba ON pe.bank_account = ba.name
        LEFT JOIN
            `tabBank` bank ON ba.bank = bank.name
        WHERE
            {conditions}
        GROUP BY 
            items.name
        ORDER BY 
            si.posting_date DESC
    """, as_dict=1)