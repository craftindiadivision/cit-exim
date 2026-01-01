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

#             # OPTIONAL: Check if fully paid
#             si.reload()
#             if si.outstanding_amount == 0:
#                 # Change workflow state
#                 si.workflow_state = "Completed Shipment"   # must match your workflow state exactly
#                 si.save(ignore_permissions=True)



import frappe

def on_submit_update_sales_invoice(doc, method):
    # Only for Customer payments
    if doc.party_type != "Customer":
        return

    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            si = frappe.get_doc("Sales Invoice", ref.reference_name)

            # Ensure invoice is submitted
            if si.docstatus != 1:
                continue

            # Only work for Overseas category
            if si.gst_category != "Overseas":
                continue

            si.reload()

            # OPTIONAL: Check fully paid
            if si.outstanding_amount == 0:
                si.workflow_state = "Completed Shipment"   # must match workflow exactly
                si.save(ignore_permissions=True)
