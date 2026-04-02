import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils import nowdate 
from cit_exim.cit_exim.doc_events.sales_invoice import set_contract_term_details
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice



        
  
# import frappe
# from frappe.model.document import Document
# from frappe.utils import flt
import math

# # ----------------------------------------------------------------------
# # DYNAMIC FIELD MAPPING & HELPERS
# # ----------------------------------------------------------------------

# def get_shared_fields():
#     parent_meta = frappe.get_meta("Consolidated Sales Invoice")
#     child_meta = frappe.get_meta("Sales Invoice")

#     parent_fields = {f.fieldname for f in parent_meta.fields if f.fieldtype != "Table"}
#     child_fields = {f.fieldname for f in child_meta.fields if f.fieldtype != "Table"}

#     exclude = {
#         "name", "owner", "creation", "modified", "modified_by",
#         "idx", "amended_from", "naming_series",
#         "custom_consolidated_invoice_reference", "workflow_state"
#     }

#     shared = list((parent_fields & child_fields) - exclude)
    
#     critical_fields = ["payment_terms_template", "payment_terms", "due_date", "customer"]
#     for f in critical_fields:
#         if parent_meta.has_field(f) and child_meta.has_field(f) and f not in shared:
#             shared.append(f)

#     return shared

# def get_shared_item_fields():
#     parent_item_meta = frappe.get_meta("Consolidated Sales Invoice Item")
#     child_item_meta = frappe.get_meta("Sales Invoice Item")

#     parent_f = {f.fieldname for f in parent_item_meta.fields}
#     child_f = {f.fieldname for f in child_item_meta.fields}

#     exclude = {
#         "name", "parent", "parenttype", "parentfield",
#         "qty", "amount", "base_amount", "stock_qty",
#         "serial_and_batch_bundle", "item_group"
#     }

#     return list((parent_f & child_f) - exclude)

# def sync_custom_child_tables(source_doc, target_doc):
#     tables_to_sync = [
#         "sales_invoice_contract_term_check",
#         "sales_invoice_export_document_item",
#         "payment_schedule",
#         "custom_quality_and_specification"
#     ]

#     for table_field in tables_to_sync:
#         if not source_doc.meta.has_field(table_field) or not target_doc.meta.has_field(table_field):
#             continue

#         target_doc.set(table_field, [])
#         for row in source_doc.get(table_field) or []:
#             data = row.as_dict()
#             for k in ("name", "parent", "parenttype", "parentfield", "creation", "modified"):
#                 data.pop(k, None)
#             target_doc.append(table_field, data)

# ----------------------------------------------------------------------
# MAIN DOCTYPE CLASS
# ----------------------------------------------------------------------
class ConsolidatedSalesInvoice(Document):
        
    def validate(self):
        self.run_core_calculations()


        if not self.items:
            return
        print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
        lot_list = []

        for item in self.items:
            if not item.serial_and_batch_bundle:
                continue

            bundle = frappe.get_doc(
                "Serial and Batch Bundle",
                item.serial_and_batch_bundle
            )

            # conversion_factor = frappe.db.get_value(
            #     "UOM Conversion Detail",
            #     {
            #         "parent": item.item_code,
            #         "uom": item.export_uom
            #     },
            #     "conversion_factor"
            # )
            conversion_factor = item.kg_per_package

            if not conversion_factor:
                frappe.throw(
                    f"Export Package is not defined for Item {item.item_code}"
                )

            for entry in bundle.entries:
                if not entry.batch_no:
                    continue

                # IMPORTANT: entry.qty is negative for outward stock
                batch_qty = abs(flt(entry.qty))  # normalize

                lot_list.append({
                    "lot_no": entry.batch_no,
                    "batch_qty": batch_qty,
                    "conversion_factor": conversion_factor
                })
        if len(self.batches_for_loading) == 0:
            for lot in lot_list:
                no_of_packages = flt(lot["batch_qty"]) / flt(lot["conversion_factor"])
                self.append("batches_for_loading",{
                    "batch_no": lot["lot_no"],
                    "batch_qty": lot["batch_qty"],
                    "no_of_packages": int(no_of_packages),
            })

        existing_lots = {row.lot_no for row in self.container_detail}

        for lot in lot_list:
            if lot["lot_no"] in existing_lots:
                continue

            no_of_packages = flt(lot["batch_qty"]) / flt(lot["conversion_factor"])

            # self.append("container_detail", {
            #     "lot_no": lot["lot_no"],
            #     "no_of_packages": int(no_of_packages)
            # })
    def before_save(self):
        self.run_core_calculations()
    
    def run_core_calculations(self):



        si = frappe.new_doc("Sales Invoice")

        # Required fields
        si.company = self.company
        si.customer = self.customer
        si.currency = self.currency
        si.conversion_rate = self.conversion_rate or 1
        si.selling_price_list = "Standard Selling"

        si.set("items", [])

        #  Initialize total_net_weight
        total_net_weight = 0

        for d in self.items:

            # Calculate amount
            d.amount = (d.qty or 0) * (d.rate or 0)

            # Get conversion factor (default = 1 if not set)
            conversion_factor = d.conversion_factor or 1

            # Calculate stock_qty
            d.stock_qty = (d.qty or 0) * conversion_factor

            #  Add to total_net_weight
            total_net_weight += d.stock_qty

            si.append("items", {
                "item_code": d.item_code,
                "qty": d.qty,
                "rate": d.rate,
                "amount": d.amount,
                "uom": d.uom,
                "conversion_factor": conversion_factor,
                "stock_qty": d.stock_qty
            })

        # Core logic
        si.set_missing_values()
        si.calculate_taxes_and_totals()

        # Map back totals
        self.total_qty = si.total_qty
        self.total = si.total
        self.net_total = si.net_total
        self.grand_total = si.grand_total
        self.rounded_total = si.rounded_total

        self.base_total = si.base_total
        self.base_net_total = si.base_net_total
        self.base_grand_total = si.base_grand_total

        #  Set total_net_weight
        self.total_net_weight = total_net_weight

    def on_update_after_submit(self):
        print("date...........")
        """
        Runs when a submitted Consolidated Sales Invoice is updated
        (e.g., workflow state change)
        """
        target_state = "Document Submitted & Awaiting Payments"

        # Check workflow state and ensure date is not already set
        if self.workflow_state == target_state and not self.custom_submission_date:
            
            # Update field bypassing validation
            self.db_set('custom_submission_date', nowdate())

            # Add comment (optional)
            self.add_comment(
                "Info",
                text=f"Captured submission date as state changed to {target_state}"
            )
        if frappe.flags.in_consolidated_reverse_sync:
            return

        frappe.flags.in_consolidated_reverse_sync = True

        try:
            consolidated_name = self.name

            # ---------------------------------------
            # PREPARE FORM UPDATES
            # ---------------------------------------
            form_updates = {
                "workflow_state": self.workflow_state,
            }

            fields = [
                "bl_no","bl_date","vessel_no","custom_shipped_on_board_date","port_address","branch",
                "total_fob_value","freight","insurance","freight_calculated","total_duty_drawback",
                "total_meis","duty_drawback_jv","meis_jv","custom_lab_test_remarks","shipping_terms",
                "port_of_loading","port_of_discharge","pre_carriage_by","custom_dclc","custom_dc_no",
                "custom_lc_no","custom_loading_point","final_destination","custom_carriage_by",
                "custom_dhl","custom_dc_date","custom_lc_date","container_size","country_of_origin",
                "country_of_destination","movement","custom_submission_date",
                "custom_bl_issued_remarks","contract_and_lc","custom_document_checked","set_warehouse"
            ]

            for f in fields:
                val = self.get(f)
                if val is not None:
                    form_updates[f] = val

            # ---------------------------------------
            # GET LINKED SALES INVOICES
            # ---------------------------------------
            invoice_names = frappe.get_all(
                "Sales Invoice",
                filters={
                    "custom_consolidated_invoice_reference": consolidated_name
                },
                pluck="name"
            )

            print("Updating invoices:", invoice_names)

            if not invoice_names:
                return

            invoices = [frappe.get_doc("Sales Invoice", inv) for inv in invoice_names]

            # ---------------------------------------
            # UPDATE SALES INVOICES
            # ---------------------------------------
            for inv in invoices:

                inv.reload()

                # ---------------------------------------
                # APPLY FORM FIELD UPDATES
                # ---------------------------------------
                for key, value in form_updates.items():
                    inv.set(key, value)

                if "contract_and_lc" in form_updates:
                    set_contract_term_details(inv)

                # ---------------------------------------
                # ITEM TABLE SYNC (IDX BASED)
                # ---------------------------------------
                for item in self.items:
                    for row in inv.items:
                        if row.idx == item.idx:
                            row.set("duty_drawback_rate", item.duty_drawback_rate)
                            row.set("capped_rate", item.capped_rate)
                            row.set("meis_rate", item.meis_rate)
                            row.set("custom_rodtep_capped_rate", item.custom_rodtep_capped_rate)
                            row.set("freight", item.freight)
                            row.set("insurance", item.insurance)
                            row.set("duty_drawback_amount", item.duty_drawback_amount)
                            row.set("capped_amount", item.capped_amount)
                            row.set("meis_value", item.meis_value)
                            row.set("custom_rodtep_capped_amount", item.custom_rodtep_capped_amount)
                            row.set("fob_value", item.fob_value)
                            row.set("description", item.description)

                # ---------------------------------------
                # CONTAINER DETAILS SYNC
                # ---------------------------------------
                for container in self.container_detail:
                    for row in inv.container_detail:
                        if row.idx == container.idx:
                            row.set("container_no", container.container_no)
                            row.set("size", container.size)
                            row.set("shipping_line_seal_no", container.shipping_line_seal_no)
                            row.set("nt_wt_kgs", container.nt_wt_kgs)
                            row.set("gr_wt_kgs", container.gr_wt_kgs)
                            row.set("no_of_packages", container.no_of_packages)
                            row.set("manufacturing_date", container.manufacturing_date)
                            row.set("batch_name", container.batch_name)

                # ---------------------------------------
                # CONTRACT TERMS SYNC
                # ---------------------------------------
                for ct in self.sales_invoice_contract_term_check:
                    for row in inv.sales_invoice_contract_term_check:
                        if row.idx == ct.idx:
                            row.set("contract_term", ct.contract_term)
                            row.set("document_check", ct.document_check)
                            row.set("checked", ct.checked)

                # ---------------------------------------
                # EXPORT DOCUMENT SYNC
                # ---------------------------------------
                for ed in self.sales_invoice_export_document_item:
                    for row in inv.sales_invoice_export_document_item:
                        if row.idx == ed.idx:
                            row.set("contract_term", ed.contract_term)
                            row.set("export_document", ed.export_document)
                            row.set("number", ed.number)
                            row.set("checked", ed.checked)

                # ---------------------------------------
                # MARK CHILD TABLES DIRTY
                # ---------------------------------------
                inv.set("items", inv.items)
                inv.set("container_detail", inv.container_detail)
                inv.set("sales_invoice_contract_term_check", inv.sales_invoice_contract_term_check)
                inv.set("sales_invoice_export_document_item", inv.sales_invoice_export_document_item)

                # ---------------------------------------
                # ALLOW UPDATE AFTER SUBMIT
                # ---------------------------------------
                inv.flags.ignore_validate_update_after_submit = True

                # ---------------------------------------
                # SAVE
                # ---------------------------------------
                inv.save(
                    ignore_permissions=True,
                    ignore_version=True
                )

            # ---------------------------------------
            # FORCE DB COMMIT
            # ---------------------------------------
            frappe.db.commit()

        finally:
            frappe.flags.in_consolidated_reverse_sync = False
    def on_submit(self):

        # Prevent recursion
        if frappe.flags.in_consolidated_submit:
            return

        frappe.flags.in_consolidated_submit = True

        try:
            # Fetch linked Sales Invoices
            invoices = frappe.get_all(
                "Sales Invoice",
                filters={
                    "custom_consolidated_invoice_reference": self.name
                },
                pluck="name"
            )

            for inv in invoices:

                invoice_doc = frappe.get_doc("Sales Invoice", inv)

                # Submit only Draft & non-return invoices
                if invoice_doc.docstatus == 0 and not invoice_doc.is_return:
                    invoice_doc.submit()

        finally:
            frappe.flags.in_consolidated_submit = False

#     def sync_to_sales_invoices(self):
#         if frappe.flags.in_consolidated_sync:
#             return

#         frappe.flags.in_consolidated_sync = True
#         try:
#             sales_invoices = frappe.get_all(
#                 "Sales Invoice",
#                 filters={"custom_consolidated_invoice_reference": self.name},
#                 fields=["name", "docstatus"]
#             )

#             shared_fields = get_shared_fields()
#             shared_item_fields = get_shared_item_fields()

#             for si in sales_invoices:
#                 si_doc = frappe.get_doc("Sales Invoice", si.name)
                
#                 for f in shared_fields:
#                     si_doc.set(f, self.get(f))

#                 if self.workflow_state:
#                     si_doc.workflow_state = self.workflow_state

#                 sync_custom_child_tables(self, si_doc)

#                 for p_item in self.items:
#                     for c_item in si_doc.items:
#                         if c_item.item_code == p_item.item_code:
#                             for f in shared_item_fields:
#                                 c_item.set(f, p_item.get(f))

#                 si_doc.flags.ignore_permissions = True
#                 si_doc.flags.ignore_workflow = True
                
#                 if si_doc.docstatus == 1:
#                     si_doc.flags.ignore_validate_update_after_submit = True

#                 si_doc.save(ignore_permissions=True)
#         finally:
#             frappe.flags.in_consolidated_sync = False

#     def on_update(self):
#         self.sync_to_sales_invoices()

#     def on_submit(self):
#         self.sync_to_sales_invoices()

# # ----------------------------------------------------------------------
# # GLOBAL HOOK: SYNC FROM CHILD TO PARENT (Updated Completion Logic)
# # ----------------------------------------------------------------------
# def sync_status_from_sales_invoice(doc, method=None):
#     if frappe.flags.in_consolidated_sync or doc.docstatus == 2:
#         return

#     parent_name = doc.custom_consolidated_invoice_reference
#     if not parent_name:
#         return

#     frappe.flags.in_consolidated_sync = True
#     try:
#         parent_doc = frappe.get_doc("Consolidated Sales Invoice", parent_name)

#         shared_fields = get_shared_fields()
#         shared_item_fields = get_shared_item_fields()
        
#         for f in shared_fields:
#             parent_doc.set(f, doc.get(f))

#         # --- LOGIC TO CHECK ALL CHILD INVOICES ---
#         if doc.workflow_state == "Completed shipment":
#             # Fetch status of all siblings
#             siblings = frappe.get_all(
#                 "Sales Invoice",
#                 filters={"custom_consolidated_invoice_reference": parent_name},
#                 fields=["workflow_state"]
#             )
            
#             # Check if all siblings are now in the 'Completed shipment' state
#             all_done = all(s.workflow_state == "Completed shipment" for s in siblings)
            
#             if all_done:
#                 parent_doc.workflow_state = "Completed shipment"
#             else:
#                 parent_doc.workflow_state = "Document Submitted & Awaiting Payments"
#         else:
#             # Maintain standard sync for other workflow states
#             if doc.workflow_state:
#                 parent_doc.workflow_state = doc.workflow_state
#         # --- END LOGIC ---

#         sync_custom_child_tables(doc, parent_doc)
        
#         for c_item in doc.items:
#             for p_item in parent_doc.items:
#                 if p_item.item_code == c_item.item_code:
#                     for f in shared_item_fields:
#                         p_item.set(f, c_item.get(f))

#         parent_doc.flags.ignore_workflow = True
        
#         if parent_doc.docstatus == 1:
#             parent_doc.flags.ignore_validate_update_after_submit = True

#         parent_doc.save(ignore_permissions=True)

#         # Propagate changes to other sibling invoices
#         frappe.flags.in_consolidated_sync = False
#         parent_doc.sync_to_sales_invoices()
#         frappe.flags.in_consolidated_sync = True

#     finally:
#         frappe.flags.in_consolidated_sync = False





# ----------------------------------------------------------------------
# SPLIT LOGIC
# ----------------------------------------------------------------------
# @frappe.whitelist()
# def split_consolidated_invoice(source_name, split_count):
#     split_count = int(split_count)
#     source_doc = frappe.get_doc("Consolidated Sales Invoice", source_name)
#     container_rows = source_doc.get("container_detail") or []
#     rows_per_split = math.ceil(len(container_rows) / split_count) if container_rows else 0

#     new_invoices = []
#     frappe.flags.in_consolidated_sync = True
    
#     try:
#         shared_fields = get_shared_fields()
#         shared_item_fields = get_shared_item_fields()

#         for i in range(split_count):
#             si = frappe.new_doc("Sales Invoice")
#             for f in shared_fields:
#                 si.set(f, source_doc.get(f))

#             si.custom_consolidated_invoice_reference = source_name
#             sync_custom_child_tables(source_doc, si)

#             for item in source_doc.items:
#                 child_item = si.append("items", {
#                     "item_code": item.item_code,
#                     "qty": flt(item.qty / split_count, 6),
#                     "rate": item.rate,
#                     "uom": item.uom,
#                     "warehouse": item.warehouse,
#                     "income_account": item.income_account,
#                     "cost_center": item.cost_center,
#                     "sales_order": item.sales_order,
#                     "so_detail": item.so_detail
#                 })
#                 for f in shared_item_fields:
#                     child_item.set(f, item.get(f))

#             start, end = i * rows_per_split, (i + 1) * rows_per_split
#             for row in container_rows[start:end]:
#                 data = row.as_dict()
#                 for k in ("name", "parent", "parenttype", "parentfield", "creation", "modified"):
#                     data.pop(k, None)
#                 si.append("container_detail", data)

#             si.flags.ignore_permissions = True
#             si.flags.ignore_workflow = True
#             si.insert()

            # if source_doc.workflow_state:
            #     frappe.db.set_value("Sales Invoice", si.name, "workflow_state", source_doc.workflow_state, update_modified=False)
            
#             new_invoices.append(si.name)
#     finally:
#         frappe.flags.in_consolidated_sync = False

#     return new_invoices
    
    



# def before_insert(doc, method=None):
#     """
#     Copy selected producers from Sales Order
#     into Consolidated Sales Invoice
#     """
#     if not doc.get("items"):
#         return

#     if len(doc.items) == 0:
#         return

#     so_name = doc.items[0].sales_order
#     if not so_name:
#         return

#     copy_selected_producers(doc, so_name)


# def copy_selected_producers(doc, sales_order):
#     so = frappe.get_doc("Sales Order", sales_order)

#     # Clear existing mapped producers
#     doc.custom_producer_table = []

#     if not so.get("custom_producer_table"):
#         return

#     for row in so.custom_producer_table:
#         if row.selected:
#             child = doc.append("custom_producer_table", {})
#             child.producer = row.producer
#             child.address = row.address
#             child.selected = row.selected

import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def get_serial_batch_bundle(bundle_name):
    if not bundle_name:
        return []

    bundle = frappe.get_doc("Serial and Batch Bundle", bundle_name)

    return [
        {
            "batch_no": row.batch_no,
            "qty": abs(flt(row.qty))
        }
        for row in bundle.entries if row.batch_no
    ]

@frappe.whitelist()
def split_consolidated_invoice(source_name, split_count, split_data=None):

    split_count = int(split_count)
    if split_data:
        split_data = frappe.parse_json(split_data)


    split_count = int(split_count)

    if split_count <= 0:
        frappe.throw("Split count must be greater than 0")

    source_doc = frappe.get_doc("Consolidated Sales Invoice", source_name)
    bundle_batch_qty = {}

    for itm in source_doc.items:

        if not itm.serial_and_batch_bundle:
            continue

        bundle = frappe.get_doc("Serial and Batch Bundle", itm.serial_and_batch_bundle)

        for entry in bundle.entries:

            batch = entry.batch_no
            qty = abs(flt(entry.qty))

            if batch not in bundle_batch_qty:
                bundle_batch_qty[batch] = 0

            bundle_batch_qty[batch] += qty

    print(bundle_batch_qty)
    selected_batch_qty = {}

    for entry in split_data:

        batch = entry.get("batch")
        qty = flt(entry.get("qty"))

        if not batch:
            continue

        # if batch not in bundle_batch_qty:
        #     frappe.throw(
        #         f"Batch <b>{batch}</b> was not used in the Consolidated Invoice."
        #     )

        if batch not in selected_batch_qty:
            selected_batch_qty[batch] = 0

        selected_batch_qty[batch] += qty


    for batch, qty in selected_batch_qty.items():

        allowed_qty = bundle_batch_qty.get(batch, 0)

        # if qty > allowed_qty:
        #     frappe.throw(
        #         f"Selected quantity <b>{qty}</b> for Batch <b>{batch}</b> exceeds available quantity <b>{allowed_qty}</b> in the Consolidated Invoice."
        #     )


    if len(source_doc.items) != 1:
        frappe.throw("Consolidated Sales Invoice must contain exactly one item")

    item = source_doc.items[0]

    total_qty = item.qty
    total_rate = item.rate
    total_amount = item.amount

    qty_per_invoice = total_qty / split_count
    rate_per_invoice = total_rate
    amount_per_invoice = total_amount / split_count

    remainder_qty = total_qty % split_count
    remainder_amount = total_amount % split_count

    created_invoices = []
    bundle_dict = {
    itm.item_code: {
        "qty": itm.qty,
        "bundle": itm.serial_and_batch_bundle
    }
    for itm in source_doc.items if itm.serial_and_batch_bundle
    }

    # -----------------------------
    # Disable workflow sync
    # -----------------------------
    frappe.flags.in_consolidated_sync = True

    try:

        for i in range(split_count):

            si = frappe.new_doc("Sales Invoice")

            container_rows = source_doc.get("container_detail") or []
            rows_per_split = math.ceil(len(container_rows) / split_count) if container_rows else 0

            # Map fields
            si.customer = source_doc.customer
            si.company = source_doc.company
            si.posting_date = source_doc.posting_date
            si.due_date = source_doc.due_date
            si.currency = source_doc.currency
            si.conversion_rate = source_doc.conversion_rate
            si.selling_price_list = source_doc.selling_price_list
            si.custom_consolidated_invoice_reference = source_doc.name
            si.branch = source_doc.branch
            si.set_warehouse = source_doc.set_warehouse

            si.custom_product = source_doc.custom_product
            si.custom_quality_and_specification = source_doc.custom_quality_and_specification
            si.payment_terms_template = source_doc.payment_terms_template
            si.payment_schedule = source_doc.payment_schedule
            si.custom_packing_template = source_doc.custom_packing_template
            si.custom_packing_detailsfor_sales_invoice = source_doc.custom_packing_detailsfor_sales_invoice
            si.tc_name = source_doc.tc_name
            si.terms = source_doc.terms
            si.shipping_terms = source_doc.shipping_terms
            si.port_of_loading = source_doc.port_of_loading
            si.port_of_discharge = source_doc.port_of_discharge
            si.pre_carriage_by = source_doc.pre_carriage_by
            si.custom_carriage_by = source_doc.custom_carriage_by
            si.custom_loading_point = source_doc.custom_loading_point
            si.container_size = source_doc.container_size
            si.country_of_origin = source_doc.country_of_origin
            si.country_of_destination = source_doc.country_of_destination
            si.custom_lab_test_remarks = source_doc.custom_lab_test_remarks
            # si.vessel_no = source_doc.vessel_no
            si.final_destination = source_doc.final_destination
            si.port_address = source_doc.port_address



            # Add item
            row = si.append("items", {})
            row.item_code = item.item_code
            row.item_name = item.item_name
            row.description = item.description
            row.uom = item.uom
            row.stock_uom = item.stock_uom
            row.conversion_factor = item.conversion_factor
            row.warehouse = item.warehouse
            row.sales_order = item.sales_order
            row.custom_export_uom = item.export_uom

            if i < remainder_qty:
                row.qty = qty_per_invoice + 1
            else:
                row.qty = qty_per_invoice

            row.rate = rate_per_invoice
            row.amount = row.qty * row.rate
            
            # Container split
            if container_rows:
                start = i * rows_per_split
                end = (i + 1) * rows_per_split

                for r in container_rows[start:end]:
                    data = r.as_dict()

                    for k in ("name", "parent", "parenttype", "parentfield", "creation", "modified"):
                        data.pop(k, None)

                    si.append("container_detail", data)

            # Insert invoice
            si.insert(ignore_permissions=True)

            # Copy workflow state
            if source_doc.workflow_state:
                frappe.db.set_value(
                    "Sales Invoice",
                    si.name,
                    {
                        "workflow_state": source_doc.workflow_state,
                        "docstatus": source_doc.docstatus
                    },
                    update_modified=False
                )
            si_doc = frappe.get_doc("Sales Invoice", si.name)

            for row in si_doc.items:

                print("Processing Item:", row.item_code)

                if not split_data:
                    print("No split data received")
                    continue

                new_bundle = frappe.new_doc("Serial and Batch Bundle")
                new_bundle.company = si_doc.company
                new_bundle.type_of_transaction = "Outward"
                new_bundle.voucher_type = "Sales Invoice"
                new_bundle.voucher_no = si_doc.name
                new_bundle.voucher_detail_no = row.name
                new_bundle.item_code = row.item_code
                new_bundle.warehouse = row.warehouse

                for batch_entry in split_data:

                    if not batch_entry.get("batch"):
                        continue

                    if flt(batch_entry.get("qty")) <= 0:
                        continue

                    if batch_entry.get("invoice") != (i + 1):
                        continue

                    existing_batches = [e.batch_no for e in new_bundle.entries]

                    if batch_entry.get("batch") not in existing_batches:
                        new_bundle.append("entries", {
                            "batch_no": batch_entry.get("batch"),
                            "qty": -flt(batch_entry.get("qty")),
                            "warehouse": row.warehouse
                        })

                if new_bundle.entries:
                    new_bundle.posting_date = si_doc.posting_date
                    new_bundle.posting_time = si_doc.posting_time or frappe.utils.nowtime()
                    new_bundle.has_batch_no = 1
                    new_bundle.has_serial_no = 0
                    new_bundle.insert(ignore_permissions=True)


                # attach bundle to item row
                row.serial_and_batch_bundle = new_bundle.name
            
            # save invoice after attaching bundle
            si_doc.save(ignore_permissions=True)
            

            created_invoices.append(si.name)

        frappe.db.commit()

    finally:
        # -----------------------------
        # Enable workflow sync again
        # -----------------------------
        frappe.flags.in_consolidated_sync = False

    return created_invoices

import frappe

@frappe.whitelist()
def get_package_type_by_item(doctype, txt, searchfield, start, page_len, filters):

    filters = filters or {}   # ✅ prevent None error

    item_code = filters.get("item_code")

    if not item_code:
        return []

    item_group = frappe.db.get_value("Item", item_code, "item_group")

    if not item_group:
        return []

    return frappe.db.sql("""
        SELECT name
        FROM `tabPackage Type`
        WHERE item_group = %s
        AND name LIKE %s
        LIMIT %s, %s
    """, (item_group, f"%{txt}%", start, page_len))

@frappe.whitelist()
def contract_and_lc_filter(doctype, txt, searchfield, start, page_len, filters):
    
    so_list = filters.get("sales_orders")

    if not so_list:
        return []

    return frappe.db.sql("""
        SELECT DISTINCT ct.name
        FROM `tabContract Term` AS ct
        JOIN `tabContract Term Order` AS cto 
            ON cto.parent = ct.name
        WHERE cto.sales_order IN ({})
    """.format(", ".join(["%s"] * len(so_list))), tuple(so_list))