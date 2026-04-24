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



# import frappe
# from frappe.utils import flt


# def update_so_delivery_qty(doc, method=None):

#     so_qty_map = {}

#     # collect qty per Sales Order
#     for item in doc.items:
#         so = item.against_sales_order
#         if not so:
#             continue

#         so_qty_map[so] = so_qty_map.get(so, 0) + flt(item.qty)

#     # add delivered qty on submit
#     for so, qty in so_qty_map.items():
#         frappe.db.sql("""
#             UPDATE `tabSales Order`
#             SET custom_delivered_qty = IFNULL(custom_delivered_qty, 0) + %s
#             WHERE name = %s
#         """, (qty, so))

#     frappe.db.commit()



# def rollback_so_delivery_qty(doc, method=None):

#     so_qty_map = {}

#     # collect qty per Sales Order
#     for item in doc.items:
#         so = item.against_sales_order
#         if not so:
#             continue

#         so_qty_map[so] = so_qty_map.get(so, 0) + flt(item.qty)

#     # subtract delivered qty on cancel
#     for so, qty in so_qty_map.items():
#         frappe.db.sql("""
#             UPDATE `tabSales Order`
#             SET custom_delivered_qty = IFNULL(custom_delivered_qty, 0) - %s
#             WHERE name = %s
#         """, (qty, so))

#     frappe.db.commit()


import frappe
from frappe.utils import flt


def update_so_delivery_qty(doc, method=None):

    so_qty_map = {}

    # collect delivered qty per Sales Order
    for item in doc.items:
        so = item.against_sales_order
        if not so:
            continue

        so_qty_map[so] = so_qty_map.get(so, 0) + flt(item.qty)

    # update delivered qty + pending qty
    for so, qty in so_qty_map.items():

        # 1. Update delivered qty
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET custom_delivered_qty = IFNULL(custom_delivered_qty, 0) + %s
            WHERE name = %s
        """, (qty, so))

        # 2. Recalculate pending qty
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET custom_pending_qty = 
                IFNULL(total_qty, 0) - IFNULL(custom_delivered_qty, 0)
            WHERE name = %s
        """, (so,))


def rollback_so_delivery_qty(doc, method=None):

    so_qty_map = {}

    # collect qty per Sales Order
    for item in doc.items:
        so = item.against_sales_order
        if not so:
            continue

        so_qty_map[so] = so_qty_map.get(so, 0) + flt(item.qty)

    # rollback delivered qty + recalc pending
    for so, qty in so_qty_map.items():

        # 1. subtract delivered qty
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET custom_delivered_qty = IFNULL(custom_delivered_qty, 0) - %s
            WHERE name = %s
        """, (qty, so))

        # 2. recalculate pending qty
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET custom_pending_qty = 
                IFNULL(total_qty, 0) - IFNULL(custom_delivered_qty, 0)
            WHERE name = %s
        """, (so,))