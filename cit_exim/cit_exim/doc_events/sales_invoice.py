import frappe
from frappe import _
from frappe.utils import flt

from frappe.model.document import Document
import json
from frappe.utils import today
import calendar
from datetime import date



def before_save(self, method):
	calculate_total(self)
	duty_calculation(self)
	meis_calculation(self)

def validate(doc, method=None):
    lot_list = []

    for item in doc.items:
        if item.serial_and_batch_bundle:
            bundle = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
            for entry in bundle.entries:
                if entry.batch_no:
                    lot_list.append({"lot_no": entry.batch_no})

    existing_lots = {row.lot_no for row in doc.container_detail}

    for lot in lot_list:
        if lot["lot_no"] not in existing_lots:
            item_code = doc.items[0].item_code if doc.items else None
            packages = frappe.db.get_value(
                "Item", item_code, "custom_no_of_packages_per_lot"
            ) if item_code else None

            doc.append("container_detail", {
                "lot_no": lot["lot_no"],
                "no_of_packages": packages
            })

    # Optional: handle submit-time transition
    if doc.docstatus == 1:
        _handle_custom_status_change(doc)

def on_update_after_submit(doc, method=None):
    _handle_custom_status_change(doc)
    
def _handle_custom_status_change(doc):
    old_doc = doc.get_doc_before_save()
    old_status = old_doc.custom_work_flow_status if old_doc else None
    new_status = doc.custom_work_flow_status

    if old_status != "Completed Shipment" and new_status == "Completed Shipment":
        update_sales_contract_from_invoice(doc)


def update_sales_contract_from_invoice(sales_invoice):
 
    for si_item in sales_invoice.items:
        if not si_item.sales_order:
            continue

        sales_contract = frappe.get_doc("Sales Order", si_item.sales_order)

        if sales_contract.docstatus != 1:
            continue

        recalculate_shipment_schedule(
            sales_contract,
            si_item.item_code,
            sales_invoice.posting_date
        )

        sales_contract.save(ignore_permissions=True)
    

def recalculate_shipment_schedule(sales_contract, item_code, posting_date):
    month_name = posting_date.strftime("%B")
    fiscal_year = posting_date.year

    for row in sales_contract.custom_shipment_schedule:
        if row.month == "Prompt":

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
            """, (
                item_code,
                sales_contract.name
            ))[0][0] or 0

            completed_qty = flt(completed_qty)

            if completed_qty >= row.planned_qty:
                row.status = "Completed"
            elif completed_qty > 0:
                row.status = "In-Process"
            else:
                row.status = None

            continue
        
        if row.month != month_name or int(row.fiscal_year) != fiscal_year:
            continue

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
                AND MONTH(si.posting_date) = %s
                AND YEAR(si.posting_date) = %s
        """, (
            item_code,
            sales_contract.name,
            posting_date.month,
            posting_date.year
        ))[0][0] or 0

        completed_qty = flt(completed_qty)
        if completed_qty >= row.planned_qty:
            row.status = "Completed"
        elif completed_qty > 0:
            row.status = "In-Process"
        elif completed_qty == 0:
            row.status = None

def get_month_date_range(month_name, year):
    month_number = list(calendar.month_name).index(month_name)
    start_date = date(year, month_number, 1)
    last_day = calendar.monthrange(year, month_number)[1]
    end_date = date(year, month_number, last_day)
    return start_date, end_date

# ------------------------------------------------------------------------------------------------------------------------

def before_submit(self,method):
	# if self._action == 'submit':
	print(222222222222)
	# validate_document_checks(self)
	before_workflow_action(self)


def on_submit(self, method):
	export_lic(self)
	create_jv(self)
	create_brc(self)
	create_jv_with_gst(self)


def on_cancel(self, method):
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
			if child_meta.has_field('duty_drawback_rate') and row.duty_drawback_rate and row.fob_value:
				duty_drawback_amount = flt(row.fob_value * row.duty_drawback_rate / 100.0)
				if child_meta.has_field('duty_drawback_amount'):
					if row.maximum_cap == 1:
						if row.capped_amount < duty_drawback_amount:
							row.duty_drawback_amount = row.capped_amount
							row.effective_rate = flt(row.capped_amount / row.fob_value * 100.0)
						else:
							row.duty_drawback_amount = duty_drawback_amount
							row.effective_rate = row.duty_drawback_rate
					else:
						row.duty_drawback_amount = duty_drawback_amount

			row.igst_taxable_value = flt(row.amount)
			if child_meta.has_field('duty_drawback_amount'):
				total_duty_drawback += flt(row.duty_drawback_amount) or 0.0

		self.total_duty_drawback = total_duty_drawback


def meis_calculation(self):
	if frappe.db.get_value('Address', self.customer_address, 'country') != "India":
		total_meis = 0.0
		for row in self.items:
			if row.fob_value and row.meis_rate:
				meis_value = flt(row.fob_value * row.meis_rate / 100.0)
				row.meis_value = meis_value

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
def create_jv(self):
    if frappe.db.get_value("Address", self.customer_address, "country") != "India":
        branch_enabled = is_branch_dimension_enabled()

        meta = frappe.get_meta(self.doctype)

        # ================= DUTY DRAWBACK =================
        if meta.has_field("total_duty_drawback"):
            if self.total_duty_drawback:
                drawback_receivable_account = frappe.db.get_value(
                    "Company",
                    {"company_name": self.company},
                    "duty_drawback_receivable_account",
                )
                drawback_income_account = frappe.db.get_value(
                    "Company",
                    {"company_name": self.company},
                    "duty_drawback_income_account",
                )
                drawback_cost_center = frappe.db.get_value(
                    "Company",
                    {"company_name": self.company},
                    "duty_drawback_cost_center",
                )

                if not drawback_receivable_account:
                    frappe.throw(_("Set Duty Drawback Receivable Account in Company"))
                elif not drawback_income_account:
                    frappe.throw(_("Set Duty Drawback Income Account in Company"))
                elif not drawback_cost_center:
                    frappe.throw(_("Set Duty Drawback Cost Center in Company"))
                else:
                    jv = frappe.new_doc("Journal Entry")
                    jv.voucher_type = "Duty Drawback Entry"
                    jv.posting_date = self.posting_date
                    jv.company = self.company
                    jv.cheque_no = self.name
                    jv.cheque_date = self.posting_date
                    jv.user_remark = (
                        "Duty draw back against " + self.name + " for " + self.customer
                    )

                    jv.append(
                        "accounts",
                        {
                            "account": drawback_receivable_account,
                            "cost_center": drawback_cost_center,
                            "debit_in_account_currency": self.total_duty_drawback,
                            **({"branch": self.branch} if branch_enabled else {}),

                        },
                    )

                    jv.append(
                        "accounts",
                        {
                            "account": drawback_income_account,
                            "cost_center": drawback_cost_center,
                            "credit_in_account_currency": self.total_duty_drawback,
                            **({"branch": self.branch} if branch_enabled else {}),

                        },
                    )

                    try:
                        jv.save(ignore_permissions=True)
                        jv.submit()
                    except Exception as e:
                        frappe.throw(str(e))
                    else:
                        if meta.has_field("duty_drawback_jv"):
                            self.db_set("duty_drawback_jv", jv.name)

        # ================= RODTEP / MEIS =================
        if self.get("total_meis"):
            meis_receivable_account = frappe.db.get_value(
                "Company", {"company_name": self.company}, "meis_receivable_account"
            )
            meis_income_account = frappe.db.get_value(
                "Company", {"company_name": self.company}, "meis_income_account"
            )
            meis_cost_center = frappe.db.get_value(
                "Company", {"company_name": self.company}, "meis_cost_center"
            )

            if not meis_receivable_account:
                frappe.throw(_("Set RODTEP Receivable Account in Company"))
            elif not meis_income_account:
                frappe.throw(_("Set RODTEP Income Account in Company"))
            elif not meis_cost_center:
                frappe.throw(_("Set RODTEP Cost Center in Company"))
            else:
                meis_jv = frappe.new_doc("Journal Entry")
                meis_jv.voucher_type = "RODTEP Entry"
                meis_jv.posting_date = self.posting_date
                meis_jv.company = self.company
                meis_jv.cheque_no = self.name
                meis_jv.cheque_date = self.posting_date
                meis_jv.user_remark = (
                    "RODTEP against " + self.name + " for " + self.customer
                )

                meis_jv.append(
                    "accounts",
                    {
                        "account": meis_receivable_account,
                        "cost_center": meis_cost_center,
                        "debit_in_account_currency": self.total_meis,
                        **({"branch": self.branch} if branch_enabled else {}),

                    },
                )

                meis_jv.append(
                    "accounts",
                    {
                        "account": meis_income_account,
                        "cost_center": meis_cost_center,
                        "credit_in_account_currency": self.total_meis,
                        **({"branch": self.branch} if branch_enabled else {}),

                    },
                )

                try:
                    meis_jv.save(ignore_permissions=True)
                    meis_jv.submit()
                except Exception as e:
                    frappe.throw(str(e))
                else:
                    self.db_set("meis_jv", meis_jv.name)


def create_brc(self):
	if frappe.db.get_value('Address', self.customer_address, 'country') != "India" and frappe.db.exists("DocType", "BRC Management"):
		brc = frappe.new_doc("BRC Management")
		brc.invoice_no = self.name
		if not self.is_return and self.shipping_bill_number and self.shipping_bill_date and self.rounded_total:
			brc.append("shipping_bill_details", {
				"shipping_bill": self.shipping_bill_number,
				"shipping_date": self.shipping_bill_date,
				"shipping_bill_amount": self.rounded_total
			})
		brc.save(ignore_permissions=True)


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
    if doc.get("items") and len(doc.items) > 0:
        so_name = doc.items[0].sales_order
        if so_name:
            copy_selected_producers(doc, so_name)


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

    if all_checked:
        doc.workflow_state = "BL Issued"





@frappe.whitelist()
def create_consolidated_invoice(sales_invoices):

    if isinstance(sales_invoices, str):
        sales_invoices = json.loads(sales_invoices)

    if not sales_invoices:
        frappe.throw("No Sales Invoices selected")

    #  Check if any selected Sales Invoice is already consolidated
    # Check if any selected Sales Invoice is already consolidated
    # Check if any selected Sales Invoice is already used in Consolidated Sales Invoice
    already_consolidated = []

    for si_name in sales_invoices:
        exists = frappe.db.exists(
            "Sales Invoices",          # child table doctype
            {"sales_invoice": si_name}
        )
        if exists:
            already_consolidated.append(si_name)

    if already_consolidated:
        frappe.throw(
            "The following Sales Invoices are already linked to a Consolidated Sales Invoice:<br><b>"
            + ", ".join(already_consolidated)
            + "</b>"
        )


    # lowest_si_name = min(sales_invoices)
    # first_si = frappe.get_doc("Sales Invoice", sales_invoices[0])
    lowest_si_name = min(sales_invoices)
    first_si = frappe.get_doc("Sales Invoice", lowest_si_name)

    sales_contracts = set()
    for si_name in sales_invoices:
        si = frappe.get_doc("Sales Invoice", si_name)
        for item in si.items:
            if item.sales_order:
                sales_contracts.add(item.sales_order)

    if len(sales_contracts) > 1:
        frappe.throw(
            "Selected Sales Invoices contain items from different Sales Contracts. "
            "Please select invoices belonging to the same Sales Contract."
        )

    sales_contract = list(sales_contracts)[0] if sales_contracts else None

    if frappe.db.exists("Consolidated Sales Invoice", first_si.name):
        frappe.throw(
            f"Consolidated Sales Invoice with name '{first_si.name}' already exists"
        )

    csi = frappe.new_doc("Consolidated Sales Invoice")
    csi.name = first_si.name

    csi.customer = first_si.customer
    # csi.is_consignee_same_as_buyer=first_si.custom_is_consignee_same_as_buyer
    # csi.consignee=first_si.custom_consignee
    csi.company = first_si.company
    csi.currency = first_si.currency
    csi.conversion_rate = first_si.conversion_rate
    csi.debit_to = first_si.debit_to
    csi.cost_center = first_si.cost_center
    csi.project = first_si.project
    csi.tax_category = first_si.tax_category
    csi.shipping_rule = first_si.shipping_rule
    csi.incoterm = first_si.incoterm
    csi.taxes_and_charges = first_si.taxes_and_charges
    csi.customer_address = first_si.customer_address
    csi.address_display = first_si.address_display
    csi.gst_category = first_si.gst_category
    csi.contact_person = first_si.contact_person
    csi.territory = first_si.territory
    csi.shipping_address_name = first_si.shipping_address_name
    csi.shipping_address = first_si.shipping_address
    csi.dispatch_address_name = first_si.dispatch_address_name
    csi.company_address = first_si.company_address
    csi.company_address_display = first_si.company_address_display
    csi.company_contact_person = first_si.company_contact_person
    csi.tc_name = first_si.tc_name
    csi.terms = first_si.terms
    csi.update_stock = 1 if first_si.update_stock else 0
    csi.set_warehouse = first_si.set_warehouse
    csi.posting_date = today()

    for si_name in sales_invoices:
        csi.append("sales_invoice_reference", {
        "sales_invoice": si_name
    })
   

    # =========================
    # CONSOLIDATE ITEMS
    # =========================
    item_map = {}

    for si_name in sales_invoices:
        si = frappe.get_doc("Sales Invoice", si_name)

        if si.docstatus != 1:
            frappe.throw(f"{si.name} must be Submitted")

        if si.is_consolidated:
            frappe.db.set_value("Sales Invoice", si.name, "is_consolidated", 0)
            si.is_consolidated = 0

        if si.customer != csi.customer:
            frappe.throw("All Sales Invoices must have the same Customer")

        if si.company != csi.company:
            frappe.throw("All Sales Invoices must belong to the same Company")

        for item in si.items:
            key = item.item_code

            if key in item_map:
                item_map[key]["qty"] += flt(item.qty)
                item_map[key]["amount"] += flt(item.amount)
                item_map[key]["base_amount"] += flt(item.base_amount)
                item_map[key]["sales_orders"].add(item.sales_order)
            else:
                item_map[key] = {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": flt(item.qty),
                    "uom": item.uom,
                    "stock_uom": item.stock_uom,
                    "conversion_factor": flt(item.conversion_factor) if item.conversion_factor else 1,
                    "rate": flt(item.rate),
                    "base_rate": flt(item.base_rate),
                    "amount": flt(item.amount),
                    "base_amount": flt(item.base_amount),
                    "income_account": item.income_account,
                    "cost_center": item.cost_center,
                    "sales_orders": {item.sales_order}
                }

    for row in item_map.values():
        csi.append("items", {
            "item_code": row["item_code"],
            "item_name": row["item_name"],
            "description": row["description"],
            "qty": row["qty"],
            "uom": row["uom"],
            "stock_uom": row["stock_uom"],
            "conversion_factor": row["conversion_factor"],
            "rate": row["rate"],
            "base_rate": row["base_rate"],
            "amount": row["amount"],
            "base_amount": row["base_amount"],
            "income_account": row["income_account"],
            "cost_center": row["cost_center"],
            "sales_order": ", ".join(filter(None, row.get("sales_orders", [])))
        })

    # =========================
    # APPLY TAXES TABLE LOGIC
    # =========================
    tax_map = {}

    for tax in first_si.taxes:
        key = (tax.account_head, tax.charge_type)
        tax_map[key] = {
            "charge_type": tax.charge_type,
            "account_head": tax.account_head,
            "description": tax.description,
            "included_in_print_rate": tax.included_in_print_rate,
            "cost_center": tax.cost_center,
            "rate": flt(tax.rate),
            "gst_tax_type": tax.gst_tax_type,
            "tax_amount": 0,
            "base_tax_amount": 0,
            "total": 0,
            "base_total": 0,
            "tax_amount_after_discount_amount": 0,
        }

    for si_name in sales_invoices:
        si = frappe.get_doc("Sales Invoice", si_name)
        for tax in si.taxes:
            key = (tax.account_head, tax.charge_type)
            if key in tax_map:
                tax_map[key]["tax_amount"] += flt(tax.tax_amount)
                tax_map[key]["base_tax_amount"] += flt(tax.base_tax_amount)
                tax_map[key]["total"] += flt(tax.total)
                tax_map[key]["base_total"] += flt(tax.base_total)
                tax_map[key]["tax_amount_after_discount_amount"] += flt(
                    tax.tax_amount_after_discount_amount
                )

    for row in tax_map.values():
        csi.append("taxes", row)

    # =========================
    # MANUAL TOTALS (FROM SALES INVOICE HEADERS)
    # =========================
    total_qty = 0
    net_total = 0
    base_total = 0
    total=0
    grand_total = 0
    base_grand_total = 0
    base_total_taxes_and_charges=0
    total_taxes_and_charges=0
    outstanding_amount=0
    base_net_total=0
    net_total=0

    for si_name in sales_invoices:
        si = frappe.get_doc("Sales Invoice", si_name)
        total_qty += flt(si.total_qty)
        # net_total += flt(si.net_total)
        total+=flt(si.total)
        base_total_taxes_and_charges+=flt(si.base_total_taxes_and_charges)
        total_taxes_and_charges+=flt(si.total_taxes_and_charges)
        base_total += flt(si.base_total)
        grand_total += flt(si.grand_total)
        base_grand_total += flt(si.base_grand_total)
        outstanding_amount += flt(si.outstanding_amount)
        # base_net_total += flt(si.base_net_total)
        # net_total += flt(si.net_total)

        


        

    csi.total_qty = total_qty
    # csi.net_total = net_total
    csi.base_total = base_total
    csi.total=total
    csi.base_total_taxes_and_charges=base_total_taxes_and_charges
    csi.total_taxes_and_charges=total_taxes_and_charges
    csi.grand_total = grand_total
    csi.base_grand_total = base_grand_total
    csi.sales_contract = sales_contract
    csi.outstanding_amount = outstanding_amount
    # csi.base_net_total = base_net_total
    csi.net_total = net_total



    csi.insert(ignore_permissions=True)
    frappe.db.commit()
    for si_name in sales_invoices:
        frappe.db.set_value("Sales Invoice", si_name, "is_consolidated", 1)

    frappe.msgprint(f"Consolidated Sales Invoice {csi.name} created successfully")

    return csi