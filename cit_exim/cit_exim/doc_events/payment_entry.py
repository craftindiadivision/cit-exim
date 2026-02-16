
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


import frappe
from frappe.utils import nowdate, flt

def on_submit(doc, method=None):
    """Sets the custom date on Payment Entry and triggers SI update"""
    doc.db_set("custom_payment_received_date", nowdate())
    on_submit_update_sales_invoice(doc, method)

def on_submit_update_sales_invoice(doc, method=None):
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            si = frappe.get_doc("Sales Invoice", ref.reference_name)

            if si.docstatus == 1 and si.gst_category == "Overseas":
                si.reload()

                if flt(si.outstanding_amount) == 0:
                    # 1. Update Sales Invoice Database
                    si.db_set("workflow_state", "Completed Shipment")
                    si.db_set("custom_work_flow_status", "Completed Shipment")
                    si.db_set("custom_payment_status", 1)
                    frappe.db.set_value("Sales Invoice", si.name, "status", "Completed Shipment")

                    # 2. Trigger Calculations using your confirmed path
                    try:
                        # Path: cit_exim (app) . cit_exim (pkg) . doc_events (folder) . sales_invoice (file)
                        path = "cit_exim.cit_exim.doc_events.sales_invoice"
                        update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")
                        handle_status = frappe.get_attr(f"{path}._handle_custom_status_change")
                        
                        update_so_qty(si)
                        handle_status(si)
                    except Exception as e:
                        frappe.log_error(f"SO Update Error: {str(e)}", "Payment Entry Hook")
                        frappe.msgprint("Status updated, but Sales Order quantities failed to sync. Check Error Log.")

def on_cancel(doc, method=None):
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            si_data = frappe.db.get_value("Sales Invoice", ref.reference_name, ["gst_category", "docstatus"], as_dict=1)
            
            if si_data and si_data.gst_category == "Overseas" and si_data.docstatus == 1:
                # Revert Database
                frappe.db.set_value("Sales Invoice", ref.reference_name, {
                    "workflow_state": "Document Submitted & Awaiting Payments",
                    "custom_work_flow_status": "Document Submitted & Awaiting Payments",
                    "status": "Unpaid",
                    "custom_payment_status": 0
                })
                
                # Recalculate Sales Order to subtract quantities
                try:
                    path = "cit_exim.cit_exim.doc_events.sales_invoice"
                    update_so_qty = frappe.get_attr(f"{path}.update_sales_order_qty")
                    si = frappe.get_doc("Sales Invoice", ref.reference_name)
                    update_so_qty(si)
                except:
                    pass