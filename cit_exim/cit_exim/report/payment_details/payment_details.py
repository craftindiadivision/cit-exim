

# Copyright (c) 2024, Your Name/Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import today, date_diff, flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    # Optional: Adding a total row for Amount and Received Amt
    if data:
        total_row = calculate_totals(data)
        data.append(total_row)
        
    return columns, data

def get_columns():
    return [
        {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 100},
        {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Data", "width": 100},
        {"label": _("Buyer"), "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Data", "width": 110},
        {"label": _("PO No"), "fieldname": "po_no", "fieldtype": "Data", "width": 110},
        {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
        {"label": _("New Inv"), "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 90},
        {"label": _("Comm. Rate"), "fieldname": "commission_rate", "fieldtype": "Percent", "width": 90},
        {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
        {"label": _("Product"), "fieldname": "product", "fieldtype": "Data", "width": 120},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 110},
        {"label": _("Received Amt"), "fieldname": "received_amt", "fieldtype": "Currency", "width": 110},
        {"label": _("Bank Charges"), "fieldname": "bank_charges", "fieldtype": "Currency", "width": 110},
        {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 100},
        {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 100},
        {"label": _("Submission Dt"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
        {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
        {"label": _("Aging Days"), "fieldname": "aging_days", "fieldtype": "Int", "width": 90},
        {"label": _("Bank Name"), "fieldname": "bank_name", "fieldtype": "Data", "width": 130},
        {"label": _("Payment Date"), "fieldname": "payment_receipt_date", "fieldtype": "Date", "width": 110},
        {"label": _("Bank Ref No"), "fieldname": "bank_ref_no", "fieldtype": "Data", "width": 120},
        {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Small Text", "width": 150}
    ]

def get_data(filters):
    conditions = "si.docstatus IN (0, 1) AND si.custom_payment_status = 0"
    
    if filters.get("company"):
        conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f" AND si.posting_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"
    if filters.get("workflow_status"):
        conditions += f" AND si.custom_work_flow_status = {frappe.db.escape(filters.get('workflow_status'))}"

    query = f"""
        SELECT 
            si.custom_loading_point AS pol,
            si.custom_agent AS agent,
            si.customer AS buyer,
            items.sales_order AS lc_po,
            so.po_no AS po_no,
            so.custom_pending_qty AS pending_qty,
            si.name AS new_inv,
            items.qty AS qty,
            items.rate AS rate,
            si.commission_rate AS commission_rate,
            si.name AS invoice_name,
            si.custom_item_group AS product,
            items.amount AS amount,
            pe.paid_amount AS received_amt,
            (SELECT SUM(atc.tax_amount) FROM `tabAdvance Taxes and Charges` atc WHERE atc.parent = pe.name) AS bank_charges,
            si.final_destination AS pod,
            si.country_of_destination AS country,
            si.custom_submission_date AS submission_dt,
            si.custom_shipped_on_board_date AS etd,
            bank.bank AS bank_name,
            pe.reference_date AS payment_receipt_date,
            pe.reference_no AS bank_ref_no,
            si.custom_dhl AS dhl,
            si.custom_bl_issued_remarks AS remarks
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` items ON items.parent = si.name
        LEFT JOIN `tabSales Order` so ON items.sales_order = so.name
        LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = si.name
        LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent
        LEFT JOIN `tabBank Account` bank ON pe.bank_account = bank.name
        WHERE {conditions}
        ORDER BY si.posting_date DESC
    """
    
    raw_data = frappe.db.sql(query, as_dict=True)
    
    current_date = today()
    for row in raw_data:
        # 1. Calculate Aging Days
        if row.submission_dt:
            row.aging_days = date_diff(current_date, row.submission_dt)
        else:
            row.aging_days = 0
            
        # 2. Extract CP (Regex applied in Python for better compatibility)
        import re
        row.cp = ""
        # Searching inside remarks or name as a fallback; adjust source field if needed
        match = re.search(r'[0-9]+(\.[0-9]+)?%', str(row.remarks or ""))
        if match:
            row.cp = match.group()

    return raw_data

def calculate_totals(data):
    total_amount = sum(flt(row.get("amount")) for row in data)
    total_received = sum(flt(row.get("received_amt")) for row in data)
    
    return {
        "pol": "<b>" + _("Total") + "</b>",
        "amount": total_amount,
        "received_amt": total_received
    }