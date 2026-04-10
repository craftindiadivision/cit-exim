import frappe
from frappe import _
from frappe.utils import flt

from frappe.model.document import Document
import json
from frappe.utils import today
import calendar
from datetime import date
from frappe.utils import getdate
from frappe.utils import nowdate



def before_save(self, method):
	calculate_total(self)
	duty_calculation(self)
	meis_calculation(self)
	



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
    # --------------------------------------------------
    # BILLING ADDRESS VALIDATION (NON-CONSIGNEE ONLY)
    # --------------------------------------------------
    current_address = None
    is_current_consignee = False

    # -----------------------------------
    # 1. Check current address (if exists)
    # -----------------------------------
    if doc.customer_address:
        current_address = frappe.get_doc("Address", doc.customer_address)

        for link in current_address.links:
            if (
                link.link_doctype == "Customer" and
                link.link_name == doc.customer and
                getattr(link, "custom_is_consignee", 0)
            ):
                is_current_consignee = True
                break

    # -----------------------------------
    # 2. If current is VALID billing → keep
    # -----------------------------------
    if doc.customer_address and not is_current_consignee:
        return

    # -----------------------------------
    # 3. Find NON-CONSIGNEE (billing) address
    # -----------------------------------
    address_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": doc.customer,
            "parenttype": "Address"
        },
        fields=["parent"]
    )

    correct_address = None

    for row in address_links:
        addr = frappe.get_doc("Address", row.parent)

        for link in addr.links:
            if (
                link.link_doctype == "Customer" and
                link.link_name == doc.customer and
                not getattr(link, "custom_is_consignee", 0)
            ):
                correct_address = addr
                break

        if correct_address:
            break

    # -----------------------------------
    # 4. Replace consignee → billing
    # -----------------------------------
    if correct_address:
        doc.customer_address = correct_address.name
        doc.address_display = correct_address.get_display()

    else:
        frappe.throw("No valid Billing Address found (all marked as Consignee)")
    
             
    # --------------------------------------------------
    # 3. EXPORT LOGIC (LOT / CONTAINER)
    # --------------------------------------------------
    
    if not doc.items:
        return
    print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
    if doc.gst_category == "Overseas":
        lot_list = []

        for item in doc.items:
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
            #         "uom": item.custom_export_uom
            #     },
            #     "conversion_factor"
            # )
            conversion_factor = item.custom_kg_per_package

            if not conversion_factor:
                frappe.throw(
                    f"Export Package is not defined for Item {item.item_code}"
                )

            for entry in bundle.entries:
                if not entry.batch_no:
                    continue

                # IMPORTANT: entry.qty is negative for outward stock
                batch_qty = abs(flt(entry.qty))  #  normalize

                lot_list.append({
                    "lot_no": entry.batch_no,
                    "batch_qty": batch_qty,
                    "conversion_factor": conversion_factor
                })
        if len(doc.custom_batches_for_loading) == 0:
            for lot in lot_list:
                no_of_packages = flt(lot["batch_qty"]) / flt(lot["conversion_factor"])
                doc.append("custom_batches_for_loading",{
                    "batch_no": lot["lot_no"],
                    "batch_qty": lot["batch_qty"],
                    "no_of_packages": int(no_of_packages),
            })

        existing_lots = {row.lot_no for row in doc.container_detail}

        for lot in lot_list:
            if lot["lot_no"] in existing_lots:
                continue

            no_of_packages = flt(lot["batch_qty"]) / flt(lot["conversion_factor"])

            # doc.append("container_detail", {
            #     # "lot_no": lot["lot_no"],
            #     "no_of_packages": int(no_of_packages)
            # })


# def sync_workflow_from_sales_invoice(doc, method):
#     # if doc.custom_loading_point != "Mudra":
#     #      return
#     # if (doc.custom_loading_point or "").lower() != "mudra":
#     #     return

#     # If invoice is not linked to consolidated invoice → stop
#     if not doc.custom_consolidated_invoice_reference:
#         return

#     consolidated_name = doc.custom_consolidated_invoice_reference
#     new_state = doc.workflow_state
#     new_docstatus = doc.docstatus

#     # Prevent recursive execution
#     if frappe.flags.in_consolidated_sync:
#         return

#     frappe.flags.in_consolidated_sync = True

#     try:

#         # -------------------------------
#         # Prepare extra fields (Form level)
#         # -------------------------------
#         form_updates = {
#             "workflow_state": new_state,
#             # "docstatus": new_docstatus
#         }

#         if doc.bl_no:
#             form_updates["bl_no"] = doc.bl_no

#         if doc.bl_date:
#             form_updates["bl_date"] = doc.bl_date
#         if doc.vessel_no:
#              form_updates["vessel_no"] = doc.vessel_no
#         if doc.custom_shipped_on_board_date:
#              form_updates["custom_shipped_on_board_date"] = doc.custom_shipped_on_board_date
#         if doc.port_address:
#              form_updates["port_address"] = doc.port_address
#         if doc.total_fob_value:
#              form_updates["total_fob_value"] = doc.total_fob_value

#         if doc.freight:
#              form_updates["freight"] = doc.freight

#         if doc.insurance:
#              form_updates["insurance"] = doc.insurance
#         if doc.freight_calculated:
#              form_updates["freight_calculated"] = doc.freight_calculated

#         if doc.total_duty_drawback:
#              form_updates["total_duty_drawback"] = doc.total_duty_drawback
#         if doc.total_meis:
#              form_updates["total_meis"] = doc.total_meis
#         if doc.duty_drawback_jv:
#              form_updates["duty_drawback_jv"] = doc.duty_drawback_jv
#         if doc.meis_jv:
#              form_updates["meis_jv"] = doc.meis_jv
#         if doc.custom_lab_test_remarks:
#              form_updates["custom_lab_test_remarks"] = doc.custom_lab_test_remarks
#         if doc.shipping_terms:
#              form_updates["shipping_terms"] = doc.shipping_terms
#         if doc.port_of_loading:
#              form_updates["port_of_loading"] = doc.port_of_loading
#         if doc.port_of_discharge:
#              form_updates["port_of_discharge"] = doc.port_of_discharge
#         if doc.pre_carriage_by:
#              form_updates["pre_carriage_by"] = doc.pre_carriage_by
#         if doc.bl_no:
#              form_updates["bl_no"] = doc.bl_no
#         if doc.custom_dclc:
#              form_updates["custom_dclc"] = doc.custom_dclc
#         if doc.custom_dc_no:
#              form_updates["custom_dc_no"] = doc.custom_dc_no
#         if doc.custom_lc_no:
#              form_updates["custom_lc_no"] = doc.custom_lc_no
#         if doc.vessel_no:
#              form_updates["vessel_no"] = doc.vessel_no
#         if doc.custom_loading_point:
#              form_updates["custom_loading_point"] = doc.custom_loading_point
#         if doc.final_destination:
#              form_updates["final_destination"] = doc.final_destination
#         if doc.custom_carriage_by:
#              form_updates["custom_carriage_by"] = doc.custom_carriage_by
#         if doc.bl_date:
#              form_updates["bl_date"] = doc.bl_date
#         if doc.custom_dhl:
#              form_updates["custom_dhl"] = doc.custom_dhl
#         if doc.custom_dc_date:
#              form_updates["custom_dc_date"] = doc.custom_dc_date
#         if doc.custom_lc_date:
#              form_updates["custom_lc_date"] = doc.custom_lc_date
#         if doc.container_size:
#              form_updates["container_size"] = doc.container_size
#         if doc.country_of_origin:
#              form_updates["country_of_origin"] = doc.country_of_origin
#         if doc.country_of_destination:
#              form_updates["country_of_destination"] = doc.country_of_destination
#         if doc.number_of_containers:
#              form_updates["number_of_containers"] = doc.number_of_containers
#         if doc.custom_shipped_on_board_date:
#              form_updates["custom_shipped_on_board_date"] = doc.custom_shipped_on_board_date
#         if doc.movement:
#              form_updates["movement"] = doc.movement
#         if doc.custom_submission_date:
#              form_updates["custom_submission_date"] = doc.custom_submission_date
#         if doc.custom_bl_issued_remarks:
#              form_updates["custom_bl_issued_remarks"] = doc.custom_bl_issued_remarks
       
#         if doc.contract_and_lc:
#             form_updates["contract_and_lc"] = doc.contract_and_lc

#         if doc.custom_document_checked:
#             form_updates["custom_document_checked"] = doc.custom_document_checked

#         if doc.set_warehouse:
#             form_updates["set_warehouse"] = doc.set_warehouse
      

#         # -------------------------------
#         # Update Consolidated Invoice
#         # -------------------------------
#         frappe.db.set_value(
#             "Consolidated Sales Invoice",
#             consolidated_name,
#             form_updates,
#             update_modified=False
#         )


#         # -------------------------------
#         # Get all related Sales Invoices
#         # -------------------------------
#         invoices = frappe.get_all(
#             "Sales Invoice",
#             filters={
#                 "custom_consolidated_invoice_reference": consolidated_name
#             },
#             pluck="name"
#         )


#         # -------------------------------
#         # Update all split invoices
#         # -------------------------------
#         for inv in invoices:

#             # Skip current invoice
#             if inv == doc.name:
#                 continue

#             frappe.db.set_value(
#                 "Sales Invoice",
#                 inv,
#                 form_updates,
#                 update_modified=False
#             )


#         # -------------------------------
#         # Sync Item Table Fields
#         # -------------------------------
#         for item in doc.items:

#             item_updates = {}

#             if item.duty_drawback_rate:
#                 item_updates["duty_drawback_rate"] = item.duty_drawback_rate

#             if item.capped_rate:
#                 item_updates["capped_rate"] = item.capped_rate
            
#             if item.meis_rate:
#                 item_updates["meis_rate"] = item.meis_rate

#             if item.custom_rodtep_capped_rate:
#                 item_updates["custom_rodtep_capped_rate"] = item.custom_rodtep_capped_rate

#             if item.freight:
#                 item_updates["freight"] = item.freight

#             if item.insurance:
#                 item_updates["insurance"] = item.insurance

#             if item.duty_drawback_amount:
#                 item_updates["duty_drawback_amount"] = item.duty_drawback_amount

#             if item.capped_amount:
#                 item_updates["capped_amount"] = item.capped_amount

#             if item.meis_value:
#                 item_updates["meis_value"] = item.meis_value

#             if item.custom_rodtep_capped_amount:
#                 item_updates["custom_rodtep_capped_amount"] = item.custom_rodtep_capped_amount

#             if item.fob_value:
#                 item_updates["fob_value"] = item.fob_value

#             if item.description:
#                 item_updates["description"] = item.description

#             if not item_updates:
#                 continue




#             # Update other invoices items
#             other_items = frappe.get_all(
#                 "Sales Invoice Item",
#                 filters={
#                     "parent": ["in", invoices],
#                     "item_code": item.item_code
#                 },
#                 fields=["name"]
#             )

#             for oi in other_items:
#                 frappe.db.set_value(
#                     "Sales Invoice Item",
#                     oi.name,
#                     item_updates,
#                     update_modified=False
#                 )


#             # Update consolidated invoice items
#             cons_items = frappe.get_all(
#                 "Consolidated Sales Invoice Item",
#                 filters={
#                     "parent": consolidated_name,
#                     "item_code": item.item_code
#                 },
#                 fields=["name"]
#             )

#             for ci in cons_items:
#                 frappe.db.set_value(
#                     "Consolidated Sales Invoice Item",
#                     ci.name,
#                     item_updates,
#                     update_modified=False
#                 )

#         # ------------FOR CONTAINER DETAIL---------------

#         for container in doc.container_detail:

#             container_updates = {}

#             if container.container_no:
#                 container_updates["container_no"] = container.container_no

#             if container.size:
#                 container_updates["size"] = container.size

#             if container.lot_no:
#                 container_updates["lot_no"] = container.lot_no

#             if container.shipping_line_seal_no:
#                 container_updates["shipping_line_seal_no"] = container.shipping_line_seal_no

#             if container.nt_wt_kgs:
#                 container_updates["nt_wt_kgs"] = container.nt_wt_kgs

#             if container.gr_wt_kgs:
#                 container_updates["gr_wt_kgs"] = container.gr_wt_kgs

#             if container.no_of_packages:
#                 container_updates["no_of_packages"] = container.no_of_packages

#             if container.manufacturing_date:
#                 container_updates["manufacturing_date"] = container.manufacturing_date

#             if container.batch_name:
#                 container_updates["batch_name"] = container.batch_name


    
#             # -------------------------------
#             # Update container rows in Consolidated Invoice
#             # -------------------------------
#             cons_containers = frappe.get_all(
#                 "Container Details",
#                 filters={
#                     "parent": consolidated_name,
#                     "lot_no": container.lot_no
#                 },
#                 fields=["name"]
#             )

#             for cc in cons_containers:
#                 frappe.db.set_value(
#                     "Container Details",
#                     cc.name,
#                     container_updates,
#                     update_modified=False
#                 )

# # ------------FOR Sales Invoice Contract Term Check----------------

#         for contract_terms in doc.sales_invoice_contract_term_check:

#             contract_term_updates = {}

#             if contract_terms.contract_term:
#                 contract_term_updates["contract_term"] = contract_terms.contract_term

#             if contract_terms.document_check:
#                 contract_term_updates["document_check"] = contract_terms.document_check

#             if contract_terms.checked is not None:
#                 contract_term_updates["checked"] = contract_terms.checked

#             if not contract_term_updates:
#                 continue


#             # Update other Sales Invoice contract terms
#             other_contract_terms = frappe.get_all(
#                 "Sales Invoice Contract Term Check",
#                 filters={
#                     "parent": ["in", invoices],
#                     "contract_term": contract_terms.contract_term
#                 },
#                 fields=["name"]
#             )

#             for oct in other_contract_terms:
#                 frappe.db.set_value(
#                     "Sales Invoice Contract Term Check",
#                     oct.name,
#                     contract_term_updates,
#                     update_modified=False
#                 )


#             # Update Consolidated Sales Invoice contract terms
#             cons_contract_terms = frappe.get_all(
#                 "Sales Invoice Contract Term Check",
#                 filters={
#                     "parent": consolidated_name,
#                     "contract_term": contract_terms.contract_term
#                 },
#                 fields=["name"]
#             )

#             for cct in cons_contract_terms:
#                 frappe.db.set_value(
#                     "Sales Invoice Contract Term Check",
#                     cct.name,
#                     contract_term_updates,
#                     update_modified=False
#                 )

#     #-----------------FOR Sales Invoice Export Document Item -----------


#         for export_doc in doc.sales_invoice_export_document_item:

#             export_updates = {}

#             if export_doc.contract_term:
#                 export_updates["contract_term"] = export_doc.contract_term

#             if export_doc.export_document:
#                 export_updates["export_document"] = export_doc.export_document

#             if export_doc.number:
#                 export_updates["number"] = export_doc.number

#             if export_doc.checked is not None:
#                 export_updates["checked"] = export_doc.checked

#             if not export_updates:
#                 continue


#         # Update other Sales Invoice export documents
#             other_export_docs = frappe.get_all(
#                 "Sales Invoice Export Document Item",
#                 filters={
#                     "parent": ["in", invoices],
#                     "export_document": export_doc.export_document
#                 },
#                 fields=["name"]
#             )

#             for oed in other_export_docs:
#                 frappe.db.set_value(
#                     "Sales Invoice Export Document Item",
#                     oed.name,
#                     export_updates,
#                     update_modified=False
#                 )


#             # Update Consolidated Sales Invoice export documents
#             cons_export_docs = frappe.get_all(
#                 "Sales Invoice Export Document Item",
#                 filters={
#                     "parent": consolidated_name,
#                     "export_document": export_doc.export_document
#                 },
#                 fields=["name"]
#             )

#             for ced in cons_export_docs:
#                 frappe.db.set_value(
#                     "Sales Invoice Export Document Item",
#                     ced.name,
#                     export_updates,
#                     update_modified=False
#                 )

#     finally:
#         frappe.flags.in_consolidated_sync = False
def set_contract_term_details(doc, method=None):

    if not doc.contract_and_lc:
        return

    # Only run when field changes (IMPORTANT)
    if not doc.is_new() and not doc.has_value_changed("contract_and_lc"):
        return

    contract_doc = frappe.get_doc("Contract Term", doc.contract_and_lc)

    doc.flags.ignore_validate_update_after_submit = True

    doc.custom_lc_no = contract_doc.lc_no

    # -------------------------------
    # Preserve existing checked values
    # -------------------------------
    existing_export = {
        row.export_document: row.checked
        for row in doc.sales_invoice_export_document_item
    }

    existing_contract = {
        row.document_check: row.checked
        for row in doc.sales_invoice_contract_term_check
    }

    # -------------------------------
    # Clear and rebuild
    # -------------------------------
    doc.set("sales_invoice_export_document_item", [])
    doc.set("sales_invoice_contract_term_check", [])

    # -------------------------------
    # Export Documents
    # -------------------------------
    for d in contract_doc.document:
        doc.append("sales_invoice_export_document_item", {
            "contract_term": contract_doc.name,
            "export_document": d.export_document,
            "number": d.number,
            "checked": existing_export.get(d.export_document, 0)
        })

    # -------------------------------
    # Contract Term Check
    # -------------------------------
    for d in contract_doc.contract_term_check:
        doc.append("sales_invoice_contract_term_check", {
            "contract_term": contract_doc.name,
            "document_check": d.document_check,
            "checked": existing_contract.get(d.document_check, 0)
        })

def sync_workflow_from_sales_invoice(doc, method):

    if not doc.custom_consolidated_invoice_reference:
        return

    if frappe.flags.in_consolidated_sync:
        return

    frappe.flags.in_consolidated_sync = True

    try:

        consolidated_name = doc.custom_consolidated_invoice_reference
        new_state = doc.workflow_state
        new_docstatus = doc.docstatus

        # ---------------------------------------
        # Prepare Form Updates
        # ---------------------------------------
        form_updates = {
            "workflow_state": new_state,
            # "docstatus": new_docstatus
        }

        fields = [
            "bl_no","bl_date","vessel_no","custom_shipped_on_board_date","port_address","branch",
            "total_fob_value","freight","insurance","freight_calculated","total_duty_drawback",
            "total_meis","custom_lab_test_remarks","shipping_terms","is_export_with_gst","taxes_and_charges",
            "port_of_loading","port_of_discharge","pre_carriage_by","custom_dclc","custom_dc_no",
            "custom_lc_no","custom_loading_point","final_destination","custom_carriage_by",
            "custom_dhl","custom_dc_date","custom_lc_date","container_size","country_of_origin",
            "country_of_destination","movement","custom_submission_date",
            "custom_bl_issued_remarks","contract_and_lc","custom_document_checked","set_warehouse"
        ]

        for f in fields:
            val = doc.get(f)
            if val:
                form_updates[f] = val

        # ---------------------------------------
        # Update Consolidated Invoice
        # ---------------------------------------
        consolidated_doc = frappe.get_doc(
            "Consolidated Sales Invoice",
            consolidated_name
        )

        consolidated_doc.update(form_updates)
        if "contract_and_lc" in form_updates:
            set_contract_term_details(consolidated_doc)

        # ---------------------------------------
        # Get All Related Sales Invoices
        # ---------------------------------------
        invoice_names = frappe.get_all(
            "Sales Invoice",
            filters={
                "custom_consolidated_invoice_reference": consolidated_name
            },
            pluck="name"
        )

        invoices = [frappe.get_doc("Sales Invoice", inv) for inv in invoice_names]

        # ---------------------------------------
        # Update Other Sales Invoices
        # ---------------------------------------
        for inv in invoices:

            if inv.name == doc.name:
                continue

            inv.update(form_updates)
            if "contract_and_lc" in form_updates:
                set_contract_term_details(inv)

        # ---------------------------------------
        # ITEM TABLE SYNC
        # ---------------------------------------
        for item in doc.items:

            for inv in invoices:

                for row in inv.items:

                    if row.item_code != item.item_code:
                        continue

                    row.duty_drawback_rate = item.duty_drawback_rate
                    row.capped_rate = item.capped_rate
                    row.meis_rate = item.meis_rate
                    row.custom_rodtep_capped_rate = item.custom_rodtep_capped_rate
                    row.freight = item.freight
                    row.insurance = item.insurance
                    row.duty_drawback_amount = item.duty_drawback_amount
                    row.capped_amount = item.capped_amount
                    row.meis_value = item.meis_value
                    row.custom_rodtep_capped_amount = item.custom_rodtep_capped_amount
                    row.fob_value = item.fob_value
                    row.description = item.description

            for row in consolidated_doc.items:

                if row.item_code != item.item_code:
                    continue

                row.duty_drawback_rate = item.duty_drawback_rate
                row.capped_rate = item.capped_rate
                row.meis_rate = item.meis_rate
                row.custom_rodtep_capped_rate = item.custom_rodtep_capped_rate
                row.freight = item.freight
                row.insurance = item.insurance
                row.duty_drawback_amount = item.duty_drawback_amount
                row.capped_amount = item.capped_amount
                row.meis_value = item.meis_value
                row.custom_rodtep_capped_amount = item.custom_rodtep_capped_amount
                row.fob_value = item.fob_value
                row.description = item.description

        # ---------------------------------------
        # CONTAINER DETAILS SYNC
        # ---------------------------------------
        for container in doc.container_detail:

            for row in consolidated_doc.container_detail:

                if row.lot_no != container.lot_no:
                    continue

                row.container_no = container.container_no
                row.size = container.size
                row.lot_no = container.lot_no
                row.shipping_line_seal_no = container.shipping_line_seal_no
                row.nt_wt_kgs = container.nt_wt_kgs
                row.gr_wt_kgs = container.gr_wt_kgs
                row.no_of_packages = container.no_of_packages
                row.manufacturing_date = container.manufacturing_date
                row.batch_name = container.batch_name

        # ---------------------------------------
        # CONTRACT TERMS SYNC
        # ---------------------------------------
        for ct in doc.sales_invoice_contract_term_check:

            for inv in invoices:

                for row in inv.sales_invoice_contract_term_check:

                    if row.idx != ct.idx:
                        continue

                    row.contract_term = ct.contract_term
                    row.document_check = ct.document_check
                    row.checked = ct.checked

            for row in consolidated_doc.sales_invoice_contract_term_check:

                if row.idx != ct.idx:
                    continue

                row.contract_term = ct.contract_term
                row.document_check = ct.document_check
                row.checked = ct.checked

        # ---------------------------------------
        # EXPORT DOCUMENT SYNC
        # ---------------------------------------
        for ed in doc.sales_invoice_export_document_item:

            for inv in invoices:

                for row in inv.sales_invoice_export_document_item:

                    if row.idx != ed.idx:
                        continue

                    row.contract_term = ed.contract_term
                    row.export_document = ed.export_document
                    row.number = ed.number
                    row.checked = ed.checked

            for row in consolidated_doc.sales_invoice_export_document_item:

                if row.idx != ed.idx:
                    continue

                row.contract_term = ed.contract_term
                row.export_document = ed.export_document
                row.number = ed.number
                row.checked = ed.checked
                 # ---------------------------------------
        # PRODUCTION & BATCH TABLE FULL SYNC
        # (ADD + DELETE SAFE)
        # ---------------------------------------

        # Step 1: Collect all batch entries from ALL Sales Invoices
        all_batches = set()

        # Step 1: Collect all batch entries from ALL Sales Invoices
        for inv in invoices:
            for pb in inv.custom_production_and_batch_table:
                key = (
                    pb.batch_code,
                    str(pb.production_date),
                    str(pb.expiry_date)
                )
                all_batches.add(key)

        # Step 2: Remove entries from Consolidated that no longer exist
        rows_to_remove = []
        for row in consolidated_doc.production_and_batch_table:
            key = (
                row.batch_code,
                str(row.production_date),
                str(row.expiry_date)
            )

            if key not in all_batches:
                rows_to_remove.append(row)

        for row in rows_to_remove:
            consolidated_doc.remove(row)

        # Step 3: Add missing entries
        existing_batches = set()
        for row in consolidated_doc.production_and_batch_table:
            key = (
                row.batch_code,
                str(row.production_date),
                str(row.expiry_date)
            )
            existing_batches.add(key)

        for key in all_batches:
            if key in existing_batches:
                continue

            consolidated_doc.append("production_and_batch_table", {
                "batch_code": key[0],
                "production_date": key[1],
                "expiry_date": key[2]
            })

        # ---------------------------------------
        # SAVE ALL DOCUMENTS
        # ---------------------------------------
        for inv in invoices:
            if inv.name != doc.name:
                inv.flags.ignore_validate = True
                inv.flags.ignore_mandatory = True
                inv.flags.ignore_version = True
                inv.save(ignore_permissions=True)

        consolidated_doc.flags.ignore_version = True
        consolidated_doc.save(ignore_permissions=True)

    finally:
        frappe.flags.in_consolidated_sync = False


    # lot_list = []

    # for item in doc.items:
    #     if item.serial_and_batch_bundle:
    #         bundle = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
    #         for entry in bundle.entries:
    #             if entry.batch_no:
    #                 lot_list.append({"lot_no": entry.batch_no})

    # existing_lots = {row.lot_no for row in doc.container_detail}

    # for lot in lot_list:
    #     if lot["lot_no"] not in existing_lots:
    #         item_code = doc.items[0].item_code if doc.items else None
    #         packages = frappe.db.get_value(
    #             "Item", item_code, "custom_no_of_packages_per_lot"
    #         ) if item_code else None

    #         doc.append("container_detail", {
    #             "lot_no": lot["lot_no"],
    #             "no_of_packages": packages
    #         })




# def validate(doc, method=None):
#     if not doc.items:
#         return
#     print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
#     lot_list = []

#     for item in doc.items:
#         if not item.serial_and_batch_bundle:
#             continue

#         bundle = frappe.get_doc(
#             "Serial and Batch Bundle",
#             item.serial_and_batch_bundle
#         )

#         conversion_factor = frappe.db.get_value(
#             "UOM Conversion Detail",
#             {
#                 "parent": item.item_code,
#                 "uom": "Packet"
#             },
#             "conversion_factor"
#         )

#         if not conversion_factor:
#             frappe.throw(
#                 f"Packet UOM conversion not defined for Item {item.item_code}"
#             )

#         for entry in bundle.entries:
#             if not entry.batch_no:
#                 continue

#             # IMPORTANT: entry.qty is negative for outward stock
#             batch_qty = abs(flt(entry.qty))  # ✅ normalize

#             lot_list.append({
#                 "lot_no": entry.batch_no,
#                 "batch_qty": batch_qty,
#                 "conversion_factor": conversion_factor
#             })

#     existing_lots = {row.lot_no for row in doc.container_detail}

#     for lot in lot_list:
#         if lot["lot_no"] in existing_lots:
#             continue

#         no_of_packages = flt(lot["batch_qty"]) / flt(lot["conversion_factor"])

#         doc.append("container_detail", {
#             "lot_no": lot["lot_no"],
#             "no_of_packages": int(no_of_packages)
#         })


















#     # Optional: handle submit-time transition
#     if doc.docstatus == 1:
#         print(4444444444444444444444444444444,doc.docstatus)
#             # _handle_custom_status_change(doc)
#         update_sales_contract_from_invoice(doc)

# def on_update_after_submit(doc, method=None):
#     _handle_custom_status_change(doc)
    
# def _handle_custom_status_change(doc):
#     #  Shipment completed after submission
#     if (
#         doc.docstatus == 1
#         and doc.custom_work_flow_status == "Completed Shipment"
#     ):
#         update_sales_contract_from_invoice(doc)

# def update_sales_contract_from_invoice(sales_invoice):
#     print("thisssssssssssss is meeeeeeeee")
#     for si_item in sales_invoice.items:
#         if not si_item.sales_order:
#             continue

#         sales_contract = frappe.get_doc("Sales Order", si_item.sales_order)

#         if sales_contract.docstatus != 1:
#             continue

#         recalculate_shipment_schedule(
#             sales_contract,
#             si_item.item_code,
#             sales_invoice.posting_date
#         )

#         sales_contract.save(ignore_permissions=True)
    

# def recalculate_shipment_schedule(sales_contract, item_code, posting_date):
#     posting_date = getdate(posting_date)
#     month_name = posting_date.strftime("%B")
#     fiscal_year = posting_date.year

#     for row in sales_contract.custom_shipment_schedule:
#         if row.month == "Prompt":

#             submitted_qty = frappe.db.sql("""
#                 SELECT SUM(sii.qty)
#                 FROM `tabSales Invoice Item` sii
#                 INNER JOIN `tabSales Invoice` si
#                     ON si.name = sii.parent
#                 WHERE
#                     sii.item_code = %s
#                     AND sii.sales_order = %s
#                     AND si.docstatus = 1
#             """, (
#                 item_code,
#                 sales_contract.name
#             ))[0][0] or 0

#             completed_qty = frappe.db.sql("""
#                 SELECT SUM(sii.qty)
#                 FROM `tabSales Invoice Item` sii
#                 INNER JOIN `tabSales Invoice` si
#                     ON si.name = sii.parent
#                 WHERE
#                     sii.item_code = %s
#                     AND sii.sales_order = %s
#                     AND si.docstatus = 1
#                     AND si.custom_work_flow_status = 'Completed Shipment'
#             """, (
#                 item_code,
#                 sales_contract.name
#             ))[0][0] or 0

#             submitted_qty = flt(submitted_qty)
#             completed_qty = flt(completed_qty)

#             if completed_qty >= row.planned_qty and row.planned_qty > 0:
#                 row.status = "Completed"
#             elif submitted_qty > 0:
#                 row.status = "In-Process"
#             else:
#                 row.status = None

#             continue
#         # monthly
#         if row.month != month_name or int(row.fiscal_year) != fiscal_year:
#             continue
#         print("thisssssssssssss is saheeeeeeeeeeeeeer")
#         submitted_qty = frappe.db.sql("""
#             SELECT SUM(sii.qty)
#             FROM `tabSales Invoice Item` sii
#             INNER JOIN `tabSales Invoice` si
#                 ON si.name = sii.parent
#             WHERE
#                 sii.item_code = %s
#                 AND sii.sales_order = %s
#                 AND si.docstatus = 1
#                 AND MONTH(si.posting_date) = %s
#                 AND YEAR(si.posting_date) = %s
#         """, (
#             item_code,
#             sales_contract.name,
#             posting_date.month,
#             posting_date.year
#         ))[0][0] or 0

#         completed_qty = frappe.db.sql("""
#             SELECT SUM(sii.qty)
#             FROM `tabSales Invoice Item` sii
#             INNER JOIN `tabSales Invoice` si
#                 ON si.name = sii.parent
#             WHERE
#                 sii.item_code = %s
#                 AND sii.sales_order = %s
#                 AND si.docstatus = 1
#                 AND si.custom_work_flow_status = 'Completed Shipment'
#                 AND MONTH(si.posting_date) = %s
#                 AND YEAR(si.posting_date) = %s
#         """, (
#             item_code,
#             sales_contract.name,
#             posting_date.month,
#             posting_date.year
#         ))[0][0] or 0

#         submitted_qty = flt(submitted_qty)
#         print(333333333333333333333333333333,submitted_qty)
#         completed_qty = flt(completed_qty)
#         print(555555555555555555555555,completed_qty)

#         if completed_qty >= row.planned_qty :
#             row.status = "Completed"
#         elif submitted_qty > 0:
#             row.status = "In-Process"
#         else:
#             row.status = None

# def get_month_date_range(month_name, year):
#     month_number = list(calendar.month_name).index(month_name)
#     start_date = date(year, month_number, 1)
#     last_day = calendar.monthrange(year, month_number)[1]
#     end_date = date(year, month_number, last_day)
#     return start_date, end_date














# add the refrence code-correct

# import frappe
# from frappe.utils import flt, getdate
# import calendar
# from datetime import date


# # -------------------------------------------------------------------
# # Hooks
# # -------------------------------------------------------------------

# def on_submit(doc, method=None):
#     if doc.docstatus == 1:
#         update_sales_contract_from_invoice(doc)


# def on_update_after_submit(doc, method=None):
#     _handle_custom_status_change(doc)


# def _handle_custom_status_change(doc):
#     if doc.docstatus == 1 and doc.custom_work_flow_status == "Completed Shipment":
#         update_sales_contract_from_invoice(doc)


# # -------------------------------------------------------------------
# # Main Update Logic
# # -------------------------------------------------------------------

# def update_sales_contract_from_invoice(sales_invoice):
#     for si_item in sales_invoice.items:
#         if not si_item.sales_order:
#             continue

#         sales_contract = frappe.get_doc("Sales Order", si_item.sales_order)

#         if sales_contract.docstatus != 1:
#             continue

#         # Clear references if this is the first invoice
#         clear_reference_if_first_invoice(sales_contract)

#         recalculate_shipment_schedule(
#             sales_contract=sales_contract,
#             item_code=si_item.item_code,
#             posting_date=sales_invoice.posting_date,
#             invoice_name=sales_invoice.name
#         )

#         sales_contract.save(ignore_permissions=True)


# -------------------------------------------------------------------
# Shipment Schedule Recalculation
# -------------------------------------------------------------------

def recalculate_shipment_schedule(
    sales_contract,
    item_code,
    posting_date,
    invoice_name
):
    posting_date = getdate(posting_date)

    for row in sales_contract.custom_shipment_schedule:

        previous_status = row.status

        # ---------------- PROMPT ----------------
        if row.month == "Prompt":

            submitted_qty = frappe.db.sql("""
                SELECT SUM(sii.qty)
                FROM `tabSales Invoice Item` sii
                INNER JOIN `tabSales Invoice` si
                    ON si.name = sii.parent
                WHERE
                    sii.item_code = %s
                    AND sii.sales_order = %s
                    AND si.docstatus = 1
            """, (item_code, sales_contract.name))[0][0] or 0

            completed_qty = frappe.db.sql("""
                SELECT SUM(sii.qty)
                FROM `tabSales Invoice Item` sii
                INNER JOIN `tabSales Invoice` si
                    ON si.name = sii.parent
                WHERE
                    sii.item_code = %s
                    AND sii.sales_order = %s
                    AND si.docstatus = 1
                    AND si.custom_work_flow_status = 'Completed Shipment'
            """, (item_code, sales_contract.name))[0][0] or 0

            submitted_qty = flt(submitted_qty)
            completed_qty = flt(completed_qty)

            if completed_qty >= row.planned_qty and row.planned_qty > 0:
                row.status = "Completed"
            elif submitted_qty > 0:
                row.status = "In-Process"
            else:
                row.status = None

            if row.status != previous_status:
                append_invoice_reference(row, invoice_name)

            continue


        # ---------------- DATE RANGE LOGIC ----------------
        if not row.start_date or not row.end_date:
            continue

        start_date = getdate(row.start_date)
        end_date = getdate(row.end_date)

        # Skip rows where invoice date is outside range
        if not (start_date <= posting_date <= end_date):
            continue


        submitted_qty = frappe.db.sql("""
            SELECT SUM(sii.qty)
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si
                ON si.name = sii.parent
            WHERE
                sii.item_code = %s
                AND sii.sales_order = %s
                AND si.docstatus = 1
                AND si.posting_date BETWEEN %s AND %s
        """, (
            item_code,
            sales_contract.name,
            start_date,
            end_date
        ))[0][0] or 0


        completed_qty = frappe.db.sql("""
            SELECT SUM(sii.qty)
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si
                ON si.name = sii.parent
            WHERE
                sii.item_code = %s
                AND sii.sales_order = %s
                AND si.docstatus = 1
                AND si.custom_work_flow_status = 'Completed Shipment'
                AND si.posting_date BETWEEN %s AND %s
        """, (
            item_code,
            sales_contract.name,
            start_date,
            end_date
        ))[0][0] or 0


        submitted_qty = flt(submitted_qty)
        completed_qty = flt(completed_qty)


        if completed_qty >= row.planned_qty and row.planned_qty > 0:
            row.status = "Completed"
        elif submitted_qty > 0:
            row.status = "In-Process"
        else:
            row.status = None


        if row.status != previous_status:
            append_invoice_reference(row, invoice_name)

        # Stop after updating correct schedule row
        break


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def clear_reference_if_first_invoice(sales_contract):
    """
    Clears copied references only when this Sales Order
    is getting its FIRST submitted Sales Invoice.
    """

    invoice_count = frappe.db.sql("""
        SELECT COUNT(DISTINCT si.name)
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            AND sii.sales_order = %s
    """, (sales_contract.name,))[0][0] or 0

    # If more than one invoice exists, do NOT clear
    if invoice_count > 1:
        return

    for row in sales_contract.custom_shipment_schedule:
        row.reference = None


def append_invoice_reference(row, invoice_name):
    if not invoice_name:
        return

    existing = row.reference or ""
    refs = [r.strip() for r in existing.split(",") if r.strip()]

    if invoice_name not in refs:
        refs.append(invoice_name)
        row.reference = ", ".join(refs)


def get_month_date_range(month_name, year):
    month_number = list(calendar.month_name).index(month_name)
    start_date = date(year, month_number, 1)
    last_day = calendar.monthrange(year, month_number)[1]
    end_date = date(year, month_number, last_day)
    return start_date, end_date


import frappe
from frappe.utils import flt, getdate
import calendar
from datetime import date


# -------------------------------------------------------------------
# Hooks
# -------------------------------------------------------------------

def on_submit(doc, method=None):
    if doc.docstatus == 1:
        update_sales_contract_from_invoice(doc)


def on_update(doc, method=None):
    sync_linked_sales_invoices(doc)



def on_update_after_submit(doc, method=None):
    print("on update after submit is working........")
    _handle_custom_status_change(doc)
    update_sales_order_qty(doc)
    set_contract_term_details(doc)
    """
    This function runs every time a submitted Sales Invoice is updated 
    (e.g., when the Workflow State changes).
    """
    target_state = "Document Submitted & Awaiting Payments"

    # Check if the workflow state matches and the date hasn't been recorded yet
    if doc.workflow_state == target_state and not doc.custom_submission_date:
        
        # We use db_set to bypass validation since the doc is already submitted
        doc.db_set('custom_submission_date', nowdate())
        
        # Optional: notify the user or add a comment
        doc.add_comment("Info", text=f"Captured submission date as state changed to {target_state}")
    
    


def update_sales_order_qty(doc):

    sales_orders = set()

    # Collect unique Sales Orders from the invoice
    for item in doc.items:
        if item.sales_order:
            sales_orders.add(item.sales_order)

    for sales_order in sales_orders:

        delivered_qty = frappe.db.sql("""
            SELECT SUM(si_item.qty)
            FROM `tabSales Invoice Item` si_item
            JOIN `tabSales Invoice` si
                ON si.name = si_item.parent
            WHERE
                si.docstatus = 1
                AND si.workflow_state = 'Completed Shipment'
                AND si_item.sales_order = %s
        """, sales_order)[0][0] or 0

        total_qty = frappe.db.get_value(
            "Sales Order",
            sales_order,
            "total_qty"
        ) or 0

        pending_qty = flt(total_qty) - flt(delivered_qty)

        frappe.db.set_value(
            "Sales Order",
            sales_order,
            {
                "custom_delivered_qty": delivered_qty,
                "custom_pending_qty": pending_qty
            }
        )

        
def on_cancel(doc, method=None):
    print("111111111111")

    sales_orders = {item.sales_order for item in doc.items if item.sales_order}

    for sales_order in sales_orders:

        total_qty = frappe.db.get_value(
            "Sales Order",
            sales_order,
            "total_qty"
        ) or 0
                                                                                                           
        frappe.db.set_value(
            "Sales Order",
            sales_order,
            {
                "custom_delivered_qty": 0,
                "custom_pending_qty": total_qty
            },
            update_modified=False,
            ignore_permissions=True
        )

    remove_invoice_reference_from_sales_order(doc)




def _handle_custom_status_change(doc):
    if doc.docstatus == 1 and doc.custom_work_flow_status == "Completed Shipment":
        update_sales_contract_from_invoice(doc)


# -------------------------------------------------------------------
# Main Update Logic
# -------------------------------------------------------------------

def update_sales_contract_from_invoice(sales_invoice):
    for si_item in sales_invoice.items:
        if not si_item.sales_order:
            continue

        sales_contract = frappe.get_doc("Sales Order", si_item.sales_order)

        if sales_contract.docstatus != 1:
            continue

        # Clear references if this is the first invoice
        clear_reference_if_first_invoice(sales_contract)

        recalculate_shipment_schedule(
            sales_contract=sales_contract,
            item_code=si_item.item_code,
            posting_date=sales_invoice.posting_date,
            invoice_name=sales_invoice.name
        )

        sales_contract.save(ignore_permissions=True)


# -------------------------------------------------------------------
# Shipment Schedule Recalculation
# -------------------------------------------------------------------

# def recalculate_shipment_schedule(
#     sales_contract,
#     item_code,
#     posting_date,
#     invoice_name
# ):
#     posting_date = getdate(posting_date)
#     month_name = posting_date.strftime("%B")
#     fiscal_year = posting_date.year

#     for row in sales_contract.custom_shipment_schedule:

#         previous_status = row.status

#         # ---------------- PROMPT ----------------
#         if row.month == "Prompt":

#             submitted_qty = frappe.db.sql("""
#                 SELECT SUM(sii.qty)
#                 FROM `tabSales Invoice Item` sii
#                 INNER JOIN `tabSales Invoice` si
#                     ON si.name = sii.parent
#                 WHERE
#                     sii.item_code = %s
#                     AND sii.sales_order = %s
#                     AND si.docstatus = 1
#             """, (item_code, sales_contract.name))[0][0] or 0

#             completed_qty = frappe.db.sql("""
#                 SELECT SUM(sii.qty)
#                 FROM `tabSales Invoice Item` sii
#                 INNER JOIN `tabSales Invoice` si
#                     ON si.name = sii.parent
#                 WHERE
#                     sii.item_code = %s
#                     AND sii.sales_order = %s
#                     AND si.docstatus = 1
#                     AND si.custom_work_flow_status = 'Completed Shipment'
#             """, (item_code, sales_contract.name))[0][0] or 0

#             submitted_qty = flt(submitted_qty)
#             completed_qty = flt(completed_qty)

#             if completed_qty >= row.planned_qty and row.planned_qty > 0:
#                 row.status = "Completed"
#             elif submitted_qty > 0:
#                 row.status = "In-Process"
#             else:
#                 row.status = None

#             if row.status != previous_status:
#                 append_invoice_reference(row, invoice_name)

#             continue

#         # ---------------- MONTHLY ----------------
#         if row.month != month_name or int(row.fiscal_year) != fiscal_year:
#             continue

#         submitted_qty = frappe.db.sql("""
#             SELECT SUM(sii.qty)
#             FROM `tabSales Invoice Item` sii
#             INNER JOIN `tabSales Invoice` si
#                 ON si.name = sii.parent
#             WHERE
#                 sii.item_code = %s
#                 AND sii.sales_order = %s
#                 AND si.docstatus = 1
#                 AND MONTH(si.posting_date) = %s
#                 AND YEAR(si.posting_date) = %s
#         """, (
#             item_code,
#             sales_contract.name,
#             posting_date.month,
#             posting_date.year
#         ))[0][0] or 0

#         completed_qty = frappe.db.sql("""
#             SELECT SUM(sii.qty)
#             FROM `tabSales Invoice Item` sii
#             INNER JOIN `tabSales Invoice` si
#                 ON si.name = sii.parent
#             WHERE
#                 sii.item_code = %s
#                 AND sii.sales_order = %s
#                 AND si.docstatus = 1
#                 AND si.custom_work_flow_status = 'Completed Shipment'
#                 AND MONTH(si.posting_date) = %s
#                 AND YEAR(si.posting_date) = %s
#         """, (
#             item_code,
#             sales_contract.name,
#             posting_date.month,
#             posting_date.year
#         ))[0][0] or 0

#         submitted_qty = flt(submitted_qty)
#         completed_qty = flt(completed_qty)

#         if completed_qty >= row.planned_qty and row.planned_qty > 0:
#             row.status = "Completed"
#         elif submitted_qty > 0:
#             row.status = "In-Process"
#         else:
#             row.status = None

#         if row.status != previous_status:
#             append_invoice_reference(row, invoice_name)


# # -------------------------------------------------------------------
# # Helpers
# # -------------------------------------------------------------------

# def clear_reference_if_first_invoice(sales_contract):
#     """
#     Clears copied references only when this Sales Order
#     is getting its FIRST submitted Sales Invoice.
#     """

#     invoice_count = frappe.db.sql("""
#         SELECT COUNT(DISTINCT si.name)
#         FROM `tabSales Invoice` si
#         INNER JOIN `tabSales Invoice Item` sii
#             ON sii.parent = si.name
#         WHERE
#             si.docstatus = 1
#             AND sii.sales_order = %s
#     """, (sales_contract.name,))[0][0] or 0

#     if invoice_count > 1:
#         return

#     for row in sales_contract.custom_shipment_schedule:
#         row.reference = None


# def append_invoice_reference(row, invoice_name):
#     if not invoice_name:
#         return

#     existing = row.reference or ""
#     refs = [r.strip() for r in existing.split(",") if r.strip()]

#     if invoice_name not in refs:
#         refs.append(invoice_name)
#         row.reference = ", ".join(refs)


# def remove_invoice_reference_from_sales_order(sales_invoice):
#     for si_item in sales_invoice.items:
#         if not si_item.sales_order:
#             continue

#         sales_contract = frappe.get_doc("Sales Order", si_item.sales_order)

#         if sales_contract.docstatus != 1:
#             continue

#         invoice_name = sales_invoice.name
#         changed = False

#         for row in sales_contract.custom_shipment_schedule:
#             if not row.reference:
#                 continue

#             refs = [r.strip() for r in row.reference.split(",") if r.strip()]

#             if invoice_name in refs:
#                 refs.remove(invoice_name)
#                 row.reference = ", ".join(refs) if refs else None
#                 changed = True

#         if changed:
#             sales_contract.save(ignore_permissions=True)


# def get_month_date_range(month_name, year):
#     month_number = list(calendar.month_name).index(month_name)
#     start_date = date(year, month_number, 1)
#     last_day = calendar.monthrange(year, month_number)[1]
#     end_date = date(year, month_number, last_day)
#     return start_date, end_date








# ------------------------------------------------------------------------------------------------------------------------

def before_submit(self,method):
	# if self._action == 'submit':
	print(222222222222)
	# validate_document_checks(self)
	before_workflow_action(self)


def on_submit(self, method):
    export_lic(self)
    create_jv(self)
    # create_brc(self)
    create_jv_with_gst(self)
    update_sales_contract_from_invoice(self)
    if frappe.flags.in_auto_submit:
        return

    frappe.flags.in_auto_submit = True

    try:

        if not self.custom_consolidated_invoice_reference:
            return

        consolidated_name = self.custom_consolidated_invoice_reference

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "custom_consolidated_invoice_reference": consolidated_name
            },
            pluck="name"
        )

        for inv in invoices:

            if inv == self.name:
                continue

            invoice_doc = frappe.get_doc("Sales Invoice", inv)

            if invoice_doc.docstatus == 0 and not invoice_doc.is_return:
                invoice_doc.submit()
        consolidated_doc = frappe.get_doc("Consolidated Sales Invoice", consolidated_name)

        if consolidated_doc.docstatus == 0:
            consolidated_doc.submit()

    finally:
        frappe.flags.in_auto_submit = False



def on_cancel(self, method):
    sales_order_qty_map = {}

    #  Collect qty per Sales Order from THIS invoice
    for item in self.items:
        if not item.sales_order:
            continue

        sales_order_qty_map.setdefault(item.sales_order, 0)
        sales_order_qty_map[item.sales_order] += flt(item.qty)

    #  Update Sales Order quantities
    for sales_order, cancel_qty in sales_order_qty_map.items():

        so = frappe.get_doc("Sales Order", sales_order)

        delivered_qty = flt(so.custom_delivered_qty)
        pending_qty = flt(so.custom_pending_qty)

        new_delivered = max(delivered_qty - cancel_qty, 0)
        new_pending = pending_qty + cancel_qty

        frappe.db.set_value(
            "Sales Order",
            sales_order,
            {
                "custom_delivered_qty": new_delivered,
                "custom_pending_qty": new_pending
            },
            update_modified=False
        )

    remove_invoice_reference_from_sales_order(self)
    cancel_export_lic(self)
    cancel_jv(self)
    update_sales_contract_from_invoice(self)


def calculate_total(self):
	total_qty = 0
	total_packages = 0
	total_gr_wt = 0
	total_tare_wt = 0
	total_freight = 0
	total_insurance = 0
	total_meis = 0
	total_drawback = 0
	total_rodtep = 0
	total_fob_value = 0
	total_pallets = 0

	if self.gst_category == "Overseas" and not self.manually_enter_fob_value and self.freight_calculated in ["By Qty", "By Amount"] and self.shipping_terms not in ["CIF", "CFR", "CNF", "CPT"]:
		frappe.msgprint(f"To calculate item wise freight please ensure shipping terms are set either of {frappe.bold('CIF, CFR, CNF OR CPT')}.")

	for row in self.items:
		if self.freight_calculated == "By Qty":
			row.freight = (row.qty * self.freight) / self.total_qty
			row.insurance = (row.qty * self.insurance) / self.total_qty
		elif self.freight_calculated == "By Amount":
			row.freight = (row.base_amount * self.freight) / self.base_total
			row.insurance = (row.base_amount * self.insurance) / self.base_total
		else:
			total_freight += flt(row.freight)
			total_insurance += flt(row.insurance)
		
		total_qty += flt(row.qty)
		total_packages += flt(row.no_of_packages)

		row.total_tare_weight = flt(row.tare_wt * row.no_of_packages)
		
		pallet = flt(row.pallet_weight) * flt(row.total_pallets)
		row.gross_wt = flt(row.total_tare_weight) + (flt(row.qty) * (flt(row.weight_per_unit) or 1)) + flt(pallet)
		
		if not self.manually_enter_fob_value and self.gst_category == "Overseas":
			if self.shipping_terms in ["CIF", "CFR", "CNF", "CPT"]:
				row.fob_value = flt(row.base_amount) - flt(row.freight * self.conversion_rate) - flt(row.insurance * self.conversion_rate)
			else:
				row.fob_value = flt(row.base_amount)
		
		total_tare_wt += flt(row.total_tare_weight)
		total_gr_wt += flt(row.gross_wt)
		total_insurance += flt(row.insurance)
		total_meis += flt(row.meis_value)
		total_drawback += row.duty_drawback_amount
		row.total_duty_drawback = total_drawback
		total_rodtep += row.meis_value
		total_fob_value += flt(row.fob_value)
		total_pallets += flt(row.total_pallets)
	
	self.total_qty = total_qty
	self.total_packages = total_packages
	self.total_gr_wt = total_gr_wt
	self.total_tare_wt = total_tare_wt
	if self.freight_calculated == "Manual":
		self.freight = total_freight
		self.insurance = total_insurance
	self.total_fob_value = total_fob_value
	self.total_pallets = total_pallets


def duty_calculation(self):
    parent_meta = frappe.get_meta(self.doctype)

    if parent_meta.has_field('total_duty_drawback') and frappe.db.get_value('Address', self.customer_address, 'country') != "India":
        total_duty_drawback = 0.0
        
        for row in self.items:
            child_meta = frappe.get_meta(row.doctype)
            
            conversion_factor = frappe.db.get_value(
                "UOM Conversion Detail",
                {"parent": row.item_code, "uom": row.uom},
                "conversion_factor"
            ) or 1.0

            calculated_weight = flt(row.qty * conversion_factor)

            # Default values 
            row.capped_amount = 0.0
            row.duty_drawback_amount = 0.0

            if row.duty_drawback_rate and row.fob_value:
                duty_drawback_amount = flt(row.fob_value * row.duty_drawback_rate / 100.0)

                #  capped calculation using qty * conversion_factor
                if row.capped_rate and calculated_weight:
                    row.capped_amount = flt(calculated_weight * row.capped_rate)

                #  APPLY YOUR LOGIC (this was missing)
                if getattr(row, "maximum_cap", 0) == 1:
                    if row.capped_amount and row.capped_amount < duty_drawback_amount:
                        row.duty_drawback_amount = row.capped_amount
                        row.effective_rate = flt(row.capped_amount / row.fob_value * 100.0)
                    else:
                        row.duty_drawback_amount = duty_drawback_amount
                        row.effective_rate = row.duty_drawback_rate
                else:
                    row.duty_drawback_amount = duty_drawback_amount

            row.igst_taxable_value = flt(row.amount)

            total_duty_drawback += flt(row.duty_drawback_amount)

        self.total_duty_drawback = total_duty_drawback


# def duty_calculation(self):
#     parent_meta = frappe.get_meta(self.doctype)

#     if parent_meta.has_field('total_duty_drawback') and frappe.db.get_value('Address', self.customer_address, 'country') != "India":
#         total_duty_drawback = 0.0
        
#         for row in self.items:
#             child_meta = frappe.get_meta(row.doctype)
            
#             # Fetch conversion factor from Item Master based on Item Code and UOM
#             conversion_factor = frappe.db.get_value("UOM Conversion Detail", 
#                 {"parent": row.item_code, "uom": row.uom}, "conversion_factor") or 1.0
            
#             if child_meta.has_field('duty_drawback_rate') and row.duty_drawback_rate and row.fob_value:
#                 duty_drawback_amount = flt(row.fob_value * row.duty_drawback_rate / 100.0)
                
#                 if child_meta.has_field('duty_drawback_amount'):
#                     # Using fetched conversion factor for weight calculation
#                     if child_meta.has_field('capped_rate') and row.capped_rate and row.qty:
#                         row.capped_amount = flt((row.qty * flt(conversion_factor)) * row.capped_rate)
                    
#                     # if row.maximum_cap == 1:
#                     #     if row.capped_amount and row.capped_amount < duty_drawback_amount:
#                     #         row.duty_drawback_amount = row.capped_amount
#                     #         row.effective_rate = flt(row.capped_amount / row.fob_value * 100.0)
#                     #     else:
#                     #         row.duty_drawback_amount = duty_drawback_amount
#                     #         row.effective_rate = row.duty_drawback_rate
#                     # else:
#                     #     row.duty_drawback_amount = duty_drawback_amount

#             row.igst_taxable_value = flt(row.amount)
#             if child_meta.has_field('duty_drawback_amount'):
#                 total_duty_drawback += flt(row.duty_drawback_amount) or 0.0

#         self.total_duty_drawback = total_duty_drawback


# def duty_calculation(self):
#     parent_meta = frappe.get_meta(self.doctype)

#     # Check if country is not India and field exists
#     if parent_meta.has_field('total_duty_drawback') and frappe.db.get_value('Address', self.customer_address, 'country') != "India":
#         total_duty_drawback = 0.0
        
#         for row in self.items:
#             child_meta = frappe.get_meta(row.doctype)
            
#             if child_meta.has_field('duty_drawback_rate') and row.duty_drawback_rate and row.fob_value:
#                 # 1. Standard calculation based on % rate
#                 duty_drawback_amount = flt(row.fob_value * row.duty_drawback_rate / 100.0)
                
#                 if child_meta.has_field('duty_drawback_amount'):
#                     # --- NEW LOGIC START ---
#                     # If a capped_rate (per kg) is provided, calculate the capped_amount
#                     if child_meta.has_field('capped_rate') and row.capped_rate and row.total_weight:
#                         row.capped_amount = flt(row.total_weight * row.capped_rate)
                    

#                     if row.maximum_cap == 1:
#                         # Compare drawback amount vs the newly calculated capped_amount
#                         if row.capped_amount and row.capped_amount < duty_drawback_amount:
#                             row.duty_drawback_amount = row.capped_amount
#                             row.effective_rate = flt(row.capped_amount / row.fob_value * 100.0)
#                         else:
#                             row.duty_drawback_amount = duty_drawback_amount
#                             row.effective_rate = row.duty_drawback_rate
#                     else:
#                         row.duty_drawback_amount = duty_drawback_amount

#             row.igst_taxable_value = flt(row.amount)
#             if child_meta.has_field('duty_drawback_amount'):
#                 total_duty_drawback += flt(row.duty_drawback_amount) or 0.0

#         self.total_duty_drawback = total_duty_drawback

def meis_calculation(self):
    if frappe.db.get_value('Address', self.customer_address, 'country') != "India":
        total_meis = 0.0

        for row in self.items:
            rodtep_fob_value = 0.0
            rodtep_kg_value = 0.0

            # 1. Fetch conversion_factor from Item Master (UOM Conversion Detail)
            # We look for the row where parent is the Item and UOM matches the row's UOM
            conversion_factor = frappe.db.get_value(
                "UOM Conversion Detail", 
                {"parent": row.item_code, "uom": row.uom}, 
                "conversion_factor"
            ) or 1.0  # Default to 1.0 if not found

            # 2. Calculate the dynamic weight (qty * conversion_factor)
            calculated_weight = flt(row.qty * flt(conversion_factor))

            # RoDTEP on FOB (%)
            if row.fob_value and row.meis_rate:
                rodtep_fob_value = flt(
                    row.fob_value * row.meis_rate / 100
                )

            # RoDTEP on Per Kg (Capped) — Using calculated weight instead of total_weight
            if calculated_weight and row.custom_rodtep_capped_rate:
                rodtep_kg_value = flt(
                    calculated_weight * row.custom_rodtep_capped_rate
                )
                row.custom_rodtep_capped_amount = rodtep_kg_value
            else:
                row.custom_rodtep_capped_amount = 0.0

            # Final RoDTEP = LOWER of FOB % or Kg cap
            if rodtep_fob_value and rodtep_kg_value:
                row.meis_value = min(rodtep_fob_value, rodtep_kg_value)
            else:
                row.meis_value = rodtep_fob_value or rodtep_kg_value or 0.0

            total_meis += flt(row.meis_value)

        self.total_meis = total_meis

# def validate_document_checks(self):
# 	if self.get('sales_invoice_export_document_item') and not all([row.checked for row in self.get('sales_invoice_export_document_item')]):
# 		print(3333333333)
# 		frappe.throw(_("Not all documents are checked for Export Documents"))

# 	elif self.get('sales_invoice_contract_term_check') and not all([row.checked for row in self.get('sales_invoice_contract_term_check')]):
# 		print(9999999999)
# 		frappe.throw(_("Not all documents are checked for Document Checks"))





def export_lic(self):
	for row in self.items:
		if row.get('advance_authorisation_license'):
			aal = frappe.get_doc("Advance Authorisation License", row.advance_authorisation_license)
			aal.append("exports", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"quantity": row.qty,
				"uom": row.uom,
				"fob_value" : flt(row.fob_value) / self.conversion_rate,
				"currency" : self.currency,	
				"shipping_bill_no": self.shipping_bill_number,
				"shipping_bill_date": self.shipping_bill_date,
				"port_of_loading" : self.port_of_loading,
				"port_of_discharge" : self.port_of_discharge,
				"sales_invoice" : self.name,
			})

			aal.total_export_qty = sum([flt(d.quantity) for d in aal.exports])
			aal.total_export_amount = sum([flt(d.fob_value) for d in aal.exports])
			aal.save()

# def create_jv_with_gst(self):
#     if not (self.get("is_export_with_gst") and self.get("taxes")):
#         return

#     taxes = self.get("taxes")[0]
#     company_gst_payable_account = frappe.db.get_value(
#         "Company", {"company_name": self.company}, "igst_export_refund_receivable"
#     )
#     currency_precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
#     jv = frappe.get_doc(
#         {
#             "doctype": "Journal Entry",
#             "voucher_type": "Journal Entry",
#             "posting_date": self.posting_date,
#             "cheque_date": self.posting_date,
#             "multi_currency": 1,
#             "company": self.company,
#             "company_gstin": self.company_gstin,
#             "branch": self.branch,
#             "cheque_no": self.name,
#             "accounts": [
#                 {
#                     "account": self.debit_to,
#                     "exchange_rate": flt(self.conversion_rate),
#                     "credit_in_account_currency": flt(taxes.tax_amount,currency_precision),
#                     "debit_in_account_currency": 0,
#                     "party_type": "Customer",
#                     "party": self.customer,
#                     "cost_center":self.cost_center,
#                     "reference_type": self.doctype,
#                     "reference_name": self.name,
# 					"branch":self.branch
#                 },
#                 {
#                     "account": company_gst_payable_account,
#                     "credit_in_account_currency": 0,
#                     "debit_in_account_currency": flt(taxes.tax_amount,currency_precision) * self.conversion_rate,
#                     "exchange_rate": 1,
#                     "cost_center":self.cost_center,
# 					"branch":self.branch
#                 },
#             ],
#         }
#     )
    
#     jv.save(ignore_permissions=True)
#     jv.submit()
#     meta = frappe.get_meta(self.doctype)
#     if meta.has_field("igst_refund_jv"):
#         self.db_set("igst_refund_jv", jv.name)
        


# def create_jv(self):
# 	if frappe.db.get_value('Address', self.customer_address, 'country') != "India":
# 		meta = frappe.get_meta(self.doctype)
# 		if meta.has_field('total_duty_drawback'):
# 			if self.total_duty_drawback:
# 				drawback_receivable_account = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_receivable_account")
# 				drawback_income_account = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_income_account")
# 				drawback_cost_center = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_cost_center")
# 				if not drawback_receivable_account:
# 					frappe.throw(_("Set Duty Drawback Receivable Account in Company"))
# 				elif not drawback_income_account:
# 					frappe.throw(_("Set Duty Drawback Income Account in Company"))
# 				elif not drawback_cost_center:
# 					frappe.throw(_("Set Duty Drawback Cost Center in Company"))
# 				else:
# 					jv = frappe.new_doc("Journal Entry")
# 					jv.voucher_type = "Duty Drawback Entry"
# 					jv.posting_date = self.posting_date
# 					jv.company = self.company
# 					jv.cheque_no = self.name
# 					jv.cheque_date = self.posting_date
# 					jv.user_remark = "Duty draw back against " + self.name + " for " + self.customer
# 					jv.append("accounts", {
# 						"account": drawback_receivable_account,
# 						"cost_center": drawback_cost_center,
# 						"debit_in_account_currency": self.total_duty_drawback,
# 						"branch":self.branch
# 					})
# 					jv.append("accounts", {
# 						"account": drawback_income_account,
# 						"cost_center": drawback_cost_center,
# 						"credit_in_account_currency": self.total_duty_drawback,
# 						"branch":self.branch
# 					})
# 					try:
# 						jv.save(ignore_permissions=True)
# 						jv.submit()
# 					except Exception as e:
# 						frappe.throw(str(e))
# 					else:
# 						meta = frappe.get_meta(self.doctype)
# 						if meta.has_field('duty_drawback_jv'):
# 							self.db_set('duty_drawback_jv',jv.name)

# 		if self.get('total_meis'):
# 			meis_receivable_account = frappe.db.get_value("Company", { "company_name": self.company}, "meis_receivable_account")
# 			meis_income_account = frappe.db.get_value("Company", { "company_name": self.company}, "meis_income_account")
# 			meis_cost_center = frappe.db.get_value("Company", { "company_name": self.company}, "meis_cost_center")
# 			if not meis_receivable_account:
# 				frappe.throw(_("Set RODTEP Receivable Account in Company"))
# 			elif not meis_income_account:
# 				frappe.throw(_("Set RODTEP Income Account in Company"))
# 			elif not meis_cost_center:
# 				frappe.throw(_("Set RODTEP Cost Center in Company"))
# 			else:
# 				meis_jv = frappe.new_doc("Journal Entry")
# 				meis_jv.voucher_type = "RODTEP Entry"
# 				meis_jv.posting_date = self.posting_date
# 				meis_jv.company = self.company
# 				meis_jv.cheque_no = self.name
# 				meis_jv.cheque_date = self.posting_date
# 				meis_jv.user_remark = "RODTEP against " + self.name + " for " + self.customer
# 				meis_jv.append("accounts", {
# 					"account": meis_receivable_account,
# 					"cost_center": meis_cost_center,
# 					"debit_in_account_currency": self.total_meis,
# 					"branch":self.branch
# 				})
# 				meis_jv.append("accounts", {
# 					"account": meis_income_account,
# 					"cost_center": meis_cost_center,
# 					"credit_in_account_currency": self.total_meis,
# 					"branch":self.branch
# 				})
				
# 				try:
# 					meis_jv.save(ignore_permissions=True)
# 					meis_jv.submit()
# 				except Exception as e:
# 					frappe.throw(str(e))
# 				else:
# 					self.db_set('meis_jv',meis_jv.name)



def is_branch_dimension_enabled():
    return frappe.db.exists(
        "Accounting Dimension",
        {
            "document_type": "Branch",
            "disabled": 0
        }
    )
def create_jv_with_gst(self):
    if not (self.get("is_export_with_gst") and self.get("taxes")):
        return

    branch_enabled = is_branch_dimension_enabled()

    taxes = self.get("taxes")[0]
    company_gst_payable_account = frappe.db.get_value(
        "Company", {"company_name": self.company}, "igst_export_refund_receivable"
    )

    currency_precision = frappe.get_precision(
        "Journal Entry Account", "debit_in_account_currency"
    )

    jv = frappe.get_doc(
        {
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": self.posting_date,
            "cheque_date": self.posting_date,
            "multi_currency": 1,
            "company": self.company,
            "company_gstin": self.company_gstin,
            "branch": self.branch if branch_enabled else None,

            "cheque_no": self.name,
            "accounts": [
                {
                    "account": self.debit_to,
                    "exchange_rate": flt(self.conversion_rate),
                    "credit_in_account_currency": flt(
                        taxes.tax_amount, currency_precision
                    ),
                    "debit_in_account_currency": 0,
                    "party_type": "Customer",
                    "party": self.customer,
                    "cost_center": self.cost_center,
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    **({"branch": self.branch} if branch_enabled else {}),

                },
                {
                    "account": company_gst_payable_account,
                    "credit_in_account_currency": 0,
                    "debit_in_account_currency": flt(
                        taxes.tax_amount, currency_precision
                    )
                    * self.conversion_rate,
                    "exchange_rate": 1,
                    "cost_center": self.cost_center,
                    **({"branch": self.branch} if branch_enabled else {}),

                },
            ],
        }
    )

    jv.save(ignore_permissions=True)
    jv.submit()

    meta = frappe.get_meta(self.doctype)
    if meta.has_field("igst_refund_jv"):
        self.db_set("igst_refund_jv", jv.name)
import frappe
from frappe import _
from frappe.utils import flt
# from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
# 	is_dimension_enabled,
# )

# def is_branch_dimension_enabled():
# 	return is_dimension_enabled("Branch")


# ---------------------------------------------------
# DUTY DRAWBACK RECEIVABLE (LESSER OF % vs CAP)
# ---------------------------------------------------
def get_duty_drawback_receivable(self):
	total = 0.0
	for row in self.items:
		if row.duty_drawback_amount and row.capped_amount:
			total += min(
				flt(row.duty_drawback_amount),
				flt(row.capped_amount),
			)
		else:
			total += flt(row.duty_drawback_amount or row.capped_amount or 0.0)
	return flt(total)


# ---------------------------------------------------
# RODTEP RECEIVABLE (LESSER OF % vs CAP)
# ---------------------------------------------------
def get_rodtep_receivable(self):
	total = 0.0
	for row in self.items:
		if row.meis_value and row.custom_rodtep_capped_amount:
			total += min(
				flt(row.meis_value),
				flt(row.custom_rodtep_capped_amount),
			)
		else:
			total += flt(row.meis_value or row.custom_rodtep_capped_amount or 0.0)
	return flt(total)


# ---------------------------------------------------
# CREATE JOURNAL ENTRIES
# ---------------------------------------------------
def create_jv(self):
	# Export only
	if frappe.db.get_value("Address", self.customer_address, "country") == "India":
		return

	branch_enabled = is_branch_dimension_enabled()
	meta = frappe.get_meta(self.doctype)

	# =================================================
	# DUTY DRAWBACK JV
	# =================================================
	if meta.has_field("total_duty_drawback") and not self.get("duty_drawback_jv"):
		duty_drawback_amount = get_duty_drawback_receivable(self)

		if duty_drawback_amount:
			drawback_receivable_account = frappe.db.get_value(
				"Company", self.company, "duty_drawback_receivable_account"
			)
			drawback_income_account = frappe.db.get_value(
				"Company", self.company, "duty_drawback_income_account"
			)
			drawback_cost_center = frappe.db.get_value(
				"Company", self.company, "duty_drawback_cost_center"
			)

			if not drawback_receivable_account:
				frappe.throw(_("Set Duty Drawback Receivable Account in Company"))
			if not drawback_income_account:
				frappe.throw(_("Set Duty Drawback Income Account in Company"))
			if not drawback_cost_center:
				frappe.throw(_("Set Duty Drawback Cost Center in Company"))

			jv = frappe.new_doc("Journal Entry")
			jv.voucher_type = "Duty Drawback Entry"
			jv.posting_date = self.posting_date
			jv.company = self.company
			jv.cheque_no = self.name
			jv.cheque_date = self.posting_date
			jv.user_remark = f"Duty Drawback against {self.name} for {self.customer}"

			jv.append(
				"accounts",
				{
					"account": drawback_receivable_account,
					"cost_center": drawback_cost_center,
					"debit_in_account_currency": duty_drawback_amount,
					**({"branch": self.branch} if branch_enabled else {}),
				},
			)

			jv.append(
				"accounts",
				{
					"account": drawback_income_account,
					"cost_center": drawback_cost_center,
					"credit_in_account_currency": duty_drawback_amount,
					**({"branch": self.branch} if branch_enabled else {}),
				},
			)

			jv.save(ignore_permissions=True)
			jv.submit()

			if meta.has_field("duty_drawback_jv"):
				self.db_set("duty_drawback_jv", jv.name)


	# =================================================
	# RODTEP / MEIS JV
	# =================================================
	if meta.has_field("total_meis") and not self.get("meis_jv"):
		rodtep_amount = get_rodtep_receivable(self)

		if rodtep_amount:
			meis_receivable_account = frappe.db.get_value(
				"Company", self.company, "meis_receivable_account"
			)
			meis_income_account = frappe.db.get_value(
				"Company", self.company, "meis_income_account"
			)
			meis_cost_center = frappe.db.get_value(
				"Company", self.company, "meis_cost_center"
			)

			if not meis_receivable_account:
				frappe.throw(_("Set RODTEP Receivable Account in Company"))
			if not meis_income_account:
				frappe.throw(_("Set RODTEP Income Account in Company"))
			if not meis_cost_center:
				frappe.throw(_("Set RODTEP Cost Center in Company"))

			meis_jv = frappe.new_doc("Journal Entry")
			meis_jv.voucher_type = "RODTEP Entry"
			meis_jv.posting_date = self.posting_date
			meis_jv.company = self.company
			meis_jv.cheque_no = self.name
			meis_jv.cheque_date = self.posting_date
			meis_jv.user_remark = f"RODTEP against {self.name} for {self.customer}"

			meis_jv.append(
				"accounts",
				{
					"account": meis_receivable_account,
					"cost_center": meis_cost_center,
					"debit_in_account_currency": rodtep_amount,
					**({"branch": self.branch} if branch_enabled else {}),
				},
			)

			meis_jv.append(
				"accounts",
				{
					"account": meis_income_account,
					"cost_center": meis_cost_center,
					"credit_in_account_currency": rodtep_amount,
					**({"branch": self.branch} if branch_enabled else {}),
				},
			)

			meis_jv.save(ignore_permissions=True)
			meis_jv.submit()

			self.db_set("meis_jv", meis_jv.name)

# def create_brc(self):
# 	if frappe.db.get_value('Address', self.customer_address, 'country') != "India" and frappe.db.exists("DocType", "BRC Management"):
# 		brc = frappe.new_doc("BRC Management")
# 		brc.invoice_no = self.name
# 		if not self.is_return and self.shipping_bill_number and self.shipping_bill_date and self.rounded_total:
# 			brc.append("shipping_bill_details", {
# 				"shipping_bill": self.shipping_bill_number,
# 				"shipping_date": self.shipping_bill_date,
# 				"shipping_bill_amount": self.rounded_total
# 			})
# 		brc.save(ignore_permissions=True)


def cancel_export_lic(self):
	doc_list = list(set([row.advance_authorisation_license for row in self.items if row.advance_authorisation_license]))

	for doc_name in doc_list:
		doc = frappe.get_doc("Advance Authorisation License", doc_name)
		to_remove = []

		for row in doc.exports:
			if row.parent == doc_name and row.sales_invoice == self.name:
				to_remove.append(row)

		[doc.remove(row) for row in to_remove]
		doc.total_export_qty = sum([flt(d.quantity) for d in doc.exports])
		doc.total_export_amount = sum([flt(d.fob_value) for d in doc.exports])
		doc.save()


def cancel_jv(self):
	meta = frappe.get_meta(self.doctype)
	if meta.has_field('duty_drawback_jv'):
		if self.duty_drawback_jv:
			jv = frappe.get_doc("Journal Entry", self.duty_drawback_jv)
			jv.cancel()
			self.db_set('duty_drawback_jv','')
	if meta.has_field('meis_jv'):
		if self.get('meis_jv'):
			jv = frappe.get_doc("Journal Entry", self.meis_jv)
			jv.cancel()
			self.db_set('meis_jv','')



# ---------------------------------------


def before_insert(doc, method):
    print('Before Insert..............................')
    if doc.get("items") and len(doc.items) > 0:
        so_name = doc.items[0].sales_order
        if so_name:
            copy_selected_producers(doc, so_name)



# def before_insert(doc, method):
#     print('before insert........................')
#     if doc.get("items") and len(doc.items) > 0:
#         so_name = doc.items[0].sales_order

#         if so_name:
#             # your existing function
#             copy_selected_producers(doc, so_name)

#             # fetch LC No from Contract Term
#             lc_no = frappe.db.get_value(
#                 "Contract Term",
#                 {"sales_order": so_name},
#                 "lc_no"
#             )

#             if lc_no:
#                 doc.custom_lc_no = lc_no



def copy_selected_producers(doc, sales_order):
    so = frappe.get_doc("Sales Order", sales_order)

    # Clear existing mapped producers
    doc.custom_producer_table = []

    for row in so.custom_producer_table:
        if row.selected:   # Only selected producers
            child = doc.append("custom_producer_table", {})
            child.producer = row.producer
            child.address = row.address
            child.selected = row.selected


# def before_save(doc, method):
#     """
#     Copy selected producers from Sales Order
#     ONLY once for NEW Sales Invoice
#     """

#     #  VERY IMPORTANT GUARD
#     if doc.custom_producer_table:
#         return

#     if doc.get("items") and len(doc.items) > 0:
#         so_name = doc.items[0].sales_order
#         if so_name:
#             copy_selected_producers(doc, so_name)


# def copy_selected_producers(doc, sales_order):
#     so = frappe.get_doc("Sales Order", sales_order)

#     # Clear existing mapped producers
#     doc.custom_producer_table = []

#     for row in so.custom_producer_table:
#         if row.selected:
#             child = doc.append("custom_producer_table", {})
#             child.producer = row.producer
#             child.address = row.address
#             child.selected = row.selected




# def before_workflow_action(doc, method=None):
#     all_checked = True

#     if doc.sales_invoice_contract_term_check:
#         for row in doc.sales_invoice_contract_term_check:
#             if not row.checked:
#                 all_checked = False
#                 break

#     if all_checked and doc.sales_invoice_export_document_item:
#         for row in doc.sales_invoice_export_document_item:
#             if not row.checked:
#                 all_checked = False
#                 break

#     if all_checked and doc.gst_category == "Overseas":
#         doc.workflow_state = "BL Issued"


def before_workflow_action(doc, method=None):
    all_checked = True

    if doc.sales_invoice_contract_term_check:
        for row in doc.sales_invoice_contract_term_check:
            if not row.checked:
                all_checked = False
                break

    if all_checked and doc.sales_invoice_export_document_item:
        for row in doc.sales_invoice_export_document_item:
            if not row.checked:
                all_checked = False
                break

    if doc.gst_category == "Overseas" and not all_checked:
        frappe.throw(
            "All Contract Terms and Export Document items must be checked before proceeding."
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






























# # ----------------------------------------------------------------------------------------
# # CONSOLIDATED SALES INVOICE
# # ----------------------------------------------------------------------------------
# @frappe.whitelist()
# def create_consolidated_invoice(sales_invoices):

#     if isinstance(sales_invoices, str):
#         sales_invoices = json.loads(sales_invoices)

#     if not sales_invoices:
#         frappe.throw("No Sales Invoices selected")

#     #  Check if any selected Sales Invoice is already consolidated
#     # Check if any selected Sales Invoice is already consolidated
#     # Check if any selected Sales Invoice is already used in Consolidated Sales Invoice
#     already_consolidated = []

#     for si_name in sales_invoices:
#         exists = frappe.db.exists(
#             "Sales Invoices",          # child table doctype
#             {"sales_invoice": si_name}
#         )
#         if exists:
#             already_consolidated.append(si_name)

#     if already_consolidated:
#         frappe.throw(
#             "The following Sales Invoices are already linked to a Consolidated Sales Invoice:<br><b>"
#             + ", ".join(already_consolidated)
#             + "</b>"
#         )


#     # lowest_si_name = min(sales_invoices)
#     # first_si = frappe.get_doc("Sales Invoice", sales_invoices[0])
#     lowest_si_name = min(sales_invoices)
#     first_si = frappe.get_doc("Sales Invoice", lowest_si_name)

#     sales_contracts = set()
#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         for item in si.items:
#             if item.sales_order:
#                 sales_contracts.add(item.sales_order)

#     if len(sales_contracts) > 1:
#         frappe.throw(
#             "Selected Sales Invoices contain items from different Sales Contracts. "
#             "Please select invoices belonging to the same Sales Contract."
#         )

#     sales_contract = list(sales_contracts)[0] if sales_contracts else None

#     if frappe.db.exists("Consolidated Sales Invoice", first_si.name):
#         frappe.throw(
#             f"Consolidated Sales Invoice with name '{first_si.name}' already exists"
#         )

#     csi = frappe.new_doc("Consolidated Sales Invoice")
#     csi.name = first_si.name

#     csi.customer = first_si.customer
#     # csi.is_consignee_same_as_buyer=first_si.custom_is_consignee_same_as_buyer
#     # csi.consignee=first_si.custom_consignee
#     csi.company = first_si.company
#     csi.currency = first_si.currency
#     csi.conversion_rate = first_si.conversion_rate
#     csi.debit_to = first_si.debit_to
#     csi.cost_center = first_si.cost_center
#     csi.project = first_si.project
#     csi.tax_category = first_si.tax_category
#     csi.shipping_rule = first_si.shipping_rule
#     csi.incoterm = first_si.incoterm
#     csi.taxes_and_charges = first_si.taxes_and_charges
#     csi.customer_address = first_si.customer_address
#     csi.address_display = first_si.address_display
#     csi.gst_category = first_si.gst_category
#     csi.contact_person = first_si.contact_person
#     csi.territory = first_si.territory
#     csi.shipping_address_name = first_si.shipping_address_name
#     csi.shipping_address = first_si.shipping_address
#     csi.dispatch_address_name = first_si.dispatch_address_name
#     csi.company_address = first_si.company_address
#     csi.company_address_display = first_si.company_address_display
#     csi.company_contact_person = first_si.company_contact_person
#     csi.tc_name = first_si.tc_name
#     csi.terms = first_si.terms
#     csi.update_stock = 1 if first_si.update_stock else 0
#     csi.set_warehouse = first_si.set_warehouse
#     csi.posting_date = today()

#     for si_name in sales_invoices:
#         csi.append("sales_invoice_reference", {
#         "sales_invoice": si_name
#     })
   

#     # =========================
#     # CONSOLIDATE ITEMS
#     # =========================
#     item_map = {}

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)

#         if si.docstatus != 1:
#             frappe.throw(f"{si.name} must be Submitted")

#         if si.is_consolidated:
#             frappe.db.set_value("Sales Invoice", si.name, "is_consolidated", 0)
#             si.is_consolidated = 0

#         if si.customer != csi.customer:
#             frappe.throw("All Sales Invoices must have the same Customer")

#         if si.company != csi.company:
#             frappe.throw("All Sales Invoices must belong to the same Company")

#         for item in si.items:
#             key = item.item_code

#             if key in item_map:
#                 item_map[key]["qty"] += flt(item.qty)
#                 item_map[key]["amount"] += flt(item.amount)
#                 item_map[key]["base_amount"] += flt(item.base_amount)
#                 item_map[key]["sales_orders"].add(item.sales_order)
#             else:
#                 item_map[key] = {
#                     "item_code": item.item_code,
#                     "item_name": item.item_name,
#                     "description": item.description,
#                     "qty": flt(item.qty),
#                     "uom": item.uom,
#                     "stock_uom": item.stock_uom,
#                     "conversion_factor": flt(item.conversion_factor) if item.conversion_factor else 1,
#                     "rate": flt(item.rate),
#                     "base_rate": flt(item.base_rate),
#                     "amount": flt(item.amount),
#                     "base_amount": flt(item.base_amount),
#                     "income_account": item.income_account,
#                     "cost_center": item.cost_center,
#                     "sales_orders": {item.sales_order}
#                 }

#     for row in item_map.values():
#         csi.append("items", {
#             "item_code": row["item_code"],
#             "item_name": row["item_name"],
#             "description": row["description"],
#             "qty": row["qty"],
#             "uom": row["uom"],
#             "stock_uom": row["stock_uom"],
#             "conversion_factor": row["conversion_factor"],
#             "rate": row["rate"],
#             "base_rate": row["base_rate"],
#             "amount": row["amount"],
#             "base_amount": row["base_amount"],
#             "income_account": row["income_account"],
#             "cost_center": row["cost_center"],
#             "sales_order": ", ".join(filter(None, row.get("sales_orders", [])))
#         })

#     # =========================
#     # APPLY TAXES TABLE LOGIC
#     # =========================
#     tax_map = {}

#     for tax in first_si.taxes:
#         key = (tax.account_head, tax.charge_type)
#         tax_map[key] = {
#             "charge_type": tax.charge_type,
#             "account_head": tax.account_head,
#             "description": tax.description,
#             "included_in_print_rate": tax.included_in_print_rate,
#             "cost_center": tax.cost_center,
#             "rate": flt(tax.rate),
#             "gst_tax_type": tax.gst_tax_type,
#             "tax_amount": 0,
#             "base_tax_amount": 0,
#             "total": 0,
#             "base_total": 0,
#             "tax_amount_after_discount_amount": 0,
#         }

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         for tax in si.taxes:
#             key = (tax.account_head, tax.charge_type)
#             if key in tax_map:
#                 tax_map[key]["tax_amount"] += flt(tax.tax_amount)
#                 tax_map[key]["base_tax_amount"] += flt(tax.base_tax_amount)
#                 tax_map[key]["total"] += flt(tax.total)
#                 tax_map[key]["base_total"] += flt(tax.base_total)
#                 tax_map[key]["tax_amount_after_discount_amount"] += flt(
#                     tax.tax_amount_after_discount_amount
#                 )

#     for row in tax_map.values():
#         csi.append("taxes", row)

#     # =========================
#     # MANUAL TOTALS (FROM SALES INVOICE HEADERS)
#     # =========================
#     total_qty = 0
#     net_total = 0
#     base_total = 0
#     total=0
#     grand_total = 0
#     base_grand_total = 0
#     base_total_taxes_and_charges=0
#     total_taxes_and_charges=0
#     outstanding_amount=0
#     base_net_total=0
#     net_total=0

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         total_qty += flt(si.total_qty)
#         # net_total += flt(si.net_total)
#         total+=flt(si.total)
#         base_total_taxes_and_charges+=flt(si.base_total_taxes_and_charges)
#         total_taxes_and_charges+=flt(si.total_taxes_and_charges)
#         base_total += flt(si.base_total)
#         grand_total += flt(si.grand_total)
#         base_grand_total += flt(si.base_grand_total)
#         outstanding_amount += flt(si.outstanding_amount)
#         # base_net_total += flt(si.base_net_total)
#         # net_total += flt(si.net_total)

        


        

#     csi.total_qty = total_qty
#     # csi.net_total = net_total
#     csi.base_total = base_total
#     csi.total=total
#     csi.base_total_taxes_and_charges=base_total_taxes_and_charges
#     csi.total_taxes_and_charges=total_taxes_and_charges
#     csi.grand_total = grand_total
#     csi.base_grand_total = base_grand_total
#     csi.sales_contract = sales_contract
#     csi.outstanding_amount = outstanding_amount
#     # csi.base_net_total = base_net_total
#     csi.net_total = net_total



#     csi.insert(ignore_permissions=True)
#     frappe.db.commit()
#     for si_name in sales_invoices:
#         frappe.db.set_value("Sales Invoice", si_name, "is_consolidated", 1)

#     frappe.msgprint(f"Consolidated Sales Invoice {csi.name} created successfully")

#     return csi





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
#         fields=["custom_consignee_name"]
#     )

#     # Return list of tuples (required for link field query)
#     return [(d.custom_consignee_name,) for d in addresses]






# @frappe.whitelist()
# def create_consolidated_invoice(sales_invoices):

#     if isinstance(sales_invoices, str):
#         sales_invoices = json.loads(sales_invoices)

#     if not sales_invoices:
#         frappe.throw("No Sales Invoices selected")

#     # ---------------------------------------------------------
#     # CHECK IF ANY SALES INVOICE IS ALREADY CONSOLIDATED
#     # ---------------------------------------------------------
#     already_consolidated = []

#     for si_name in sales_invoices:
#         exists = frappe.db.exists(
#             "Sales Invoices",     # child table doctype
#             {"sales_invoice": si_name}
#         )
#         if exists:
#             already_consolidated.append(si_name)

#     if already_consolidated:
#         frappe.throw(
#             "The following Sales Invoices are already linked to a Consolidated Sales Invoice:<br><b>"
#             + ", ".join(already_consolidated)
#             + "</b>"
#         )

#     # ---------------------------------------------------------
#     # PICK BASE SALES INVOICE
#     # ---------------------------------------------------------
#     lowest_si_name = min(sales_invoices)
#     first_si = frappe.get_doc("Sales Invoice", lowest_si_name)

#     # ---------------------------------------------------------
#     # ENSURE SINGLE SALES ORDER (SALES CONTRACT)
#     # ---------------------------------------------------------
#     sales_contracts = set()

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         for item in si.items:
#             if item.sales_order:
#                 sales_contracts.add(item.sales_order)

#     if len(sales_contracts) > 1:
#         frappe.throw(
#             "Selected Sales Invoices contain items from different Sales Contracts. "
#             "Please select invoices belonging to the same Sales Contract."
#         )

#     sales_contract = list(sales_contracts)[0] if sales_contracts else None

#     if frappe.db.exists("Consolidated Sales Invoice", first_si.name):
#         frappe.throw(
#             f"Consolidated Sales Invoice with name '{first_si.name}' already exists"
#         )

#     # ---------------------------------------------------------
#     # CREATE CONSOLIDATED SALES INVOICE
#     # ---------------------------------------------------------
#     csi = frappe.new_doc("Consolidated Sales Invoice")
#     csi.name = first_si.name

#     # Header mapping
#     csi.customer = first_si.customer
#     csi.company = first_si.company
#     csi.currency = first_si.currency
#     csi.conversion_rate = first_si.conversion_rate
#     csi.debit_to = first_si.debit_to
#     csi.cost_center = first_si.cost_center
#     csi.project = first_si.project
#     csi.tax_category = first_si.tax_category
#     csi.shipping_rule = first_si.shipping_rule
#     csi.incoterm = first_si.incoterm
#     csi.taxes_and_charges = first_si.taxes_and_charges
#     csi.customer_address = first_si.customer_address
#     csi.address_display = first_si.address_display
#     csi.gst_category = first_si.gst_category
#     csi.contact_person = first_si.contact_person
#     csi.territory = first_si.territory
#     csi.shipping_address_name = first_si.shipping_address_name
#     csi.shipping_address = first_si.shipping_address
#     csi.dispatch_address_name = first_si.dispatch_address_name
#     csi.company_address = first_si.company_address
#     csi.company_address_display = first_si.company_address_display
#     csi.company_contact_person = first_si.company_contact_person
#     csi.tc_name = first_si.tc_name
#     csi.terms = first_si.terms
#     csi.update_stock = 1 if first_si.update_stock else 0
#     csi.set_warehouse = first_si.set_warehouse
#     csi.posting_date = today()
#     csi.sales_contract = sales_contract

#     # ---------------------------------------------------------
#     # LINK SALES INVOICES
#     # ---------------------------------------------------------
#     for si_name in sales_invoices:
#         csi.append("sales_invoice_reference", {
#             "sales_invoice": si_name
#         })

#     # ---------------------------------------------------------
#     # FETCH PAYMENT TERMS FROM SALES ORDER
#     # ---------------------------------------------------------
#     if sales_contract:
#         so = frappe.get_doc("Sales Order", sales_contract)
#         csi.payment_terms_template = so.payment_terms_template

#         # Copy payment schedule
#         csi.set("payment_schedule", [])
#         for ps in so.payment_schedule:
#             csi.append("payment_schedule", {
#                 "payment_term": ps.payment_term,
#                 "description": ps.description,
#                 "due_date": ps.due_date,
#                 "invoice_portion": ps.invoice_portion,
#                 "payment_amount": ps.payment_amount,
#                 "base_payment_amount": ps.base_payment_amount,
#                 "discount_type": ps.discount_type,
#                 "discount": ps.discount,
#                 "discount_date": ps.discount_date
#             })

#     # ---------------------------------------------------------
#     # CONSOLIDATE ITEMS
#     # ---------------------------------------------------------
#     item_map = {}

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)

#         if si.docstatus != 1:
#             frappe.throw(f"{si.name} must be Submitted")

#         if si.customer != csi.customer:
#             frappe.throw("All Sales Invoices must have the same Customer")

#         if si.company != csi.company:
#             frappe.throw("All Sales Invoices must belong to the same Company")

#         for item in si.items:
#             key = item.item_code

#             if key in item_map:
#                 item_map[key]["qty"] += flt(item.qty)
#                 item_map[key]["amount"] += flt(item.amount)
#                 item_map[key]["base_amount"] += flt(item.base_amount)
#                 item_map[key]["sales_orders"].add(item.sales_order)
#             else:
#                 item_map[key] = {
#                     "item_code": item.item_code,
#                     "item_name": item.item_name,
#                     "description": item.description,
#                     "qty": flt(item.qty),
#                     "uom": item.uom,
#                     "stock_uom": item.stock_uom,
#                     "conversion_factor": flt(item.conversion_factor) or 1,
#                     "rate": flt(item.rate),
#                     "base_rate": flt(item.base_rate),
#                     "amount": flt(item.amount),
#                     "base_amount": flt(item.base_amount),
#                     "income_account": item.income_account,
#                     "cost_center": item.cost_center,
#                     "sales_orders": {item.sales_order}
#                 }

#     for row in item_map.values():
#         csi.append("items", {
#             "item_code": row["item_code"],
#             "item_name": row["item_name"],
#             "description": row["description"],
#             "qty": row["qty"],
#             "uom": row["uom"],
#             "stock_uom": row["stock_uom"],
#             "conversion_factor": row["conversion_factor"],
#             "rate": row["rate"],
#             "base_rate": row["base_rate"],
#             "amount": row["amount"],
#             "base_amount": row["base_amount"],
#             "income_account": row["income_account"],
#             "cost_center": row["cost_center"],
#             "sales_order": ", ".join(filter(None, row["sales_orders"]))
#         })

#     # ---------------------------------------------------------
#     # TAX CONSOLIDATION
#     # ---------------------------------------------------------
#     tax_map = {}

#     for tax in first_si.taxes:
#         key = (tax.account_head, tax.charge_type)
#         tax_map[key] = {
#             "charge_type": tax.charge_type,
#             "account_head": tax.account_head,
#             "description": tax.description,
#             "included_in_print_rate": tax.included_in_print_rate,
#             "cost_center": tax.cost_center,
#             "rate": flt(tax.rate),
#             "gst_tax_type": tax.gst_tax_type,
#             "tax_amount": 0,
#             "base_tax_amount": 0,
#             "total": 0,
#             "base_total": 0,
#             "tax_amount_after_discount_amount": 0,
#         }

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         for tax in si.taxes:
#             key = (tax.account_head, tax.charge_type)
#             if key in tax_map:
#                 tax_map[key]["tax_amount"] += flt(tax.tax_amount)
#                 tax_map[key]["base_tax_amount"] += flt(tax.base_tax_amount)
#                 tax_map[key]["total"] += flt(tax.total)
#                 tax_map[key]["base_total"] += flt(tax.base_total)
#                 tax_map[key]["tax_amount_after_discount_amount"] += flt(
#                     tax.tax_amount_after_discount_amount
#                 )

#     for row in tax_map.values():
#         csi.append("taxes", row)

#     # ---------------------------------------------------------
#     # MANUAL TOTALS
#     # ---------------------------------------------------------
#     total_qty = 0
#     base_total = 0
#     total = 0
#     grand_total = 0
#     base_grand_total = 0
#     base_total_taxes_and_charges = 0
#     total_taxes_and_charges = 0
#     outstanding_amount = 0

#     for si_name in sales_invoices:
#         si = frappe.get_doc("Sales Invoice", si_name)
#         total_qty += flt(si.total_qty)
#         total += flt(si.total)
#         base_total += flt(si.base_total)
#         grand_total += flt(si.grand_total)
#         base_grand_total += flt(si.base_grand_total)
#         base_total_taxes_and_charges += flt(si.base_total_taxes_and_charges)
#         total_taxes_and_charges += flt(si.total_taxes_and_charges)
#         outstanding_amount += flt(si.outstanding_amount)

#     csi.total_qty = total_qty
#     csi.base_total = base_total
#     csi.total = total
#     csi.grand_total = grand_total
#     csi.base_grand_total = base_grand_total
#     csi.base_total_taxes_and_charges = base_total_taxes_and_charges
#     csi.total_taxes_and_charges = total_taxes_and_charges
#     csi.outstanding_amount = outstanding_amount

#     # ---------------------------------------------------------
#     # SAVE
#     # ---------------------------------------------------------
#     csi.insert(ignore_permissions=True)
#     frappe.db.commit()

#     for si_name in sales_invoices:
#         frappe.db.set_value("Sales Invoice", si_name, "is_consolidated", 1)

#     frappe.msgprint(f"Consolidated Sales Invoice {csi.name} created successfully")

#     return csi











# -----------------------------------------------------------------------------------------------------------
#    SPLIT SALES INVOICE
# ------------------------------------------------------------------------------------------------------


# import frappe
# from frappe.utils import flt, money_in_words
# import string

# @frappe.whitelist()
# def split_sales_invoice(sales_invoice, split_count):
#     source_doc = frappe.get_doc("Sales Invoice", sales_invoice)
#     split_count = int(split_count)

#     if split_count <= 0:
#         frappe.throw("Split count must be at least 1")

#     if source_doc.docstatus != 1:
#         frappe.throw("Only submitted Sales Invoices can be split")

    # target_meta = frappe.get_meta("Split Sales Invoice")
    # suffixes = list(string.ascii_uppercase)
    # new_records = []
    
    # container_rows = source_doc.get("container_detail") or []
    # total_rows = len(container_rows)
    
    # # Calculate how many container rows per split
    # rows_per_split = total_rows // split_count

    # for i in range(split_count):
    #     if i >= len(suffixes): break 
        
    #     new_split_doc = frappe.new_doc("Split Sales Invoice")
        
    #     # --- NAMING ---
    #     suffix = suffixes[i]
    #     name_parts = source_doc.name.split("-")
    #     if len(name_parts) >= 2:
    #         name_parts[1] = f"{name_parts[1]}{suffix}"
    #     else:
    #         name_parts[0] = f"{name_parts[0]}{suffix}"
    #     new_split_doc.name = "-".join(name_parts)

    #     new_split_doc.sales_invoice_reference = source_doc.name

#         # --- COPY PARENT FIELDS & SPLIT TOTALS ---
#         fields_to_divide = [
#             "total_qty", "total", "grand_total", "net_total", 
#             "outstanding_amount", "base_total", "base_net_total", 
#             "total_net_weight", "base_grand_total","total_packages"
#         ]
        
#         # Added number_of_containers to exclude list to recalculate it manually
#         exclude_fields = [
#             "name", "docstatus", "items", "container_detail", 
#             "amended_from", "base_in_words", "in_words", "number_of_containers"
#         ]

#         for field in target_meta.fields:
#             fname = field.fieldname
#             if source_doc.get(fname) and fname not in exclude_fields:
#                 val = source_doc.get(fname)
#                 new_split_doc.set(fname, flt(val) / split_count if fname in fields_to_divide else val)

#         # --- UPDATE TOTALS IN WORDS ---
#         if target_meta.has_field("base_in_words") and new_split_doc.base_grand_total:
#             company_currency = frappe.get_cached_value('Company', source_doc.company, 'default_currency')
#             new_split_doc.base_in_words = money_in_words(new_split_doc.base_grand_total, company_currency)

#         if target_meta.has_field("in_words") and new_split_doc.grand_total:
#             new_split_doc.in_words = money_in_words(new_split_doc.grand_total, source_doc.currency)

#         # --- COPY ITEMS (Divided Qty) ---
#         for item in source_doc.items:
#             new_item = new_split_doc.append("items", {})
#             new_item.update(item.as_dict())
#             new_item.name = None 
#             new_item.qty = flt(item.qty) / split_count
#             new_item.amount = flt(new_item.qty) * flt(new_item.rate)

#         # --- DISTRIBUTE CONTAINER DETAILS ---
#         start_idx = i * rows_per_split
        
#         # Grab remaining rows for the last split to handle uneven division
#         if i == split_count - 1:
#             current_batch = container_rows[start_idx:]
#         else:
#             end_idx = start_idx + rows_per_split
#             current_batch = container_rows[start_idx:end_idx]

#         for row in current_batch:
#             new_row = new_split_doc.append("container_detail", {})
#             new_row.update(row.as_dict())
#             new_row.name = None 

#         # --- UPDATE NUMBER OF CONTAINERS ---
#         # Set the field based on the count of rows actually added to this split
#         new_split_doc.number_of_containers = len(current_batch)

#         new_split_doc.insert(ignore_permissions=True)
#         new_records.append(new_split_doc.name)

#     return new_records


# import frappe
# from frappe.utils import flt, money_in_words
# import string

# @frappe.whitelist()
# def split_sales_invoice(sales_invoice, split_count):
#     source_doc = frappe.get_doc("Sales Invoice", sales_invoice)
#     split_count = int(split_count)

#     if split_count <= 0:
#         frappe.throw("Split count must be at least 1")

#     if source_doc.docstatus != 1:
#         frappe.throw("Only submitted Sales Invoices can be split")

#     target_meta = frappe.get_meta("Split Sales Invoice")
#     suffixes = list(string.ascii_uppercase)
#     new_records = []
    
#     container_rows = source_doc.get("container_detail") or []
#     total_rows = len(container_rows)
#     rows_per_split = total_rows // split_count

#     # Fields that need to be divided by the split count
#     fields_to_divide = [
#         "total_qty", "total", "grand_total", "net_total", 
#         "outstanding_amount", "base_total", "base_net_total", 
#         "total_net_weight", "base_grand_total", "total_packages"
#     ]

#     # Fields to completely ignore during the copy loop
#     # We add "status" here to avoid the "Completed Shipment" error
#     exclude_fields = [
#         "name", "docstatus", "items", "container_detail", 
#         "amended_from", "base_in_words", "in_words", 
#         "number_of_containers", "status"
#     ]

#     for i in range(split_count):
#         if i >= len(suffixes): break 
        
#         new_split_doc = frappe.new_doc("Split Sales Invoice")
        
#         # --- NAMING ---
#         suffix = suffixes[i]
#         name_parts = source_doc.name.split("-")
#         if len(name_parts) >= 2:
#             name_parts[1] = f"{name_parts[1]}{suffix}"
#         else:
#             name_parts[0] = f"{name_parts[0]}{suffix}"
#         new_split_doc.name = "-".join(name_parts)
#         new_split_doc.sales_invoice_reference = source_doc.name

#         # --- COPY PARENT FIELDS & SPLIT TOTALS ---
#         for field in target_meta.fields:
#             fname = field.fieldname
#             if source_doc.get(fname) and fname not in exclude_fields:
#                 val = source_doc.get(fname)
#                 if fname in fields_to_divide:
#                     # Logic: Divide value, but on the last split, take the remainder 
#                     # to ensure totals match the source exactly.
#                     divided_val = flt(val) / split_count
#                     if i == split_count - 1:
#                         new_split_doc.set(fname, flt(val) - (flt(divided_val) * (split_count - 1)))
#                     else:
#                         new_split_doc.set(fname, divided_val)
#                 else:
#                     new_split_doc.set(fname, val)

#         # --- FIX STATUS ERROR ---
#         # Explicitly set status to a value allowed by your "Split Sales Invoice" DocType
#         new_split_doc.status = "Draft"

#         # --- UPDATE TOTALS IN WORDS ---
#         company_currency = frappe.get_cached_value('Company', source_doc.company, 'default_currency')
#         if target_meta.has_field("base_in_words") and new_split_doc.base_grand_total:
#             new_split_doc.base_in_words = money_in_words(new_split_doc.base_grand_total, company_currency)

#         if target_meta.has_field("in_words") and new_split_doc.grand_total:
#             new_split_doc.in_words = money_in_words(new_split_doc.grand_total, source_doc.currency)

#         # --- COPY ITEMS (Divided Qty) ---
#         for item in source_doc.items:
#             new_item = new_split_doc.append("items", {})
#             new_item.update(item.as_dict())
#             new_item.name = None 
            
#             # Item qty handling with remainder for the last split
#             divided_qty = flt(item.qty) / split_count
#             if i == split_count - 1:
#                 new_item.qty = flt(item.qty) - (flt(divided_qty) * (split_count - 1))
#             else:
#                 new_item.qty = divided_qty
                
#             new_item.amount = flt(new_item.qty) * flt(new_item.rate)

#         # --- DISTRIBUTE CONTAINER DETAILS ---
#         start_idx = i * rows_per_split
#         if i == split_count - 1:
#             current_batch = container_rows[start_idx:]
#         else:
#             end_idx = start_idx + rows_per_split
#             current_batch = container_rows[start_idx:end_idx]

#         for row in current_batch:
#             new_row = new_split_doc.append("container_detail", {})
#             new_row.update(row.as_dict())
#             new_row.name = None 

#         new_split_doc.number_of_containers = len(current_batch)

#         # Use set_new_name() if you want Frappe to handle naming, 
#         # but since you're overriding .name, insert will respect it.
#         new_split_doc.insert(ignore_permissions=True)
#         new_records.append(new_split_doc.name)

#     return new_records



# import frappe
# from frappe.utils import flt, money_in_words
# import string

# @frappe.whitelist()
# def split_sales_invoice(sales_invoice, split_count):
#     # Fetch source document
#     source_doc = frappe.get_doc("Sales Invoice", sales_invoice)
#     split_count = int(split_count)

#     # --- VALIDATIONS ---
#     if split_count <= 1:
#         frappe.throw("Split count must be at least 2")

#     if source_doc.custom_loading_point != "MUNDRA":
#         frappe.throw("Splitting is only allowed for invoices with Loading Point: MUNDRA")

#     target_meta = frappe.get_meta("Split Sales Invoice")
#     suffixes = list(string.ascii_uppercase)
#     new_records = []
    
#     container_rows = source_doc.get("container_detail") or []
#     total_rows = len(container_rows)
#     rows_per_split = total_rows // split_count

#     # Fields that need to be mathematically divided
#     fields_to_divide = [
#         "total_qty", "total", "grand_total", "net_total", 
#         "outstanding_amount", "base_total", "base_net_total", 
#         "total_net_weight", "base_grand_total", "total_packages"
#     ]

#     # Fields to exclude from the automatic copy loop
#     exclude_fields = [
#         "name", "docstatus", "items", "container_detail", 
#         "amended_from", "base_in_words", "in_words", 
#         "number_of_containers", "status"
#     ]

#     for i in range(split_count):
#         if i >= len(suffixes): break 
        
#         new_split_doc = frappe.new_doc("Split Sales Invoice")
        
#         # --- CUSTOM NAMING LOGIC ---
#         suffix = suffixes[i]
#         name_parts = source_doc.name.split("-")
#         if len(name_parts) >= 2:
#             name_parts[1] = f"{name_parts[1]}{suffix}"
#         else:
#             name_parts[0] = f"{name_parts[0]}{suffix}"
        
#         new_split_doc.name = "-".join(name_parts)
#         new_split_doc.sales_invoice_reference = source_doc.name

#         # --- COPY PARENT FIELDS & SPLIT TOTALS ---
#         for field in target_meta.fields:
#             fname = field.fieldname
#             if source_doc.get(fname) and fname not in exclude_fields:
#                 val = source_doc.get(fname)
#                 if fname in fields_to_divide:
#                     # Logic: Divide value, but on the last split, take the remainder 
#                     divided_val = flt(val) / split_count
#                     if i == split_count - 1:
#                         remainder = flt(val) - (flt(divided_val) * (split_count - 1))
#                         new_split_doc.set(fname, remainder)
#                     else:
#                         new_split_doc.set(fname, divided_val)
#                 else:
#                     new_split_doc.set(fname, val)

#         # Ensure status is Draft for the new record
#         new_split_doc.status = "Draft"

#         # --- RE-GENERATE CURRENCY IN WORDS ---
#         company_currency = frappe.get_cached_value('Company', source_doc.company, 'default_currency')
#         if target_meta.has_field("base_in_words") and new_split_doc.base_grand_total:
#             new_split_doc.base_in_words = money_in_words(new_split_doc.base_grand_total, company_currency)

#         if target_meta.has_field("in_words") and new_split_doc.grand_total:
#             new_split_doc.in_words = money_in_words(new_split_doc.grand_total, source_doc.currency)

#         # --- COPY ITEMS & DIVIDE QUANTITIES ---
#         for item in source_doc.items:
#             new_item = new_split_doc.append("items", {})
#             new_item.update(item.as_dict())
#             new_item.name = None 
            
#             divided_qty = flt(item.qty) / split_count
#             if i == split_count - 1:
#                 new_item.qty = flt(item.qty) - (flt(divided_qty) * (split_count - 1))
#             else:
#                 new_item.qty = divided_qty
                
#             new_item.amount = flt(new_item.qty) * flt(new_item.rate)

#         # --- DISTRIBUTE CONTAINER DETAILS ROWS ---
#         start_idx = i * rows_per_split
#         if i == split_count - 1:
#             current_batch = container_rows[start_idx:]
#         else:
#             end_idx = start_idx + rows_per_split
#             current_batch = container_rows[start_idx:end_idx]

#         for row in current_batch:
#             new_row = new_split_doc.append("container_detail", {})
#             new_row.update(row.as_dict())
#             new_row.name = None 

#         new_split_doc.number_of_containers = len(current_batch)

#         # Insert into database
#         new_split_doc.insert(ignore_permissions=True)
#         new_records.append(new_split_doc.name)

#     return new_records



# import frappe


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
#         fields=["custom_consignee_name"]
#     )

#     # Return list of tuples (required for link field query)
#     return [(d.custom_consignee_name,) for d in addresses]




# @frappe.whitelist()
# def get_customer_billing_address(customer):
#     """
#     Returns the primary billing address of a Customer.
#     """
#     # Get address linked to this customer
#     address = frappe.db.sql("""
#         SELECT a.name
#         FROM `tabAddress` a
#         JOIN `tabDynamic Link` dl
#             ON dl.parent = a.name
#         WHERE dl.link_doctype = 'Customer'
#           AND dl.link_name = %s
#           AND a.is_primary_address = 1
#         LIMIT 1
#     """, customer, as_dict=True)

#     if address:
#         return address[0].name
#     return None







# @frappe.whitelist()
# def get_billing_address_for_customer(customer):
#     """
#     Returns a valid Billing Address linked to the selected customer.
#     """

#     if not customer:
#         return None

#     # Find billing address linked to this customer
#     address = frappe.db.sql("""
#         SELECT a.name
#         FROM `tabAddress` a
#         INNER JOIN `tabDynamic Link` dl
#             ON dl.parent = a.name
#         WHERE dl.link_doctype = 'Customer'
#           AND dl.link_name = %s
#           AND a.disabled = 0
#           AND (
#                 a.address_type = 'Billing'
#                 OR a.is_primary_address = 1
#           )
#         ORDER BY
#             a.is_primary_address DESC,
#             a.modified DESC
#         LIMIT 1
#     """, (customer,), as_dict=True)

#     return address[0].name if address else None




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

















# import frappe


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



# ------------------------------------------------------- corrected code -----------------------------------------------------

# import frappe
# from frappe import _

# @frappe.whitelist()
# def map_buyer_to_consignee_address_si(buyer, consignee):


#     if not buyer or not consignee:
#         frappe.throw(_("Buyer and Consignee are required"))

#     # -----------------------------------
#     # 1. GET CONSIGNEE ADDRESS (SHIPPING)
#     # -----------------------------------
#     addresses = frappe.db.sql("""
#         SELECT parent
#         FROM `tabDynamic Link`
#         WHERE link_name = %s
#         AND parenttype = 'Address'
#     """, (consignee,), as_dict=True)

#     if not addresses:
#         frappe.throw(_("No Address found linked to Consignee: {0}").format(consignee))

#     shipping_address = None

#     for row in addresses:
#         address_doc = frappe.get_doc("Address", row.parent)

#         updated = False

#         for link in address_doc.links:
#             if link.link_name == consignee:

#                 # ✅ AUTO-CHECK CONSIGNEE
#                 if not getattr(link, "custom_is_consignee", 0):
#                     link.custom_is_consignee = 1
#                     updated = True

#                 shipping_address = address_doc

#         if updated:
#             address_doc.save(ignore_permissions=True)

#         if shipping_address:
#             break

#     # -----------------------------------
#     # 2. GET BUYER ADDRESS (BILLING)
#     # -----------------------------------
#     buyer_addresses = frappe.db.sql("""
#         SELECT parent
#         FROM `tabDynamic Link`
#         WHERE link_name = %s
#         AND parenttype = 'Address'
#     """, (buyer,), as_dict=True)

#     if not buyer_addresses:
#         frappe.throw(_("No Address found for Buyer: {0}").format(buyer))

#     billing_address = frappe.get_doc("Address", buyer_addresses[0].parent)

#     # -----------------------------------
#     # 3. RETURN
#     # -----------------------------------
#     return {
#         "shipping_address_name": shipping_address.name,
#         "shipping_address": shipping_address.get_display(),
#         "customer_address": billing_address.name,
#         "address_display": billing_address.get_display()
#     }



import frappe
from frappe import _

@frappe.whitelist()
def map_buyer_to_consignee_address_si(buyer, consignee):

    if not buyer or not consignee:
        frappe.throw(_("Buyer and Consignee are required"))

    # -----------------------------------
    # 1. GET CONSIGNEE ADDRESS (SHIPPING)
    # -----------------------------------
    addresses = frappe.db.sql("""
        SELECT parent
        FROM `tabDynamic Link`
        WHERE link_name = %s
        AND parenttype = 'Address'
    """, (consignee,), as_dict=True)

    if not addresses:
        frappe.throw(_("No Address found linked to Consignee: {0}").format(consignee))

    shipping_address = None

    for row in addresses:
        address_doc = frappe.get_doc("Address", row.parent)

        updated = False
        buyer_link_exists = False

        for link in address_doc.links:

            # 👉 Identify consignee row
            if link.link_name == consignee:

                # ✅ AUTO-CHECK CONSIGNEE
                if not getattr(link, "custom_is_consignee", 0):
                    link.custom_is_consignee = 1
                    updated = True

                shipping_address = address_doc

            # 👉 Check if Buyer already exists
            if link.link_doctype == "Customer" and link.link_name == buyer:
                buyer_link_exists = True

        # 👉 ADD BUYER INTO LINKS TABLE (IMPORTANT)
        if shipping_address and not buyer_link_exists:
            address_doc.append("links", {
                "link_doctype": "Customer",
                "link_name": buyer
            })
            updated = True

        if updated:
            address_doc.save(ignore_permissions=True)

        if shipping_address:
            break

    if not shipping_address:
        frappe.throw(_("No valid shipping address found for Consignee"))

    # -----------------------------------
    # 2. GET BUYER ADDRESS (BILLING)
    # -----------------------------------
    buyer_addresses = frappe.db.sql("""
        SELECT parent
        FROM `tabDynamic Link`
        WHERE link_name = %s
        AND parenttype = 'Address'
    """, (buyer,), as_dict=True)

    if not buyer_addresses:
        frappe.throw(_("No Address found for Buyer: {0}").format(buyer))

    billing_address = frappe.get_doc("Address", buyer_addresses[0].parent)

    # -----------------------------------
    # 3. RETURN
    # -----------------------------------
    return {
        "shipping_address_name": shipping_address.name,
        "shipping_address": shipping_address.get_display(),
        "customer_address": billing_address.name,
        "address_display": billing_address.get_display()
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
#     """, (customer,), as_dict=True)

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




#     return address[0].name if address else None

# ---------------------------------------------------------
# GET COMMON FIELDS BETWEEN SALES INVOICES
# ---------------------------------------------------------

def get_shared_fields():
    meta = frappe.get_meta("Sales Invoice")

    excluded = {
        "name",
        "owner",
        "creation",
        "modified",
        "modified_by",
        "idx"
    }

    return [
        df.fieldname
        for df in meta.fields
        if df.fieldtype not in ["Table", "Section Break", "Column Break"]
        and df.fieldname not in excluded
    ]


def on_cancel(doc, method=None):

    if not doc.custom_consolidated_invoice_reference:
        return

    frappe.db.set_value(
        "Consolidated Sales Invoice",
        doc.custom_consolidated_invoice_reference,
        "workflow_state",
        "Cancelled"
    )
