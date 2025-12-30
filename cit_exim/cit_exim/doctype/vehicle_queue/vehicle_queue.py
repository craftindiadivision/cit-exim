# Copyright (c) 2025, craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleQueue(Document):
    def validate(self):
        if self.gross_weight is not None and self.tare_weight is not None:
            self.net_weight = self.gross_weight - self.tare_weight
        else:
            self.net_weight = 0  



@frappe.whitelist()
def create_purchase_voucher(doc, method):
    doc = frappe.get_doc(doc.get("doctype"), doc.get("name"))

    if not doc.supplier:
        return

    pv = frappe.new_doc("Purchase Voucher")
    pv.supplier = doc.supplier
    pv.company_name = doc.company
    pv.date = doc.date
    pv.time = doc.time
    pv.custom_vehicle_queue = doc.name
    pv.branch = doc.branch
    pv.accepted_warehouse = doc.warehouse
    pv.weigment_sino = doc.name
    pv.vehicle_no = doc.vehicle_no
    pv.vendor_name = doc.supplier
    pv.vehicle_queue_reference = doc.name
    pv.accepted_warehouse = doc.warehouse
    # pv.1st_weightkg = doc.gross_weight
    pv.set("1st_weightkg", doc.gross_weight)
    pv.set("2nd_weightkg",doc.tare_weight)
    pv.net_weightkg = doc.net_weight

    # Map Product Name to the Item Group of the Vehicle Queue's item
    item_group = frappe.db.get_value("Item", doc.item, "item_group")
    if item_group:
        pv.product_name = item_group

    # Add item details to the child table 'raw_materials'
    pv.append("raw_materials", {
        "fish_variety": doc.item,       
        "warehouse": doc.warehouse,  
        "no_of_boxes": doc.no_of_bags,
        "gross_weight": doc.gross_weight,
        "tare_weight": doc.tare_weight,
        "net_weight": doc.net_weight
    })

    pv.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.msgprint(f"Purchase Voucher Draft Created : <b>{pv.name}</b>")
