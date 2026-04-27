

# Copyright (c) 2025, craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class DutyDrawBackClaim(Document):

	def validate(self):
		total = 0.0
		total1 = 0.0

		for row in self.rodtep_details:
			total += flt(row.debit_amount)
			total1 += flt(row.received_amount)

		self.total_debit_amount = flt(total)
		self.script_amount = flt(total1)
		self.round_off_amount = flt(total) - flt(total1)

		# if self.round_off_amount >= 20:
		# 	frappe.throw(_("Round off amount should be less than 20"))

	def on_submit(self):
		self.total_debit_amount = flt(self.total_debit_amount) - flt(self.round_off_amount)

		if round(flt(self.total_debit_amount), 4) != round(flt(self.script_amount), 4):
			frappe.throw(_("Total Script Amount and Total Debit Amount should be equal"))

		if not self.credit_account:
			frappe.throw(_("Set credit account first"))

	def on_cancel(self):
		if self.journal_entry_ref:
			jv = frappe.get_doc("Journal Entry", self.journal_entry_ref)
			jv.cancel()
			self.journal_entry_ref = ''


def exp_je_data(company):
	list_of_je = frappe.db.sql("""
		SELECT rcm.je_no, rd.journal_entry_ref
		FROM `tabDrawback Details` rcm
		JOIN `tabDuty DrawBack Claim` rd
			ON rd.name = rcm.parent
		WHERE rd.company = %s
		  AND rd.docstatus != 2
	""", (company,), as_list=True)

	je = []
	for row in list_of_je:
		for d in row:
			if d:
				je.append(str(d))

	return je


@frappe.whitelist()
def journal_entry_list(start_date, end_date, company):
	list_of_je = exp_je_data(company)
	conditions = ""

	if list_of_je:
		conditions = " AND je.name NOT IN ({})".format(
			", ".join([f'"{l}"' for l in list_of_je])
		)

	args = {
		"r_start_date": start_date,
		"r_end_date": end_date,
		"company": company
	}

	je_data = frappe.db.sql(f"""
		SELECT
			je.name AS je_no,
			IFNULL(jea.debit_in_account_currency, 0) AS debit_amount,
			je.cheque_date,
			je.cheque_no,
			si.shipping_bill_number AS shipping_bill_no,
			c.duty_drawback_receivable_account AS account
		FROM `tabJournal Entry` je
		LEFT JOIN `tabJournal Entry Account` jea
			ON jea.parent = je.name
		LEFT JOIN `tabSales Invoice` si
			ON si.name = je.cheque_no
		LEFT JOIN `tabCompany` c
			ON c.name = je.company
		WHERE je.voucher_type = 'Duty Drawback Entry'
		  AND je.posting_date >= %(r_start_date)s
		  AND je.posting_date <= %(r_end_date)s
		  AND IFNULL(jea.debit_in_account_currency, 0) > 0
		  AND je.docstatus < 2
		  AND je.company = %(company)s
		  {conditions}
	""", args, as_dict=True)

	return je_data


def create_jv_on_submit(self, method):

	if round(flt(self.total_debit_amount), 4) == round(flt(self.script_amount), 4):

		meis_receivable_account = frappe.db.get_value(
			"Company", {"company_name": self.company}, "duty_drawback_receivable_account"
		)
		meis_income_account = frappe.db.get_value(
			"Company", {"company_name": self.company}, "duty_drawback_income_account"
		)
		meis_cost_center = frappe.db.get_value(
			"Company", {"company_name": self.company}, "duty_drawback_cost_center"
		)

		if not meis_receivable_account:
			frappe.throw(_("Set Duty Drawback Receivable Account in Company"))
		elif not meis_income_account:
			frappe.throw(_("Set Duty Drawback Income Account in Company"))
		elif not meis_cost_center:
			frappe.throw(_("Set Duty Drawback Cost Center in Company"))

		meis_jv = frappe.new_doc("Journal Entry")
		meis_jv.voucher_type = "Duty Drawback Entry"
		meis_jv.posting_date = self.posting_date
		meis_jv.company = self.company
		meis_jv.cheque_no = self.name
		meis_jv.cheque_date = self.posting_date
		meis_jv.user_remark = "Duty Drawback against " + self.name

		for row in self.rodtep_details:
			meis_jv.append("accounts", {
				"account": row.account,
				"reference_type": "Journal Entry",
				"reference_name": row.je_no,
				"credit_in_account_currency": flt(row.debit_amount),
				"branch":self.branch
			})

		meis_jv.append("accounts", {
			"account": self.credit_account,
			"debit_in_account_currency": flt(self.total_debit_amount),
			"branch":self.branch
		})

		if flt(self.round_off_amount) < 0:
			meis_jv.append("accounts", {
				"account": self.round_off_account,
				"credit_in_account_currency": abs(flt(self.round_off_amount)),
			})
		elif flt(self.round_off_amount) > 0:
			meis_jv.append("accounts", {
				"account": self.round_off_account,
				"debit_in_account_currency": flt(self.round_off_amount),
			})

		try:
			meis_jv.save(ignore_permissions=True)
			meis_jv.submit()
			self.db_set("journal_entry_ref", meis_jv.name)

			frappe.msgprint(
				_("Journal Entry Created Successfully {0}")
				.format(frappe.bold(meis_jv.name))
			)

		except Exception as e:
			frappe.throw(str(e))



@frappe.whitelist()
def get_credit_account_list(doctype, txt, searchfield, start, page_len, filters):
    company = filters.get("company")

    if not company:
        return []

    accounts = frappe.db.get_all(
        "Account",
        filters={
            "company": company,
            "is_group": 0
        },
        fields=["name"]
    )

    return [(d.name,) for d in accounts]

@frappe.whitelist()
def get_round_off_account_list(doctype, txt, searchfield, start, page_len, filters):
    company = filters.get("company")

    if not company:
        return []

    accounts = frappe.db.get_all(
        "Account",
        filters={
            "company": company,
            "is_group": 0
        },
        fields=["name"]
    )

    return [(d.name,) for d in accounts]