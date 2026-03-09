import frappe
from frappe import _
from frappe.utils import today, date_diff

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("POL"), "fieldname": "pol", "fieldtype": "Data", "width": 100},
        {"label": _("AGENT"), "fieldname": "agent", "fieldtype": "Data", "width": 100},
        {"label": _("BUYER"), "fieldname": "buyer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("LC/PO"), "fieldname": "lc_po", "fieldtype": "Data", "width": 110},
        {"label": _("PO No"), "fieldname": "po_no", "fieldtype": "Data", "width": 110},
        {"label": _("NEW INV"), "fieldname": "new_inv", "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
        {"label": _("QTY"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("RATE"), "fieldname": "rate", "fieldtype": "Currency", "width": 90},
        {"label": _("COMM. RATE"), "fieldname": "commission_rate", "fieldtype": "Percent", "width": 90},
        {"label": _("CP"), "fieldname": "cp", "fieldtype": "Data", "width": 80},
        {"label": _("PRODUCT"), "fieldname": "product", "fieldtype": "Data", "width": 120},
        {"label": _("AMOUNT"), "fieldname": "amount", "fieldtype": "Currency", "width": 110},
        {"label": _("POD"), "fieldname": "pod", "fieldtype": "Data", "width": 100},
        {"label": _("COUNTRY"), "fieldname": "country", "fieldtype": "Data", "width": 100},
        {"label": _("SUBMISSION DT"), "fieldname": "submission_dt", "fieldtype": "Date", "width": 110},
        {"label": _("ETD"), "fieldname": "etd", "fieldtype": "Date", "width": 110},
        {"label": _("BANK"), "fieldname": "bank_name", "fieldtype": "Data", "width": 130},
        {"label": _("DHL"), "fieldname": "dhl", "fieldtype": "Data", "width": 100},
        {"label": _("REACHING DT / PAYMENT RECEIPT DATE"), "fieldname": "payment_receipt_date", "fieldtype": "Date", "width": 110},
        {"label": _("RECEIVED AMOUNT"), "fieldname": "received_amt", "fieldtype": "Currency", "width": 110},
        {"label": _("BANK CHARGES/BALANCE"), "fieldname": "bank_charges", "fieldtype": "Currency", "width": 110},
        {"label": _("BANK REFERENCE NO"), "fieldname": "bank_ref_no", "fieldtype": "Data", "width": 120},
        {"label": _("AGING  DAYS"), "fieldname": "aging_days", "fieldtype": "Int", "width": 90},
        {"label": _("PENDING QTY"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
        {"label": _("REMARKS"), "fieldname": "remarks", "fieldtype": "Small Text", "width": 150}
    ]

def get_data(filters):
    # Mandatory condition: docstatus 0 or 1 and pending payment
    conditions = "si.docstatus IN (0,1) AND si.custom_payment_status IN (0,1)"
    
    # Apply dynamic filters
    if filters.get("company"):
        conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    
    if filters.get("from_date"):
        conditions += f" AND si.posting_date >= '{filters.get('from_date')}'"
    
    if filters.get("to_date"):
        conditions += f" AND si.posting_date <= '{filters.get('to_date')}'"
    
    # This must match the fieldname in the .js file
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
            si.custom_item_group AS product,
            items.amount AS amount,
            pe.paid_amount AS received_amt,
            (SELECT SUM(atc.tax_amount) FROM `tabAdvance Taxes and Charges` atc WHERE atc.parent = pe.name) AS bank_charges,
            si.final_destination AS pod,
            si.country_of_destination AS country,
            si.custom_submission_date AS submission_dt,
            si.custom_shipped_on_board_date AS etd,
            bank_master.bank_name AS bank_name,
            pe.reference_date AS payment_receipt_date,
            pe.reference_no AS bank_ref_no,
            si.custom_dhl AS dhl,
            si.custom_bl_issued_remarks AS remarks,
            MAX(REGEXP_SUBSTR(cqs.value, '[0-9]+(\\\\.[0-9]+)?%')) AS cp
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` items ON items.parent = si.name
        LEFT JOIN `tabSales Order` so ON items.sales_order = so.name
        LEFT JOIN `tabFISH MEAL CHILDTABLE` cqs ON cqs.parent = si.name 
            AND cqs.parenttype = 'Sales Invoice' 
            AND cqs.test = 'PROTEIN'
        LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = si.name
        LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent
        LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
        LEFT JOIN `tabBank` bank_master ON ba.bank = bank_master.name
        WHERE {conditions}
        GROUP BY items.name
        ORDER BY si.posting_date DESC
    """
    
    raw_data = frappe.db.sql(query, as_dict=True)
    current_date = today()
    
    for row in raw_data:
        if row.submission_dt:
            row.aging_days = date_diff(current_date, row.submission_dt)
        else:
            row.aging_days = 0

    return raw_data