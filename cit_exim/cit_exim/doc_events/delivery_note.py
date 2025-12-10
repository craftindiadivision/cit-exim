# def before_insert(doc, method):
#     # Copy producer table only when created from Sales Invoice
#     if doc.get("items") and len(doc.items) > 0:
#         si_name = doc.items[0].against_sales_invoice
#         if si_name:
#             copy_producers_from_sales_invoice(doc, si_name)


# def copy_producers_from_sales_invoice(doc, sales_invoice):
#     si = frappe.get_doc("Sales Invoice", sales_invoice)

#     # Clear existing rows first
#     doc.custom_producer_table = []

#     for row in si.custom_producer_table:
#         child = doc.append("custom_producer_table", {})
#         child.producer = row.producer
#         child.address = row.address
#         child.selected = row.selected