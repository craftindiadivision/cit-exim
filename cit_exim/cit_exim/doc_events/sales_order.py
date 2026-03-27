import frappe
from frappe.model.document import Document
from frappe import _

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




@frappe.whitelist()
def get_customer_billing_address(customer):
    """
    Returns the primary billing address of a Customer.
    """
    # Get address linked to this customer
    address = frappe.db.sql("""
        SELECT a.name
        FROM `tabAddress` a
        JOIN `tabDynamic Link` dl
            ON dl.parent = a.name
        WHERE dl.link_doctype = 'Customer'
          AND dl.link_name = %s
          AND a.is_primary_address = 1
        LIMIT 1
    """, customer, as_dict=True)

    if address:
        return address[0].name
    return None







@frappe.whitelist()
def get_billing_address_for_customer(customer):
    """
    Returns a valid Billing Address linked to the selected customer.
    """

    if not customer:
        return None

    # Find billing address linked to this customer
    address = frappe.db.sql("""
        SELECT a.name
        FROM `tabAddress` a
        INNER JOIN `tabDynamic Link` dl
            ON dl.parent = a.name
        WHERE dl.link_doctype = 'Customer'
          AND dl.link_name = %s
          AND a.disabled = 0
          AND (
                a.address_type = 'Billing'
                OR a.is_primary_address = 1
          )
        ORDER BY
            a.is_primary_address DESC,
            a.modified DESC
        LIMIT 1
    """, (customer,), as_dict=True)

    return address[0].name if address else None








# -------------------------------corrected code-------------------


import frappe
from frappe import _

@frappe.whitelist()
def map_buyer_to_consignee_address(buyer, consignee):
    if not buyer or not consignee:
        frappe.throw(_("Buyer and Consignee are required"))

    # 1. Get Consignee Address (DO NOT MODIFY LINKS)
    address = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": consignee,
            "parenttype": "Address"
        },
        fields=["parent"],
        limit=1
    )

    if not address:
        frappe.throw(_("No Address found linked to Consignee: {0}").format(consignee))

    address_name = address[0].parent

    # 2. Get Address document
    address_doc = frappe.get_doc("Address", address_name)

    # 3. Get formatted address
    address_display = address_doc.get_display()

    # 4. Return ONLY values (no DB modification)
    return {
        "shipping_address_name": address_doc.name,
        "shipping_address": address_display
    }

























# import frappe

# @frappe.whitelist()
# def get_consignee_default_address(customer):

#     address = frappe.db.sql("""
#         SELECT 
#             a.name
#         FROM `tabAddress` a
#         INNER JOIN `tabDynamic Link` dl 
#             ON dl.parent = a.name
#         WHERE dl.link_doctype = 'Customer'
#         AND dl.link_name = %s
#         ORDER BY
#             a.is_shipping_address DESC,
#             a.is_primary_address DESC
#         LIMIT 1
#     """, (customer), as_dict=True)

#     if not address:
#         return None

#     addr_name = address[0].name
#     addr_doc = frappe.get_doc("Address", addr_name)

#     return {
#         "name": addr_doc.name,
#         "display": addr_doc.get_display()
#     }












# @frappe.whitelist()
# def get_customer_shipping_address(customer):
#     """
#     Returns Shipping Address of a Customer (Consignee).
#     Handles real ERPNext address structure.
#     """

#     address = frappe.db.sql("""
#         SELECT a.name
#         FROM `tabAddress` a
#         INNER JOIN `tabDynamic Link` dl
#             ON dl.parent = a.name
#         WHERE dl.link_doctype = 'Customer'
#           AND dl.link_name = %s
#           AND a.disabled = 0
#           AND (
#                 a.address_type = 'Shipping'
#                 OR a.is_shipping_address = 1
#           )
#         ORDER BY
#             a.is_primary_address DESC,
#             a.modified DESC
#         LIMIT 1
#     """, (customer,), as_dict=True)

#     return address[0].name if address else None










import frappe

def validate(doc, method=None):
    if doc.branch:

        address = frappe.db.get_value(
            "Address",
            {
                "custom_branch": doc.branch,
                "is_your_company_address": 1
            },
            "name"
        )

        if address:
            doc.company_address = address
        else:

            company_address = frappe.db.get_value(
                "Dynamic Link",
                {
                    "link_doctype": "Company",
                    "link_name": doc.company,
                    "parenttype": "Address"
                },
                "parent"
            )

            if company_address:
                doc.company_address = company_address

    populate_banks(doc)


def populate_banks(doc):
    # Prevent duplicate rows
    if doc.get("custom_banks"):
        return

    banks = frappe.get_all(
        "Bank",
        fields=["name"],
        order_by="name"
    )

    for bank in banks:
        row = doc.append("custom_banks", {})
        row.bank = bank.name



# import frappe

# def before_save(doc, method=None):
#     populate_banks(doc)


# def populate_banks(doc):
#     # Run only once (prevents duplicates on every save)
#     if doc.get("custom_banks"):
#         return

#     banks = frappe.get_all(
#         "Bank",
#         fields=["name"],
#         order_by="name"
#     )

#     for bank in banks:
#         doc.append("custom_banks", {
#             "bank": bank.name
#         })


