
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










import frappe
from frappe.utils import nowdate, flt

def on_submit_update_sales_invoice(doc, method):
    # Only for Customer payments
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
            continue

        si = frappe.get_doc("Sales Invoice", ref.reference_name)

        # Ensure invoice is submitted
        if si.docstatus != 1:
            continue

        # Only for Overseas category
        if si.gst_category != "Overseas":
            continue

        si.reload()

        # Check fully paid
        if si.outstanding_amount == 0:
            si.workflow_state = "Completed Shipment"
            si.custom_work_flow_status = "Completed Shipment"
            si.custom_payment_status = 1
            si.save(ignore_permissions=True)

def on_cancel(doc, method=None):
    """
    Logic for Cancellation: Reverts status if Invoice is Overseas and now Unpaid.
    """
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            
            # Fetch minimal info to check conditions
            si_data = frappe.db.get_value("Sales Invoice", ref.reference_name, ["gst_category", "docstatus"], as_dict=1)
            
            # Only proceed if it's Overseas and currently Submitted
            if si_data and si_data.gst_category == "Overseas" and si_data.docstatus == 1:
                
                # Update the database directly. This is the MOST RELIABLE way for cancelled docs.
                frappe.db.set_value("Sales Invoice", ref.reference_name, {
                    "workflow_state": "Document Submitted & Awaiting Payments",
                    "custom_work_flow_status": "Document Submitted & Awaiting Payments",
                    "status": "Unpaid",
                    "custom_payment_status": 0  # Uncheck the box
                })
                
                # Add a comment to the Invoice so you can see it worked in the timeline
                frappe.get_doc("Sales Invoice", ref.reference_name).add_comment(
                    "Info", f"Payment {doc.name} cancelled. Status reverted to Unpaid."
                )

def on_submit(doc, method=None):
    """
    Sets the custom_payment_received_date upon submission.
    """
    doc.custom_payment_received_date = nowdate()