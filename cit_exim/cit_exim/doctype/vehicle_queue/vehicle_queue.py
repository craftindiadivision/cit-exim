# import frappe
# from frappe.model.document import Document


# class VehicleQueue(Document):

#     def validate(self):
#         # Net weight calculation
#         if self.gross_weight is not None and self.tare_weight is not None:
#             self.net_weight = self.gross_weight - self.tare_weight
#         else:
#             self.net_weight = 0


# def create_purchase_documents(doc, method=None):
#     """
#     Triggered on Vehicle Queue submit
#     """

#     # Only on submit
#     if doc.docstatus != 1:
#         return

#     # Only for Inward (Supplier)
#     if doc.type != "Inward":
#         return

#     if not doc.supplier:
#         frappe.throw("Supplier is mandatory for Inward Vehicle Queue")

#     if not doc.item:
#         frappe.throw("At least one Item is required")

#     # Take first item from child table
#     item_code = doc.item[0].item

#     # Fetch Item Group
#     item_group = frappe.db.get_value("Item", item_code, "item_group")

#     if not item_group:
#         return

#     # ==================================================
#     # CASE 1: RAW FISH → PURCHASE VOUCHER (DRAFT)
#     # ==================================================
#     if item_group == "Raw Fish":

#         if frappe.db.exists("Purchase Voucher", {
#             "vehicle_queue_reference": doc.name
#         }):
#             return

#         pv = frappe.new_doc("Purchase Voucher")
#         pv.supplier = doc.supplier
#         pv.company_name = doc.company
#         pv.date = doc.date
#         pv.time = doc.time
#         pv.branch = doc.branch
#         pv.vehicle_no = doc.vehicle_no

#         pv.vehicle_queue_reference = doc.name
#         pv.accepted_warehouse = doc.warehouse

#         pv.set("1st_weightkg", doc.gross_weight)
#         pv.set("2nd_weightkg", doc.tare_weight)
#         pv.net_weightkg = doc.net_weight

#         pv.product_name = item_group

#         pv.append("raw_materials", {
#             "fish_variety": item_code,
#             "warehouse": doc.warehouse,
#             "no_of_boxes": doc.no_of_bags,
#             "gross_weight": doc.gross_weight,
#             "tare_weight": doc.tare_weight,
#             "net_weight": doc.net_weight
#         })

#         pv.insert(ignore_permissions=True)

#         frappe.msgprint(
#             f"Purchase Voucher Draft Created: <b>{pv.name}</b>",
#             alert=True
#         )

    # ==================================================
    # # CASE 2: RM-FISH MEAL → PURCHASE ORDER (DRAFT)
    # # ==================================================
    # elif item_group == "RM-Fish Meal":

    #     if frappe.db.exists("Purchase Order", {
    #         "custom_vehicle_queue": doc.name
    #     }):
    #         return

    #     po = frappe.new_doc("Purchase Order")
    #     po.supplier = doc.supplier
    #     po.company = doc.company
    #     po.transaction_date = doc.date
    #     po.schedule_date = doc.date
    #     po.custom_vehicle_queue = doc.name
    #     po.set_warehouse = doc.warehouse
        
    #     po.append("items", {
    #         "item_code": item_code,
    #         "qty": (doc.no_of_bags or 0) * 50,
    #          "uom": frappe.db.get_value("Item", item_code, "stock_uom"),
    #     })

    #     po.insert(ignore_permissions=True)

    #     frappe.msgprint(
    #         f"Purchase Order Draft Created: <b>{po.name}</b>",
    #         alert=True
    #     )




# Copyright (c) 2025, craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleQueue(Document):

    def validate(self):
        # Calculate Net Weight
        if self.vehicle_no:
            self.vehicle_no = self.vehicle_no.replace(" ", "").upper()
        if self.gross_weight is not None and self.tare_weight is not None and self.ice_weight is not None :
            self.net_weight = self.gross_weight - self.tare_weight - self.ice_weight
        else:
            self.net_weight = 0
    def on_submit(self):
        # CONDITION CHECK
        if self.type != "Inward":
            return

        if self.product != "RM-Fish Meal":
            return

        if not self.purchase_order:
            frappe.throw("Purchase Order is mandatory to create Purchase Receipt")

        self.create_purchase_receipt()
    def on_cancel(self):
        self.delete_linked_purchase_receipt()
        self.delete_linked_purchase_voucher()

    def create_purchase_receipt(self):
    # Fetch Purchase Order
        po = frappe.get_doc("Purchase Order", self.purchase_order)

        # Create Purchase Receipt
        pr = frappe.new_doc("Purchase Receipt")
        pr.supplier = po.supplier
        pr.company = po.company
        pr.custom_purchase_order_ref = po.name
        pr.custom_vehicle_queue = self.name
        pr.custom_token_number = self.token_number
        pr.cost_center = self.cost_center
        pr.branch = self.branch
        pr.posting_date = frappe.utils.today()
        pr.posting_time = frappe.utils.nowtime()
        pr.vehicle_no = self.vehicle_no
        pr.set_warehouse = self.warehouse
        pr.custom_item_group = self.product

        # ---------------------------------------------------------
        # Map Items PO → PR
        # ---------------------------------------------------------
        for po_item in po.items:
            pr_item = pr.append("items", {})

            pr_item.item_code = po_item.item_code
            pr_item.item_name = po_item.item_name
            pr_item.description = po_item.description
            pr_item.custom_old_item_code = po_item.item_code
            pr_item.qty = self.net_weight
            pr_item.uom = po_item.uom
            pr_item.stock_uom = po_item.stock_uom
            pr_item.rejected_warehouse = ""

            # Get Item Group and Lab Template
            po_item_group = frappe.db.get_value(
                "Item", po_item.item_code, "item_group"
            )
            lab_template = frappe.db.get_value(
                "Item Group", po_item_group, "custom_test_variable_template"
            )
            pr_item.custom_test_variable_template = lab_template

            pr_item.rate = po_item.rate
            pr_item.warehouse = po_item.warehouse

            # Important PO Links
            # pr_item.purchase_order = po.name
            # pr_item.purchase_order_item = po_item.name

        # ---------------------------------------------------------
        # Map Taxes PO → PR
        # ---------------------------------------------------------
        pr.taxes = []

        for po_tax in po.taxes:
            pr_tax = pr.append("taxes", {})

            pr_tax.charge_type = po_tax.charge_type
            pr_tax.account_head = po_tax.account_head
            pr_tax.description = po_tax.description
            pr_tax.rate = po_tax.rate
            pr_tax.tax_amount = po_tax.tax_amount
            pr_tax.total = po_tax.total
            pr_tax.tax_amount_after_discount_amount = po_tax.tax_amount_after_discount_amount
            pr_tax.base_tax_amount = po_tax.base_tax_amount
            pr_tax.base_total = po_tax.base_total
            pr_tax.cost_center = po_tax.cost_center
            pr_tax.included_in_print_rate = po_tax.included_in_print_rate

        # ---------------------------------------------------------
        # Insert PR as Draft
        # ---------------------------------------------------------
        pr.insert(ignore_permissions=True)

        frappe.msgprint(
            f"Purchase Receipt <b>{pr.name}</b> created in Draft from Vehicle Queue"
        )
    def delete_linked_purchase_receipt(self):

        prs = frappe.get_all(
            "Purchase Receipt",
            filters={
                "custom_vehicle_queue": self.name,
                "docstatus": 0
            },
            pluck="name"
        )

        for pr_name in prs:

            # --------------------------------------------------
            # 1️⃣ DELETE LINKED LABORATORY REGISTERS FIRST
            # --------------------------------------------------
            lab_registers = frappe.get_all(
                "Laboratory Register",
                filters={
                    "reference_name": pr_name,
                    "docstatus": 0
                },
                pluck="name"
            )

            for lr_name in lab_registers:
                lr = frappe.get_doc("Laboratory Register", lr_name)
                lr.delete(ignore_permissions=True)

            # --------------------------------------------------
            # 2️⃣ DELETE PURCHASE RECEIPT
            # --------------------------------------------------
            pr = frappe.get_doc("Purchase Receipt", pr_name)
            pr.delete(ignore_permissions=True)

    # --------------------------------------------------
    # DELETE PURCHASE VOUCHER
    # --------------------------------------------------
    def delete_linked_purchase_voucher(self):
        pvs = frappe.get_all(
            "Purchase Voucher",
            filters={
                "vehicle_queue": self.name,
                "docstatus": 0
            },
            pluck="name"
        )

        for pv_name in pvs:
            pv = frappe.get_doc("Purchase Voucher", pv_name)
            pv.delete(ignore_permissions=True)

def create_purchase_voucher(doc, method=None):
    """
    Triggered on Vehicle Queue submit
    Conditions:
    1. Vehicle Queue must be Submitted
    2. Item Group must be 'Raw Fish'
    3. Purchase Voucher created in Draft
    4. Prevent duplicate creation
    """

    # Ensure submit state
    if doc.docstatus != 1:
        return

    # Mandatory validations
    if not doc.supplier:
        frappe.throw("Supplier is required to create Purchase Voucher")

    if not doc.item:
        frappe.throw("Item is required to create Purchase Voucher")

    # Vehicle Queue has CHILD TABLE item → take first row ONLY for validation
    first_item_code = doc.item[0].item

    # Fetch Item Group
    item_group = frappe.db.get_value("Item", first_item_code, "item_group")

    # Condition: Item Group must be 'Raw Fish'
    if item_group != "Raw Fish":
        return

    # Create Purchase Voucher (Draft)
    pv = frappe.new_doc("Purchase Voucher")
    pv.supplier = doc.supplier
    pv.company_name = doc.company
    pv.date = doc.date

    pv.cost_center = doc.cost_center
    pv.branch = doc.branch
    pv.vehicle_no = doc.vehicle_no
    pv.vendor_name = doc.supplier
    pv.vehicle_queue = doc.name
    pv.accepted_warehouse = doc.warehouse
    pv.weigment_sino = doc.token_number
    pv.weigment_location = doc.weigh_bridge_name
    pv.driver_name=doc.driver_name

    # Weight mapping
    pv.set("1st_weightkg", doc.gross_weight)
    pv.set("2nd_weightkg", doc.tare_weight)
    pv.ice_weightkg = doc.ice_weight
    pv.net_weightkg = doc.net_weight
    pv.loading_location = doc.loading_location
    # Product Name = Item Group
    pv.product_name = item_group

    # ----------------------------
    # Child table mapping (ALL ITEMS)
    # ----------------------------
    for row in doc.item:
        pv.append("raw_materials", {
            "fish_variety": row.item,        # Vehicle Queue Item
            "warehouse": doc.warehouse,
            "no_of_boxes": row.no_of_bags,    # Vehicle Queue noof_bags
            "gross_weight": doc.gross_weight,
            "tare_weight": doc.tare_weight,
            "net_weight": doc.net_weight
        })

    pv.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.msgprint(
        f"Purchase Voucher Draft Created : <b>{pv.name}</b>",
        alert=True
    )
import frappe
import json
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_vehicle_queue_from_po(source_name, target_doc=None, args=None):
  if args is None:
    args = {}
  if isinstance(args, str):
    args = json.loads(args)

  def update_item(source, target, source_parent):
    target.item = source.item_code

  def select_item(d):
    filtered_items = args.get("filtered_children", [])
    return d.name in filtered_items if filtered_items else True

  doc = get_mapped_doc(
    "Purchase Order",
    source_name,
    {
      "Purchase Order": {
        "doctype": "Vehicle Queue",
        "validation": {"docstatus": ["=", 1]},
      },
      "Purchase Order Item": {
        "doctype": "Vehicle Queue Item",
        "postprocess": update_item,
        "condition": lambda d: select_item(d),
      },
    },
    target_doc,
  )

  return doc