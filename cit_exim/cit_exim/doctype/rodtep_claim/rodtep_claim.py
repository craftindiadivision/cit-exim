# Copyright (c) 2025, craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


class RodtepClaim(Document):

    def validate(self):
        total = 0.0
        for row in self.rodtep_details:
            total += flt(row.debit_amount)

        self.total_debit_amount = total
        self.script_amount = total

    def on_submit(self):
        if round(flt(self.total_debit_amount), 4) != round(flt(self.script_amount), 4):
            frappe.throw(_("Total Script Amount and Total Debit Amount should be equal"))

        if not self.credit_account:
            frappe.throw(_("Set credit account first"))

    def on_cancel(self):
        if self.journal_entry_ref:
            jv = frappe.get_doc("Journal Entry", self.journal_entry_ref)
            jv.cancel()
            self.journal_entry_ref = ''


# ----------------------------------------------------------------------
# Get already-used Journal Entries (FIXED SQL)
# ----------------------------------------------------------------------
def exp_je_data(company):
    """
    Returns list of Journal Entry names already linked
    with Rodtep Claim (not cancelled)
    """

    data = frappe.db.sql("""
        SELECT rcm.journal_entry_ref
        FROM `tabRodtep Claim` AS rcm
        WHERE rcm.company = %s
          AND rcm.docstatus < 2
          AND rcm.journal_entry_ref IS NOT NULL
    """, (company,), as_list=True)

    return [row[0] for row in data]


# ----------------------------------------------------------------------
# Fetch Journal Entries for selection
# ----------------------------------------------------------------------
@frappe.whitelist()
def journal_entry_list(start_date, end_date, company):

    list_of_je = exp_je_data(company)
    conditions = ""
    values = [start_date, end_date, company]

    if list_of_je:
        conditions = " AND je.name NOT IN ({}) ".format(
            ",".join(["%s"] * len(list_of_je))
        )
        values.extend(list_of_je)

    je_data = frappe.db.sql(f"""
        SELECT
            je.name AS je_no,
            jea.debit_in_account_currency AS debit_amount,
            je.cheque_date,
            je.cheque_no,
            si.shipping_bill_number AS shipping_bill_no,
            c.meis_receivable_account AS account,
            je.company
        FROM `tabJournal Entry` AS je
        LEFT JOIN `tabJournal Entry Account` AS jea
            ON jea.parent = je.name
        LEFT JOIN `tabSales Invoice` AS si
            ON si.name = je.cheque_no
        LEFT JOIN `tabCompany` AS c
            ON c.name = je.company
        WHERE je.voucher_type = 'RODTEP Entry'
          AND je.posting_date >= %s
          AND je.posting_date <= %s
          AND jea.debit_in_account_currency > 0
          AND je.docstatus < 2
          AND je.company = %s
          {conditions}
    """, values, as_dict=True)

    return je_data


# ----------------------------------------------------------------------
# Create Journal Entry on Submit
# ----------------------------------------------------------------------
def create_jv_on_submit(self, method):

    if round(flt(self.total_debit_amount), 4) != round(flt(self.script_amount), 4):
        return

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
    meis_jv.user_remark = f"RODTEP against {self.name}"

    for row in self.rodtep_details:
        meis_jv.append("accounts", {
            "account": row.account,
            "reference_type": "Journal Entry",
            "reference_name": row.je_no,
            "credit_in_account_currency": flt(row.debit_amount),
        })

    meis_jv.append("accounts", {
        "account": self.credit_account,
        "debit_in_account_currency": flt(self.total_debit_amount),
        "cost_center": meis_cost_center
    })

    try:
        meis_jv.save(ignore_permissions=True)
        meis_jv.submit()
        self.db_set("journal_entry_ref", meis_jv.name)

        frappe.msgprint(
            _("Journal Entry Created Successfully {0}").format(
                frappe.bold(meis_jv.name)
            )
        )

    except Exception as e:
        frappe.throw(str(e))
