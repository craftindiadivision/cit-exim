

# import frappe

# def on_submit_update_sales_invoice(doc, method):
#     # Only for Customer payments
#     if doc.party_type != "Customer":
#         return

#     for ref in doc.references:
#         if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
#             si = frappe.get_doc("Sales Invoice", ref.reference_name)

#             # Ensure invoice is submitted
#             if si.docstatus != 1:
#                 continue

#             # Only work for Overseas category
#             if si.gst_category != "Overseas":
#                 continue

#             si.reload()

#             # OPTIONAL: Check fully paid
#             if si.outstanding_amount == 0:
#                 si.workflow_state = "Completed Shipment"   # must match workflow exactly
#                 si.save(ignore_permissions=True)
# 




# update the status of sales invoice according to completion of payment entry

import frappe

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
            si.workflow_state = "Completed Shipment"  # must match workflow
            si.custom_work_flow_status = "Completed Shipment"
            si.custom_payment_status = 1              # auto-enable checkbox
            si.save(ignore_permissions=True)


import frappe
from frappe.utils import nowdate

def on_submit(doc, method=None):
    """
    Automatically sets the custom_payment_received_date upon submission.
    """
    # Set the field to today's date
    doc.custom_payment_received_date = nowdate()
    
    # Since this is the 'on_submit' method, the system will save 
    # the modified 'doc' object automatically. 
    # No need for doc.db_set or doc.save() here.