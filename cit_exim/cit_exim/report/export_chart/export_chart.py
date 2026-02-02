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
#         {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 120},
#         {"label": _("BUYER"), "fieldname": "buyer", "fieldtype": "Data", "width": 150},
#         {"label": _("CONSIGNEE"), "fieldname": "consignee", "fieldtype": "Data", "width": 150},
#         {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
#         {"label": _("PO"), "fieldname": "po", "fieldtype": "Data", "width": 120},
#         {"label": _("INV"), "fieldname": "inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
#         {"label": _("QTY"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": _("RATE"), "fieldname": "rate", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("COMM"), "fieldname": "comm", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
#         {"label": _("PRODUCT"), "fieldname": "product", "fieldtype": "Data", "width": 120},
#         {"label": _("AMOUNT"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 120},
#         {"label": _("COUNTRY"), "fieldname": "country", "fieldtype": "Data", "width": 120},
#         {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
#         {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
#         {"label": _("SUBMISSION DT"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("BANK"), "fieldname": "bank", "fieldtype": "Data", "width": 150},
#         {"label": _("Pmt Rcvd Dt"), "fieldname": "pmt_rcvd_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("Rcvd Amt"), "fieldname": "rcvd_amt", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("Bank Reference No"), "fieldname": "bank_ref", "fieldtype": "Data", "width": 150},
#         {"label": _("Bank Charges"), "fieldname": "bank_charges", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Currency", "hidden": 1}
#     ]

# def get_data(filters):
#     conditions = ""
#     if filters.get("company"):
#         conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
#     if filters.get("from_date"):
#         conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
#     if filters.get("to_date"):
#         conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
#     if filters.get("agent"):
#         conditions += f" AND si.custom_agent = {frappe.db.escape(filters.get('agent'))}"

#     query = f"""
#         SELECT
#             si.port_of_loading AS pol,
#             si.customer_name AS buyer,
#             si.custom_consignee AS consignee,
#             so.name AS lc_po,
#             so.po_no AS po,
#             si.name AS inv,
#             SUM(sii.qty) AS qty,
#             AVG(sii.rate) AS rate,
#             si.total_commission AS comm,
#             MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\.[0-9]+)?%')) AS cp,
#             so.custom_item_group AS product,
#             si.grand_total AS amount,
#             si.currency AS currency,
#             si.port_of_discharge AS pod,
#             si.country_of_destination AS country,
#             si.custom_shipped_on_board_date AS etd,
#             si.custom_dhl AS dhl,
#             si.custom_submission_date AS submission_dt,
            
#             -- Improved Bank Subquery
#             (SELECT GROUP_CONCAT(DISTINCT COALESCE(ba.bank, pe.bank_account) SEPARATOR ', ')
#              FROM `tabPayment Entry Reference` per
#              INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
#              LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
#              WHERE per.reference_name = si.name 
#              AND pe.docstatus = 1 
#              AND pe.payment_type = 'Receive') AS bank,

#             (SELECT MAX(pe.reference_date)
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS pmt_rcvd_dt,
            
#             (SELECT SUM(pe.paid_amount) 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS rcvd_amt,
            
#             (SELECT GROUP_CONCAT(pe.reference_no SEPARATOR ', ') 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_ref,
            
#             (si.grand_total - IFNULL((
#                 SELECT SUM(pe.paid_amount)
#                 FROM `tabPayment Entry Reference` per
#                 JOIN `tabPayment Entry` pe ON per.parent = pe.name
#                 WHERE per.reference_name = si.name AND pe.docstatus = 1
#             ), 0)) AS bank_charges
#         FROM
#             `tabSales Invoice` si
#         LEFT JOIN
#             `tabSales Invoice Item` sii ON si.name = sii.parent
#         LEFT JOIN
#             `tabSales Order` so ON sii.sales_order = so.name
#         LEFT JOIN
#             `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = so.name 
#             AND cqs.parenttype = 'Sales Order' 
#             AND cqs.test = 'PROTEIN'
#         WHERE
#             si.docstatus = 1
#             AND (si.status = 'Paid' OR si.custom_payment_status = 1 OR si.custom_work_flow_status = 'Completed shipment')
#             {conditions}
#         GROUP BY
#             si.name
#         ORDER BY
#             si.posting_date DESC
#     """
#     return frappe.db.sql(query, as_dict=True)




# import frappe
# from frappe import _
# from frappe.utils import today

# def execute(filters=None):
#     if not filters: filters = {}
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 120},
#         {"label": _("BUYER"), "fieldname": "buyer", "fieldtype": "Data", "width": 150},
#         {"label": _("CONSIGNEE"), "fieldname": "consignee", "fieldtype": "Data", "width": 150},
#         {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
#         {"label": _("PO"), "fieldname": "po", "fieldtype": "Data", "width": 120},
#         {"label": _("INV"), "fieldname": "inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
#         {"label": _("QTY"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": _("PENDING QTY"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 110}, # Added Pending Qty
#         {"label": _("RATE"), "fieldname": "rate", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("COMM"), "fieldname": "comm", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
#         {"label": _("PRODUCT"), "fieldname": "product", "fieldtype": "Data", "width": 120},
#         {"label": _("AMOUNT"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("AGING DAYS"), "fieldname": "aging_days", "fieldtype": "Int", "width": 100}, # Added Aging
#         {"label": _("REMARKS"), "fieldname": "remarks", "fieldtype": "Small Text", "width": 150}, # Added Remarks
#         {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 120},
#         {"label": _("COUNTRY"), "fieldname": "country", "fieldtype": "Data", "width": 120},
#         {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
#         {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
#         {"label": _("SUBMISSION DT"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("BANK"), "fieldname": "bank", "fieldtype": "Data", "width": 150},
#         {"label": _("Pmt Rcvd Dt"), "fieldname": "pmt_rcvd_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("RECEIVED AMT"), "fieldname": "rcvd_amt", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("BANK CHARGES/BALANCE"), "fieldname": "bank_charges", "fieldtype": "Currency", "options": "currency", "width": 140},
#         {"label": _("Bank Reference No"), "fieldname": "bank_ref", "fieldtype": "Data", "width": 150},
#         # {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Currency", "hidden": 1}
#     ]

# def get_data(filters):
#     conditions = ""
#     if filters.get("company"):
#         conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
#     if filters.get("from_date"):
#         conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
#     if filters.get("to_date"):
#         conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
#     if filters.get("agent"):
#         conditions += f" AND si.custom_agent = {frappe.db.escape(filters.get('agent'))}"
    
#     # Handle Workflow status filter from previous requirements
#     if filters.get("custom_work_flow_status"):
#         conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(filters.get('custom_work_flow_status'))}"

#     current_date = today()

#     query = f"""
#         SELECT
#             si.port_of_loading AS pol,
#             si.customer_name AS buyer,
#             si.custom_consignee AS consignee,
#             so.name AS lc_po,
#             so.po_no AS po,
#             so.custom_pending_qty AS pending_qty,
#             si.name AS inv,
#             SUM(sii.qty) AS qty,
#             AVG(sii.rate) AS rate,
#             si.total_commission AS comm,
#             MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\.[0-9]+)?%')) AS cp,
#             so.custom_item_group AS product,
#             si.grand_total AS amount,
#             si.currency AS currency,
#             si.port_of_discharge AS pod,
#             si.country_of_destination AS country,
#             si.custom_shipped_on_board_date AS etd,
#             si.custom_dhl AS dhl,
#             si.custom_submission_date AS submission_dt,
#             si.custom_bl_issued_remarks AS remarks,
            
#             -- Aging Days Calculation
#             DATEDIFF(
#                 COALESCE((SELECT MAX(pe.reference_date) FROM `tabPayment Entry Reference` per JOIN `tabPayment Entry` pe ON per.parent = pe.name WHERE per.reference_name = si.name AND pe.docstatus = 1), '{current_date}'),
#                 si.custom_submission_date
#             ) AS aging_days,

#             -- Bank Name (from Bank Account / Paid To)
#             (SELECT GROUP_CONCAT(DISTINCT COALESCE(ba.bank, pe.bank_account) SEPARATOR ', ')
#              FROM `tabPayment Entry Reference` per
#              INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
#              LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
#              WHERE per.reference_name = si.name 
#              AND pe.docstatus = 1) AS bank,

#             -- Payment Date
#             (SELECT MAX(pe.reference_date)
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS pmt_rcvd_dt,
            
#             -- Received Amount (Sum of paid_amount linked to this invoice)
#             (SELECT SUM(pe.paid_amount) 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS rcvd_amt,
            
#             -- Bank Charges (Sum of tax_amount from Advance Taxes and Charges table)
#             (SELECT SUM(atc.tax_amount)
#              FROM `tabPayment Entry Reference` per
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name
#              JOIN `tabAdvance Taxes and Charges` atc ON atc.parent = pe.name
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_charges,

#             (SELECT GROUP_CONCAT(pe.reference_no SEPARATOR ', ') 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_ref
            
#         FROM
#             `tabSales Invoice` si
#         LEFT JOIN
#             `tabSales Invoice Item` sii ON si.name = sii.parent
#         LEFT JOIN
#             `tabSales Order` so ON sii.sales_order = so.name
#         LEFT JOIN
#             `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = so.name 
#             AND cqs.parenttype = 'Sales Order' 
#             AND cqs.test = 'PROTEIN'
#         WHERE
#             si.docstatus IN (0, 1)
#             {conditions}
#         GROUP BY
#             si.name
#         ORDER BY
#             si.posting_date DESC
#     """
#     return frappe.db.sql(query, as_dict=True)



# import frappe
# from frappe import _
# from frappe.utils import today

# def execute(filters=None):
#     if not filters: filters = {}
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 120},
#         {"label": _("BUYER"), "fieldname": "buyer", "fieldtype": "Data", "width": 150},
#         {"label": _("CONSIGNEE"), "fieldname": "consignee", "fieldtype": "Data", "width": 150},
#         {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
#         {"label": _("PO"), "fieldname": "po", "fieldtype": "Data", "width": 120},
#         {"label": _("INV"), "fieldname": "inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
#         {"label": _("QTY"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": _("PENDING QTY"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 110},
#         {"label": _("RATE"), "fieldname": "rate", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("COMM"), "fieldname": "comm", "fieldtype": "Currency", "options": "currency", "width": 100},
#         {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
#         {"label": _("PRODUCT"), "fieldname": "product", "fieldtype": "Data", "width": 120},
#         {"label": _("AMOUNT"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("AGING DAYS"), "fieldname": "aging_days", "fieldtype": "Int", "width": 100},
#         {"label": _("REMARKS"), "fieldname": "remarks", "fieldtype": "Small Text", "width": 150},
#         {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 120},
#         {"label": _("COUNTRY"), "fieldname": "country", "fieldtype": "Data", "width": 120},
#         {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
#         {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
#         {"label": _("SUBMISSION DT"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("BANK"), "fieldname": "bank", "fieldtype": "Data", "width": 150},
#         {"label": _("Pmt Rcvd Dt"), "fieldname": "pmt_rcvd_dt", "fieldtype": "Date", "width": 110},
#         {"label": _("RECEIVED AMT"), "fieldname": "rcvd_amt", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("BANK CHARGES/BALANCE"), "fieldname": "bank_charges", "fieldtype": "Currency", "options": "currency", "width": 140},
#         {"label": _("Bank Reference No"), "fieldname": "bank_ref", "fieldtype": "Data", "width": 150},
#     ]

# def get_data(filters):
#     conditions = ""
#     if filters.get("company"):
#         conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
#     if filters.get("from_date"):
#         conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
#     if filters.get("to_date"):
#         conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
#     if filters.get("agent"):
#         conditions += f" AND si.custom_agent = {frappe.db.escape(filters.get('agent'))}"
    
#     if filters.get("custom_work_flow_status"):
#         conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(filters.get('custom_work_flow_status'))}"

#     current_date = today()

#     query = f"""
#         SELECT
#             si.port_of_loading AS pol,
#             si.customer_name AS buyer,
#             si.custom_consignee AS consignee,
#             so.name AS lc_po,
#             so.po_no AS po,
#             so.custom_pending_qty AS pending_qty,
#             si.name AS inv,
#             SUM(sii.qty) AS qty,
#             AVG(sii.rate) AS rate,
#             si.total_commission AS comm,
#             MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\.[0-9]+)?%')) AS cp,
#             so.custom_item_group AS product,
#             si.grand_total AS amount,
#             si.currency AS currency,
#             si.port_of_discharge AS pod,
#             si.country_of_destination AS country,
#             si.custom_shipped_on_board_date AS etd,
#             si.custom_dhl AS dhl,
#             si.custom_submission_date AS submission_dt,
#             si.custom_bl_issued_remarks AS remarks,
            
#             -- Updated Aging Days to use pe.custom_date
#             DATEDIFF(
#                 COALESCE((SELECT MAX(pe.custom_date) FROM `tabPayment Entry Reference` per JOIN `tabPayment Entry` pe ON per.parent = pe.name WHERE per.reference_name = si.name AND pe.docstatus = 1), '{current_date}'),
#                 si.custom_submission_date
#             ) AS aging_days,

#             (SELECT GROUP_CONCAT(DISTINCT COALESCE(ba.bank, pe.bank_account) SEPARATOR ', ')
#              FROM `tabPayment Entry Reference` per
#              INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
#              LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
#              WHERE per.reference_name = si.name 
#              AND pe.docstatus = 1) AS bank,

#             (SELECT MAX(pe.custom_date)
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS pmt_rcvd_dt,
            
#             (SELECT SUM(pe.paid_amount) 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS rcvd_amt,
            
#             (SELECT SUM(atc.tax_amount)
#              FROM `tabPayment Entry Reference` per
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name
#              JOIN `tabAdvance Taxes and Charges` atc ON atc.parent = pe.name
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_charges,

#             (SELECT GROUP_CONCAT(pe.reference_no SEPARATOR ', ') 
#              FROM `tabPayment Entry Reference` per 
#              JOIN `tabPayment Entry` pe ON per.parent = pe.name 
#              WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_ref
            
#         FROM
#             `tabSales Invoice` si
#         LEFT JOIN
#             `tabSales Invoice Item` sii ON si.name = sii.parent
#         LEFT JOIN
#             `tabSales Order` so ON sii.sales_order = so.name
#         LEFT JOIN
#             `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = so.name 
#             AND cqs.parenttype = 'Sales Order' 
#             AND cqs.test = 'PROTEIN'
#         WHERE
#             si.docstatus IN (0, 1)
#             {conditions}
#         GROUP BY
#             si.name
#         ORDER BY
#             si.posting_date DESC
#     """
#     return frappe.db.sql(query, as_dict=True)



import frappe
from frappe import _
from frappe.utils import today

def execute(filters=None):
    if not filters: filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 120},
        {"label": _("BUYER"), "fieldname": "buyer", "fieldtype": "Data", "width": 150},
        {"label": _("CONSIGNEE"), "fieldname": "consignee", "fieldtype": "Data", "width": 150},
        {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Link", "options": "Sales Order", "width": 120},
        {"label": _("PO"), "fieldname": "po", "fieldtype": "Data", "width": 120},
        {"label": _("INV"), "fieldname": "inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
        {"label": _("QTY"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        # {"label": _("PENDING QTY"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 110},
        {"label": _("RATE"), "fieldname": "rate", "fieldtype": "Currency", "options": "currency", "width": 100},
        {"label": _("COMM"), "fieldname": "comm", "fieldtype": "Currency", "options": "currency", "width": 100},
        {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
        {"label": _("PRODUCT"), "fieldname": "product", "fieldtype": "Data", "width": 120},
        {"label": _("AMOUNT"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 120},
        # {"label": _("AGING DAYS"), "fieldname": "aging_days", "fieldtype": "Int", "width": 100},
        # {"label": _("REMARKS"), "fieldname": "remarks", "fieldtype": "Small Text", "width": 150},
        {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 120},
        {"label": _("COUNTRY"), "fieldname": "country", "fieldtype": "Data", "width": 120},
        {"label": _("SUBMISSION DT"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
        {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
        {"label": _("BANK"), "fieldname": "bank", "fieldtype": "Data", "width": 150},
        {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
        {"label": _("Pmt Rcvd Dt"), "fieldname": "pmt_rcvd_dt", "fieldtype": "Date", "width": 110},
        {"label": _("Received Amt"), "fieldname": "rcvd_amt", "fieldtype": "Currency", "options": "currency", "width": 120},
        {"label": _("Bank Charges/Balance"), "fieldname": "bank_charges", "fieldtype": "Currency", "options": "currency", "width": 140},
        {"label": _("Bank Reference No"), "fieldname": "bank_ref", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    conditions = ""
    if filters.get("company"):
        conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    if filters.get("from_date"):
        conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
    if filters.get("to_date"):
        conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
    if filters.get("agent"):
        conditions += f" AND si.custom_agent = {frappe.db.escape(filters.get('agent'))}"
    
    if filters.get("custom_work_flow_status"):
        conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(filters.get('custom_work_flow_status'))}"

    current_date = today()

    query = f"""
        SELECT
            si.port_of_loading AS pol,
            si.customer_name AS buyer,
            si.custom_consignee AS consignee,
            so.name AS lc_po,
            so.po_no AS po,
            # so.custom_pending_qty AS pending_qty,
            si.name AS inv,
            SUM(sii.qty) AS qty,
            AVG(sii.rate) AS rate,
            si.total_commission AS comm,
            MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\.[0-9]+)?%')) AS cp,
            so.custom_item_group AS product,
            si.grand_total AS amount,
            si.currency AS currency,
            si.port_of_discharge AS pod,
            si.country_of_destination AS country,
            si.custom_shipped_on_board_date AS etd,
            si.custom_dhl AS dhl,
            si.custom_submission_date AS submission_dt,
            # si.custom_bl_issued_remarks AS remarks,
            
            # -- Aging Days
            # DATEDIFF(
            #     COALESCE((SELECT MAX(pe.custom_date) FROM `tabPayment Entry Reference` per JOIN `tabPayment Entry` pe ON per.parent = pe.name WHERE per.reference_name = si.name AND pe.docstatus = 1), '{current_date}'),
            #     si.custom_submission_date
            # ) AS aging_days,

            -- Bank Name
            (SELECT GROUP_CONCAT(DISTINCT COALESCE(ba.bank, pe.bank_account) SEPARATOR ', ')
             FROM `tabPayment Entry Reference` per
             INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
             LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
             WHERE per.reference_name = si.name 
             AND pe.docstatus = 1) AS bank,

            -- Payment Date (custom_date)
            (SELECT MAX(pe.reference_date)
             FROM `tabPayment Entry Reference` per 
             JOIN `tabPayment Entry` pe ON per.parent = pe.name 
             WHERE per.reference_name = si.name AND pe.docstatus = 1) AS pmt_rcvd_dt,
            
            -- Received Amount
            (SELECT SUM(pe.paid_amount) 
             FROM `tabPayment Entry Reference` per 
             JOIN `tabPayment Entry` pe ON per.parent = pe.name 
             WHERE per.reference_name = si.name AND pe.docstatus = 1) AS rcvd_amt,
            
            -- Bank Charges
            (SELECT SUM(atc.tax_amount)
             FROM `tabPayment Entry Reference` per
             JOIN `tabPayment Entry` pe ON per.parent = pe.name
             JOIN `tabAdvance Taxes and Charges` atc ON atc.parent = pe.name
             WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_charges,

            -- Updated Bank Reference (custom_inward_remittance_no)
            (SELECT GROUP_CONCAT(DISTINCT pe.reference_no SEPARATOR ', ') 
             FROM `tabPayment Entry Reference` per 
             JOIN `tabPayment Entry` pe ON per.parent = pe.name 
             WHERE per.reference_name = si.name AND pe.docstatus = 1) AS bank_ref
            
        FROM
            `tabSales Invoice` si
        LEFT JOIN
            `tabSales Invoice Item` sii ON si.name = sii.parent
        LEFT JOIN
            `tabSales Order` so ON sii.sales_order = so.name
        LEFT JOIN
            `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = so.name 
            AND cqs.parenttype = 'Sales Order' 
            AND cqs.test = 'PROTEIN'
        WHERE
            si.docstatus IN (0, 1)
            {conditions}
        GROUP BY
            si.name
        ORDER BY
            si.posting_date DESC
    """
    return frappe.db.sql(query, as_dict=True)