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
import json
from frappe.utils import flt,get_time,nowdate, getdate
from frappe.model.mapper import get_mapped_doc



class VehicleQueue(Document):

    def validate(self):
        self.validate_supplier_invoice_number()
        # if self.product != "Raw Fish":
        #     if self.net_weight != self.invoice_qty:
        #         frappe.msgprint(
        #                 f"""
        #                 <b>Weight Mismatch</b><br><br>
        #                 There is a difference between the invoice quantity and the load weight.<br><br>
                        
        #                 <b>Invoice Quantity:</b> {self.invoice_qty}<br>
        #                 <b>Load Weight:</b> {self.net_weight}<br><br>
                        
        #                 Please verify the values before proceeding.
        #                 """,
        #                 indicator="orange"
        #             )
        #     for row in self.item:
        #         row.net_weight = (row.no_of_bags or 0) * (row.conversion_factor_kg or 0)
        #     child_total = sum([row.net_weight or 0 for row in self.item])
        #     voucher_net = self.net_weight or 0
        #     print(child_total,voucher_net,"total values")
        #     if child_total != voucher_net:
        #         frappe.msgprint(
        #             f"""
        #             <b>Weight Mismatch Warning</b><br>
        #             Items Total Weight: {child_total}<br>
        #             Load Weight: {voucher_net}
        #             """,
        #             indicator="orange"
        #         )
            # Calculate Net Weight
        if self.vehicle_no:
            self.vehicle_no = self.vehicle_no.replace(" ", "").upper()
    def validate_supplier_invoice_number(self):

        if self.supplier_invoice_number:
            fiscal_year = get_fiscal_year(self.date, company=self.company, as_dict=True)

            vq = frappe.db.sql("""
                SELECT name
                FROM `tabVehicle Queue`
                WHERE supplier_invoice_number = %(supplier_invoice_number)s
                AND supplier = %(supplier)s
                AND name != %(name)s
                AND docstatus < 2
                AND date BETWEEN %(year_start_date)s AND %(year_end_date)s
            """, {
                "supplier_invoice_number": self.supplier_invoice_number,
                "supplier": self.supplier,
                "name": self.name,
                "year_start_date": fiscal_year.year_start_date,
                "year_end_date": fiscal_year.year_end_date
            })

            if vq:
                vq_name = vq[0][0]

                frappe.throw(
                    _("Supplier Invoice Number already exists in Vehicle Queue {0}").format(
                        frappe.utils.get_link_to_form("Vehicle Queue", vq_name)
                    )
                )



        # if self.gross_weight is not None and self.tare_weight is not None and self.ice_weight is not None :
        #     self.net_weight = self.gross_weight - self.tare_weight - self.ice_weight
        # else:
        #     self.net_weight = 0
        # supplier_invoice_amount = 0

        # if self.invoice_qty and self.item:
        #     rate = self.item[0].rate or 0
        #     supplier_invoice_amount = self.invoice_qty * rate

        # self.supplier_invoice_amount = supplier_invoice_amount

        # for row in self.item:
        #     rate = row.rate or 0
        #     net_weight = self.net_weight or 0

        #     row.amount = net_weight * rate
        #     self.difference_in_amount = supplier_invoice_amount - row.amount
    def on_submit(self):
        # CONDITION CHECK
        if self.type != "Inward":
            return

        if self.product not in ["RM-Fish Meal", "Soluble Paste", "Fish Oil"]:
            return

        # if not self.purchase_order:
        #     frappe.throw("Purchase Order is mandatory to create Purchase Receipt")

        self.create_purchase_receipt()
    def on_cancel(self):
        self.delete_linked_purchase_receipt()
        self.delete_linked_purchase_voucher()

    def create_purchase_receipt(self):

        if self.purchase_order:

            po = frappe.get_doc("Purchase Order", self.purchase_order)

            pr = frappe.new_doc("Purchase Receipt")
            pr.supplier = po.supplier
            pr.company = po.company
            pr.custom_purchase_order_ref = po.name
            pr.custom_vehicle_queue = self.name
            pr.custom_token_number = self.token_number
            pr.cost_center = self.cost_center
            pr.branch = self.branch
            pr.posting_date = self.date
            pr.posting_time = get_time(self.out_time)
            pr.vehicle_no = self.vehicle_no
            pr.set_warehouse = self.warehouse
            pr.custom_item_group = self.product

            # Map Items PO → PR
            for po_item in po.items:
                pr_item = pr.append("items", {})

                pr_item.item_code = po_item.item_code
                pr_item.item_name = po_item.item_name
                pr_item.description = po_item.description
                pr_item.custom_old_item_code = po_item.item_code
                pr_item.qty = self.net_weight
                pr_item.uom = po_item.uom
                pr_item.stock_uom = po_item.stock_uom
                pr_item.rate = po_item.rate
                pr_item.warehouse = po_item.warehouse
                pr_item.custom_purchase_order_item_ref = po_item.name
                pr_item.rejected_warehouse = ""
                # Get Lab Template
                po_item_group = frappe.db.get_value(
                    "Item", po_item.item_code, "item_group"
                )
                lab_template = frappe.db.get_value(
                    "Item Group", po_item_group, "custom_test_variable_template"
                )
                pr_item.custom_test_variable_template = lab_template

            # Map Taxes PO → PR
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
            pr.insert(ignore_permissions=True)

            frappe.msgprint(
                    f"Purchase Receipt <b>{pr.name}</b> created in Draft from Vehicle Queue"
                )

        elif any(d.purchase_order for d in self.item):

            pr = frappe.new_doc("Purchase Receipt")
            pr.supplier = self.supplier
            pr.company = self.company
            pr.custom_vehicle_queue = self.name
            pr.custom_token_number = self.token_number
            pr.cost_center = self.cost_center
            pr.branch = self.branch
            if self.date:
                pr.posting_date = getdate(self.date)

            if self.out_time:
                pr.posting_time = get_time(self.out_time)

            # Enable manual posting time if backdated
            if self.date and getdate(self.date) < getdate(nowdate()):
                pr.set_posting_time = 1
            pr.vehicle_no = self.vehicle_no
            pr.set_warehouse = self.warehouse
            pr.custom_item_group = self.product

            # -------------------------------------------------
            # LOOP VEHICLE QUEUE ITEM TABLE
            # -------------------------------------------------
            for vq_item in self.item:

                if not vq_item.purchase_order:
                    continue

                po = frappe.get_doc("Purchase Order", vq_item.purchase_order)

                # Match PO item
                po_item = next(
                    (i for i in po.items if i.item_code == vq_item.item),
                    None
                )

                if not po_item:
                    continue

                pr_item = pr.append("items", {})

                pr_item.item_code = vq_item.item
                pr_item.qty = self.net_weight   # ✅ direct qty, no allocation
                pr_item.rate = vq_item.rate or 0
                pr_item.warehouse = self.warehouse
                # pr_item.qty = vq_item.net_weight
                pr_item.custom_purchase_order_item_ref = po_item.name
                pr_item.rejected_warehouse = ""
                
                if vq_item.purchase_order:
                    pr_item.custom_purchase_order_ref = vq_item.purchase_order

                # Fetch Lab Template
                item_group = frappe.db.get_value(
                    "Item", vq_item.item, "item_group"
                )

                lab_template = frappe.db.get_value(
                    "Item Group", item_group, "custom_test_variable_template"
                )

                pr_item.custom_test_variable_template = lab_template
            pr.set_missing_values()
            pr.run_method("calculate_taxes_and_totals")
                # Copy Taxes from PO (only once ideally, but keeping your logic)
                # if vq_item.purchase_order:
                #     for po_tax in po.taxes:
                #         pr_tax = pr.append("taxes", {})
                #         pr_tax.charge_type = po_tax.charge_type
                #         pr_tax.account_head = po_tax.account_head
                #         pr_tax.description = po_tax.description
                #         pr_tax.rate = po_tax.rate
                #         pr_tax.tax_amount = po_tax.tax_amount
                #         pr_tax.total = po_tax.total
                #         pr_tax.tax_amount_after_discount_amount = po_tax.tax_amount_after_discount_amount
                #         pr_tax.base_tax_amount = po_tax.base_tax_amount
                #         pr_tax.base_total = po_tax.base_total
                #         pr_tax.cost_center = po_tax.cost_center
                #         pr_tax.included_in_print_rate = po_tax.included_in_print_rate

            # ---------------------------------------------------------
            # Insert PR
            # ---------------------------------------------------------
            pr.insert(ignore_permissions=True)

            frappe.msgprint(
                f"Purchase Receipt <b>{pr.name}</b> created in Draft from Vehicle Queue"
            )
        else:
            pr = frappe.new_doc("Purchase Receipt")
            pr.supplier = self.supplier
            pr.company = self.company
            pr.custom_vehicle_queue = self.name
            pr.custom_token_number = self.token_number
            pr.cost_center = self.cost_center
            pr.branch = self.branch
            if self.date:
                pr.posting_date = getdate(self.date)
            if self.out_time:
                pr.posting_time = get_time(self.out_time)

            # Enable manual posting time if backdated
            if self.date and getdate(self.date) < getdate(nowdate()):
                pr.set_posting_time = 1
            pr.vehicle_no = self.vehicle_no
            pr.set_warehouse = self.warehouse
            pr.custom_item_group = self.product

            for vq_item in self.item:

                pr_item = pr.append("items", {})
                pr_item.item_code = vq_item.item
                pr_item.qty = self.net_weight   # ✅ direct qty, no allocation
                pr_item.rate = vq_item.rate  # MUST exist
                pr_item.uom = frappe.db.get_value("Item", vq_item.item, "stock_uom")
                pr_item.stock_uom = pr_item.uom
                pr_item.warehouse = self.warehouse
                item_group = frappe.db.get_value(
                    "Item", vq_item.item, "item_group"
                )

                lab_template = frappe.db.get_value(
                    "Item Group", item_group, "custom_test_variable_template"
                )

                pr_item.custom_test_variable_template = lab_template

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
            #  DELETE LINKED LABORATORY REGISTERS FIRST
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
            #  DELETE PURCHASE RECEIPT
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
    pv.company = doc.company
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
    pv.purchase_bill_no = doc.purchase_bill_no
    # Product Name = Item Group
    pv.product_name = item_group
    pv.weighment_location = doc.weighment_location
    pv.vehicle_queue_created_by = doc.owner
    pv.narration = doc.narration

    # ----------------------------
    # Child table mapping (ALL ITEMS)
    # ----------------------------
    for row in doc.item:
        pv.append("raw_materials", {
            "fish_variety": row.item,        # Vehicle Queue Item
            "warehouse": doc.warehouse,
            "no_of_boxes": row.no_of_bags,
            "count":row.count,
            "gross_weight": doc.gross_weight,
            "tare_weight": doc.tare_weight,
            "net_weight": doc.net_weight,
            "mixed_item":row.mixed_item
        })

    pv.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.msgprint(
        f"Purchase Voucher Draft Created : <b>{pv.name}</b>",
        alert=True
    )


# @frappe.whitelist()
# def make_vehicle_queue_from_po(source_name, target_doc=None, args=None):
#   if args is None:
#     args = {}
#   if isinstance(args, str):
#     args = json.loads(args)

#   def update_item(source, target, source_parent):
#     target.item = source.item_code

#   def select_item(d):
#     filtered_items = args.get("filtered_children", [])
#     return d.name in filtered_items if filtered_items else True

#   doc = get_mapped_doc(
#     "Purchase Order",
#     source_name,
#     {
#       "Purchase Order": {
#         "doctype": "Vehicle Queue",
#         "validation": {"docstatus": ["=", 1]},
#       },
#       "Purchase Order Item": {
#         "doctype": "Vehicle Queue Item",
#         "postprocess": update_item,
#         "condition": lambda d: select_item(d),
#       },
#     },
#     target_doc,
#   )

#   return doc

@frappe.whitelist()
def get_pending_po_items(supplier, company):

    po_items = frappe.db.sql("""
        SELECT
            po.name AS purchase_order,
            po.transaction_date,
            po.supplier,

            poi.name AS purchase_order_item,   -- 🔥 IMPORTANT (use later)
            poi.item_code,
            poi.item_name,

            poi.qty AS ordered_qty,
            poi.received_qty,                  -- ✅ DIRECT VALUE

            (poi.qty - poi.received_qty) AS pending_qty,   -- ✅ CORRECT

            item.custom_default_receiving_uom,

            -- UOM Conversion
            uomc.conversion_factor,

            poi.rate

        FROM `tabPurchase Order` po

        INNER JOIN `tabPurchase Order Item` poi
            ON poi.parent = po.name

        LEFT JOIN `tabItem` item
            ON poi.item_code = item.item_code

        LEFT JOIN `tabUOM Conversion Detail` uomc
            ON uomc.parent = item.name
            AND uomc.uom = item.custom_default_receiving_uom

        WHERE
            po.docstatus = 1
            AND po.status NOT IN ('Closed', 'On Hold')
            AND po.supplier = %s
            AND po.company = %s

            -- ✅ Use item-level pending
            AND (poi.qty - poi.received_qty) > 0

        ORDER BY po.transaction_date, po.name

    """, (supplier, company), as_dict=True)

    return po_items

import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.accounts.utils import get_fiscal_year


def validate_supplier_invoice_number(self):

    if self.supplier_invoice_number:
        fiscal_year = get_fiscal_year(self.posting_date, company=self.company, as_dict=True)

        vq = frappe.db.sql("""
            SELECT name
            FROM `tabVehicle Queue`
            WHERE supplier_invoice_number = %(supplier_invoice_number)s
            AND supplier = %(supplier)s
            AND name != %(name)s
            AND docstatus < 2
            AND posting_date BETWEEN %(year_start_date)s AND %(year_end_date)s
        """, {
            "supplier_invoice_number": self.supplier_invoice_number,
            "supplier": self.supplier,
            "name": self.name,
            "year_start_date": fiscal_year.year_start_date,
            "year_end_date": fiscal_year.year_end_date
        })

        if vq:
            vq_name = vq[0][0]

            frappe.throw(
                _("Supplier Invoice Number already exists in Vehicle Queue {0}").format(
                    frappe.utils.get_link_to_form("Vehicle Queue", vq_name)
                )
            )

@frappe.whitelist()
def get_po_item_details(purchase_order, item, net_weight=0, product=None):

    # 🚫 Skip Raw Fish
    if product == "Raw Fish":
        return {}

    if not purchase_order or not item:
        return {}

    # Fetch PO Item directly (optimized)
    po_item = frappe.db.get_value(
        "Purchase Order Item",
        {
            "parent": purchase_order,
            "item_code": item
        },
        ["qty", "received_qty"],
        as_dict=1
    )

    if not po_item:
        frappe.throw("Item not found in selected Purchase Order")

    po_qty = po_item.qty or 0
    received_qty = po_item.received_qty or 0
    net_weight = float(net_weight or 0)
    print(received_qty,net_weight,"received and net weight values")

    balance_qty = po_qty - received_qty - net_weight

    return {
        "po_qty": po_qty,
        "received_qty": received_qty,
        "po_balance_qty": balance_qty
    }