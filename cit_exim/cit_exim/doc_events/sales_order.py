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




@frappe.whitelist()
def get_customer_shipping_address(customer):
    """
    Returns Shipping Address of a Customer (Consignee).
    Handles real ERPNext address structure.
    """

    address = frappe.db.sql("""
        SELECT a.name
        FROM `tabAddress` a
        INNER JOIN `tabDynamic Link` dl
            ON dl.parent = a.name
        WHERE dl.link_doctype = 'Customer'
          AND dl.link_name = %s
          AND a.disabled = 0
          AND (
                a.address_type = 'Shipping'
                OR a.is_shipping_address = 1
          )
        ORDER BY
            a.is_primary_address DESC,
            a.modified DESC
        LIMIT 1
    """, (customer,), as_dict=True)

    return address[0].name if address else None
