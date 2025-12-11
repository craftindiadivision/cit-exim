import frappe

@frappe.whitelist()
def get_producers():
    return frappe.get_all(
        "Producer",
        fields=["name", "producer_name"]
    )

@frappe.whitelist()
def get_consignee_list(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []

    addresses = frappe.db.get_all(
        "Address",
        filters={
            "custom_is_consignee": 1,
            "link_doctype": "Customer",
            "link_name": customer,
        },
        fields=["custom_consignee_name"]
    )

    # Return list of tuples (required for link field query)
    return [(d.custom_consignee_name,) for d in addresses]





# @frappe.whitelist()
# def get_consignee_list(doctype, txt, searchfield, start, page_len, filters):
#     customer = filters.get("customer")

#     if not customer:
#         return []

#     addresses = frappe.db.get_all(
#         "Address",
#         filters={
#             "custom_is_consignee": 1,
#             "link_doctype": "Customer",
#             "link_name": customer,
#         },
#         fields=["name", "custom_consignee_name"]
#     )

#     # Return (value, label) so Link field can save correctly
#     return [(d.name, d.custom_consignee_name) for d in addresses]




