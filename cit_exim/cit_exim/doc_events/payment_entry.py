
# # update the status of sales invoice according to completion of payment entry

# import frappe
# from frappe.utils import nowdate

# def on_submit_update_sales_invoice(doc, method):
#     # Only for Customer payments
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
#             continue

#         si = frappe.get_doc("Sales Invoice", ref.reference_name)

#         # Ensure invoice is submitted
#         if si.docstatus != 1:
#             continue

#         # Only for Overseas category
#         if si.gst_category != "Overseas":
#             continue

#         si.reload()

#         # Check fully paid
#         if si.outstanding_amount == 0:
#             si.workflow_state = "Completed Shipment"  # must match workflow
#             si.custom_work_flow_status = "Completed Shipment"
#             si.custom_payment_status = 1              # auto-enable checkbox
#             si.save(ignore_permissions=True)






# def on_submit(doc, method=None):
#     """
#     Automatically sets the custom_payment_received_date upon submission.
#     """
#     # Set the field to today's date
#     doc.custom_payment_received_date = nowdate()
    
#     # Since this is the 'on_submit' method, the system will save 
#     # the modified 'doc' object automatically. 
#     # No need for doc.db_set or doc.save() here.










# import frappe
# from frappe.utils import nowdate, flt

# def on_submit_update_sales_invoice(doc, method):
#     # Only for Customer payments
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
#             continue

#         si = frappe.get_doc("Sales Invoice", ref.reference_name)

#         # Ensure invoice is submitted
#         if si.docstatus != 1:
#             continue

#         # Only for Overseas category
#         if si.gst_category != "Overseas":
#             continue

#         si.reload()

#         # Check fully paid
#         if si.outstanding_amount == 0:
#             si.workflow_state = "Completed Shipment"
#             si.custom_work_flow_status = "Completed Shipment"
#             si.custom_payment_status = 1
#             si.save(ignore_permissions=True)

# def on_cancel(doc, method=None):
#     """
#     Logic for Cancellation: Reverts status if Invoice is Overseas and now Unpaid.
#     """
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            
#             # Fetch minimal info to check conditions
#             si_data = frappe.db.get_value("Sales Invoice", ref.reference_name, ["gst_category", "docstatus"], as_dict=1)
            
#             # Only proceed if it's Overseas and currently Submitted
#             if si_data and si_data.gst_category == "Overseas" and si_data.docstatus == 1:
                
#                 # Update the database directly. This is the MOST RELIABLE way for cancelled docs.
#                 frappe.db.set_value("Sales Invoice", ref.reference_name, {
#                     "workflow_state": "Document Submitted & Awaiting Payments",
#                     "custom_work_flow_status": "Document Submitted & Awaiting Payments",
#                     "status": "Unpaid",
#                     "custom_payment_status": 0  # Uncheck the box
#                 })
                
#                 # Add a comment to the Invoice so you can see it worked in the timeline
#                 frappe.get_doc("Sales Invoice", ref.reference_name).add_comment(
#                     "Info", f"Payment {doc.name} cancelled. Status reverted to Unpaid."
#                 )

# def on_submit(doc, method=None):
#     """
#     Sets the custom_payment_received_date upon submission.
#     """
#     doc.custom_payment_received_date = nowdate()








# This script automates the synchronization between Payment Entries and Sales Invoices for overseas transactions
#  by updating the workflow state to "Completed Shipment" upon full payment.
#  It also features a self-reverting mechanism that resets the invoice status and unchecks payment indicators 
# if a payment entry is cancelled, bypassing standard workflow restrictions to ensure data integrity.


# import frappe
# from frappe.utils import nowdate, flt


# # =========================================================
# # 🔹 PAYMENT ENTRY SUBMIT
# # =========================================================
# def on_submit(doc, method=None):
#     """Set payment date + update linked Sales Invoices"""
#     doc.db_set("custom_payment_received_date", nowdate())
#     on_submit_update_sales_invoice(doc)


# # =========================================================
# # 🔹 UPDATE SALES INVOICE ON PAYMENT
# # =========================================================
# def on_submit_update_sales_invoice(doc, method=None):
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
#             continue

#         si = frappe.get_doc("Sales Invoice", ref.reference_name)

#         if si.docstatus != 1 or si.gst_category != "Overseas":
#             continue

#         si.reload()

#         #  FULL PAYMENT CHECK
#         if flt(si.outstanding_amount) == 0:

#             # 🔹 Update Sales Invoice
#             si.db_set("workflow_state", "Completed Shipment")
#             si.db_set("custom_work_flow_status", "Completed Shipment")
#             si.db_set("custom_payment_status", 1)
#             frappe.db.set_value("Sales Invoice", si.name, "status", "Completed Shipment")

#             # 🔹 Trigger your existing logic
#             try:
#                 path = "cit_exim.cit_exim.doc_events.sales_invoice"
#                 update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")
#                 handle_status = frappe.get_attr(f"{path}._handle_custom_status_change")

#                 update_so_qty(si)
#                 handle_status(si)

#             except Exception as e:
#                 frappe.log_error(f"SO Update Error: {str(e)}", "Payment Entry Hook")
#                 frappe.msgprint("SO sync failed. Check Error Log.")

#             # NEW: Update Consolidated Invoice
#             update_consolidated_status(si)


# # =========================================================
# # 🔹 UPDATE CONSOLIDATED INVOICE
# # =========================================================
# def update_consolidated_status(si):
#     if not si.custom_consolidated_invoice_reference:
#         return

#     consolidated_name = si.custom_consolidated_invoice_reference

#     # Get all submitted invoices under this consolidated
#     invoices = frappe.get_all(
#         "Sales Invoice",
#         filters={
#             "custom_consolidated_invoice_reference": consolidated_name,
#             "docstatus": 1
#         },
#         fields=["name", "workflow_state"]
#     )

#     if not invoices:
#         return

#     # Check ALL completed
#     all_completed = all(
#         inv.workflow_state == "Completed Shipment"
#         for inv in invoices
#     )

#     if not all_completed:
#         return

#     consolidated_doc = frappe.get_doc(
#         "Consolidated Sales Invoice",
#         consolidated_name
#     )

#     # Avoid duplicate update
#     if consolidated_doc.workflow_state == "Completed Shipment":
#         return

#     consolidated_doc.db_set("workflow_state", "Completed Shipment")

#     consolidated_doc.add_comment(
#         "Info",
#         text="Auto updated: All linked Sales Invoices are Completed Shipment"
#     )


# # =========================================================
# # 🔹 PAYMENT CANCEL
# # =========================================================
# def on_cancel(doc, method=None):
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
#             continue

#         si_data = frappe.db.get_value(
#             "Sales Invoice",
#             ref.reference_name,
#             ["gst_category", "docstatus"],
#             as_dict=1
#         )

#         if not si_data:
#             continue

#         if si_data.gst_category == "Overseas" and si_data.docstatus == 1:

#             # 🔹 Revert Sales Invoice
#             frappe.db.set_value(
#                 "Sales Invoice",
#                 ref.reference_name,
#                 {
#                     "workflow_state": "Document Submitted & Awaiting Payments",
#                     "custom_work_flow_status": "Document Submitted & Awaiting Payments",
#                     "status": "Unpaid",
#                     "custom_payment_status": 0
#                 }
#             )

#             # 🔹 Recalculate SO
#             try:
#                 path = "cit_exim.cit_exim.doc_events.sales_invoice"
#                 update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")

#                 si = frappe.get_doc("Sales Invoice", ref.reference_name)
#                 update_so_qty(si)

#             except:
#                 pass

#             #  NEW: Revert Consolidated Invoice
#             revert_consolidated_status(ref.reference_name)


# # =========================================================
# # 🔹 REVERT CONSOLIDATED INVOICE
# # =========================================================
# def revert_consolidated_status(si_name):
#     si = frappe.get_doc("Sales Invoice", si_name)

#     if not si.custom_consolidated_invoice_reference:
#         return

#     consolidated_name = si.custom_consolidated_invoice_reference

#     invoices = frappe.get_all(
#         "Sales Invoice",
#         filters={
#             "custom_consolidated_invoice_reference": consolidated_name,
#             "docstatus": 1
#         },
#         fields=["workflow_state"]
#     )

#     if not invoices:
#         return

#     #  If ANY invoice is NOT completed → revert
#     any_pending = any(
#         inv.workflow_state != "Completed Shipment"
#         for inv in invoices
#     )

#     if not any_pending:
#         return

#     frappe.db.set_value(
#         "Consolidated Sales Invoice",
#         consolidated_name,
#         "workflow_state",
#         "Document Submitted & Awaiting Payments"
#     )
# import frappe
# from frappe.utils import flt

# @frappe.whitelist()
# def get_sales_invoices(consolidated_invoice):

#     if not consolidated_invoice:
#         return []

#     invoices = frappe.get_all(
#         "Sales Invoice",
#         filters={
#             "custom_consolidated_invoice_reference": consolidated_invoice,
#             "docstatus": 1,
#             "outstanding_amount": [">", 0]
#         },
#         fields=["name", "grand_total", "outstanding_amount"]
#     )

#     for inv in invoices:
#         inv["grand_total"] = flt(inv.get("grand_total"))
#         inv["outstanding_amount"] = flt(inv.get("outstanding_amount"))

#     return invoices


# def validate(doc, method):

#     if not doc.custom_get_from_consolidated_sales_invoice:
#         return

#     if not doc.custom_consolidated_sales_invoice:
#         return

#     #  Step 1: Get invoices in FIFO order
#     invoices = frappe.get_all(
#         "Sales Invoice",
#         filters={
#             "custom_consolidated_invoice_reference": doc.custom_consolidated_sales_invoice,
#             "docstatus": 1,
#             "outstanding_amount": [">", 0]
#         },
#         fields=["name", "grand_total", "outstanding_amount", "posting_date"],
#         order_by="posting_date asc"   #  FIFO
#     )

#     #Step 2: Clear table
#     doc.set("references", [])

#     #  Step 3: Total amount to distribute
#     remaining = flt(doc.paid_amount)

#     #  Step 4: FIFO Allocation
#     for inv in invoices:

#         outstanding = flt(inv.outstanding_amount)

#         if remaining <= 0:
#             allocated = 0

#         elif remaining >= outstanding:
#             allocated = outstanding
#             remaining -= outstanding

#         else:
#             allocated = remaining
#             remaining = 0

#         doc.append("references", {
#             "reference_doctype": "Sales Invoice",
#             "reference_name": inv.name,
#             "total_amount": flt(inv.grand_total),
#             "outstanding_amount": outstanding,
#             "allocated_amount": allocated
#         })



# import frappe

# @frappe.whitelist()
# def get_filtered_consolidated_invoices(doctype, txt, searchfield, start, page_len, filters):

#     party = filters.get("party")

#     conditions = [
#         "docstatus = 1",
#         "TRIM(workflow_state) = %s",
#         "name LIKE %s"
#     ]

#     values = [
#         "Document Submitted & Awaiting Payments",
#         f"%{txt}%"
#     ]

#     # 🔴 IMPORTANT: apply party filter ONLY if field exists in your doctype
#     # change 'customer' if your Consolidated Sales Invoice uses different field
#     if party:
#         conditions.append("customer = %s")
#         values.append(party)

#     where_clause = " AND ".join(conditions)

#     values.extend([start, page_len])

#     return frappe.db.sql(f"""
#         SELECT
#             name,
#             name as label
#         FROM `tabConsolidated Sales Invoice`
#         WHERE {where_clause}
#         ORDER BY modified DESC
#         LIMIT %s, %s
#     """, values)






import frappe
from frappe.utils import nowdate, flt


# =========================================================
# 🔹 PAYMENT ENTRY SUBMIT
# =========================================================
def on_submit(doc, method=None):
    """Set payment date + update linked Sales Invoices"""
    doc.db_set("custom_payment_received_date", nowdate())
    on_submit_update_sales_invoice(doc)

    # ✅ NEW: Update consolidated outstanding
    update_consolidated_outstanding_from_pe(doc)


# =========================================================
# 🔹 UPDATE SALES INVOICE ON PAYMENT
# =========================================================
def on_submit_update_sales_invoice(doc, method=None):
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
            continue

        si = frappe.get_doc("Sales Invoice", ref.reference_name)

        if si.docstatus != 1 or si.gst_category != "Overseas":
            continue

        si.reload()

        #  FULL PAYMENT CHECK
        if flt(si.outstanding_amount) == 0:
            
            # 🔹 Update Sales Invoice
            si.db_set("workflow_state", "Completed Shipment")
            si.db_set("custom_work_flow_status", "Completed Shipment")
            si.db_set("custom_payment_status", 1)
            frappe.db.set_value("Sales Invoice", si.name, "status", "Completed Shipment")

            # 🔹 Trigger your existing logic
            try:
                path = "cit_exim.cit_exim.doc_events.sales_invoice"
                update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")
                handle_status = frappe.get_attr(f"{path}._handle_custom_status_change")

                update_so_qty(si)
                handle_status(si)

            except Exception as e:
                frappe.log_error(f"SO Update Error: {str(e)}", "Payment Entry Hook")
                frappe.msgprint("SO sync failed. Check Error Log.")

            # NEW: Update Consolidated Invoice
            update_consolidated_status(si)


# =========================================================
# 🔹 UPDATE CONSOLIDATED INVOICE STATUS
# =========================================================
def update_consolidated_status(si):
    if not si.custom_consolidated_invoice_reference:
        return

    consolidated_name = si.custom_consolidated_invoice_reference

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_consolidated_invoice_reference": consolidated_name,
            "docstatus": 1
        },
        fields=["name", "workflow_state"]
    )

    if not invoices:
        return

    all_completed = all(
        inv.workflow_state == "Completed Shipment"
        for inv in invoices
    )

    if not all_completed:
        return

    consolidated_doc = frappe.get_doc(
        "Consolidated Sales Invoice",
        consolidated_name
    )

    if consolidated_doc.workflow_state == "Completed Shipment":
        return

    consolidated_doc.db_set("workflow_state", "Completed Shipment")

    consolidated_doc.add_comment(
        "Info",
        text="Auto updated: All linked Sales Invoices are Completed Shipment"
    )


# =========================================================
# 🔹 PAYMENT CANCEL
# =========================================================
def on_cancel(doc, method=None):
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
            continue

        si_data = frappe.db.get_value(
            "Sales Invoice",
            ref.reference_name,
            ["gst_category", "docstatus"],
            as_dict=1
        )

        if not si_data:
            continue

        if si_data.gst_category == "Overseas" and si_data.docstatus == 1:

            frappe.db.set_value(
                "Sales Invoice",
                ref.reference_name,
                {
                    "workflow_state": "Document Submitted & Awaiting Payments",
                    "custom_work_flow_status": "Document Submitted & Awaiting Payments",
                    "status": "Unpaid",
                    "custom_payment_status": 0
                }
            )

            try:
                path = "cit_exim.cit_exim.doc_events.sales_invoice"
                update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")

                si = frappe.get_doc("Sales Invoice", ref.reference_name)
                update_so_qty(si)

            except:
                pass

            #  NEW: Revert Consolidated Invoice
            revert_consolidated_status(ref.reference_name)

    # ✅ NEW: Update consolidated outstanding on cancel
    update_consolidated_outstanding_from_pe(doc)


# =========================================================
# 🔹 REVERT CONSOLIDATED INVOICE
# =========================================================
def revert_consolidated_status(si_name):
    si = frappe.get_doc("Sales Invoice", si_name)

    if not si.custom_consolidated_invoice_reference:
        return

    consolidated_name = si.custom_consolidated_invoice_reference

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_consolidated_invoice_reference": consolidated_name,
            "docstatus": 1
        },
        fields=["workflow_state"]
    )

    if not invoices:
        return

    any_pending = any(
        inv.workflow_state != "Completed Shipment"
        for inv in invoices
    )

    if not any_pending:
        return

    frappe.db.set_value(
        "Consolidated Sales Invoice",
        consolidated_name,
        "workflow_state",
        "Document Submitted & Awaiting Payments"
    )


# =========================================================
# ✅ NEW: UPDATE CONSOLIDATED OUTSTANDING FROM PAYMENT ENTRY
# =========================================================
def update_consolidated_outstanding_from_pe(doc):
    consolidated_set = set()

    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            consolidated_name = frappe.db.get_value(
                "Sales Invoice",
                ref.reference_name,
                "custom_consolidated_invoice_reference"
            )
            if consolidated_name:
                consolidated_set.add(consolidated_name)

    for consolidated in consolidated_set:
        update_consolidated_outstanding(consolidated)


# =========================================================
# ✅ NEW: CORE OUTSTANDING CALCULATION
# =========================================================
def update_consolidated_outstanding(consolidated_name):
    from frappe.utils import flt

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_consolidated_invoice_reference": consolidated_name,
            "docstatus": 1
        },
        fields=["outstanding_amount"]
    )

    total_outstanding = sum(flt(inv.outstanding_amount) for inv in invoices)

    frappe.db.set_value(
        "Consolidated Sales Invoice",
        consolidated_name,
        "outstanding_amount",
        total_outstanding
    )






def validate(doc, method):

    if not doc.custom_get_from_consolidated_sales_invoice:
        return

    if not doc.custom_consolidated_sales_invoice:
        return

    #  Step 1: Get invoices in FIFO order
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_consolidated_invoice_reference": doc.custom_consolidated_sales_invoice,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=["name", "grand_total", "outstanding_amount", "posting_date"],
        order_by="posting_date asc"   #  FIFO
    )

    #Step 2: Clear table
    doc.set("references", [])

    #  Step 3: Total amount to distribute
    remaining = flt(doc.paid_amount)

    #  Step 4: FIFO Allocation
    for inv in invoices:

        outstanding = flt(inv.outstanding_amount)

        if remaining <= 0:
            allocated = 0

        elif remaining >= outstanding:
            allocated = outstanding
            remaining -= outstanding

        else:
            allocated = remaining
            remaining = 0

        doc.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": inv.name,
            "total_amount": flt(inv.grand_total),
            "outstanding_amount": outstanding,
            "allocated_amount": allocated
        })




import frappe

@frappe.whitelist()
def get_filtered_consolidated_invoices(doctype, txt, searchfield, start, page_len, filters):

    party = filters.get("party")

    conditions = [
    "docstatus IN (0, 1)",
    "TRIM(workflow_state) = %s",
    "name LIKE %s"
]

    values = [
        "Document Submitted & Awaiting Payments",
        f"%{txt}%"
    ]

    # 🔴 IMPORTANT: apply party filter ONLY if field exists in your doctype
    # change 'customer' if your Consolidated Sales Invoice uses different field
    if party:
        conditions.append("customer = %s")
        values.append(party)

    where_clause = " AND ".join(conditions)

    values.extend([start, page_len])

    return frappe.db.sql(f"""
        SELECT
            name,
            name as label
        FROM `tabConsolidated Sales Invoice`
        WHERE {where_clause}
        ORDER BY modified DESC
        LIMIT %s, %s
    """, values)




import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_sales_invoices(consolidated_invoice):

    if not consolidated_invoice:
        return []

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_consolidated_invoice_reference": consolidated_invoice,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=["name", "grand_total", "outstanding_amount"]
    )

    for inv in invoices:
        inv["grand_total"] = flt(inv.get("grand_total"))
        inv["outstanding_amount"] = flt(inv.get("outstanding_amount"))

    return invoices
