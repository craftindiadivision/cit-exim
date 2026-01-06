import frappe

@frappe.whitelist()
def create_vehicle_queue(purchase_order):
    po = frappe.get_doc("Purchase Order", purchase_order)

    vq = frappe.new_doc("Vehicle Queue")

    # Header mappings

    vq.supplier = po.supplier
    vq.company = po.company
    vq.warehouse = po.set_warehouse
    vq.branch = po.branch
    vq.purchase_order = po.name

    # SAFE way to set reserved fieldname
    vq.set("type", "Inward")

    product_set = set()  # to avoid duplicates

    # Map items
    for po_item in po.items:

        # Get item_group from Item
        item_group = frappe.db.get_value(
            "Item",
            po_item.item_code,
            "item_group"
        )

        # Collect unique item groups
        if item_group:
            product_set.add(item_group)

        # Append child row
        vq.append("item", {
            "item": po_item.item_code
        })

    # Set product field (comma separated if multiple)
    vq.product = ", ".join(product_set)

    vq.save(ignore_permissions=True)
    frappe.db.commit()

    return vq.name
