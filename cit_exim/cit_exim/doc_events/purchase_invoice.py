import frappe
from frappe import _
from frappe.utils import flt

def pi_on_submit(self, method):
	import_lic(self)
	
def pi_on_cancel(self, method):
	import_lic_cancel(self)
	
def import_lic(self):
	for row in self.items:
		if row.get('advance_authorisation_license'):
			aal = frappe.get_doc("Advance Authorisation License", row.advance_authorisation_license)
			aal.append("imports", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"quantity": row.qty,
				"uom": row.uom,
				"cif_value" : flt(row.cif_value) / self.conversion_rate,
				"fob_value" : flt(row.fob_value) / self.conversion_rate,
				"currency" : self.currency,
				"shipping_bill_no": self.shipping_bill,
				"shipping_bill_date": self.shipping_bill_date,
				"port_of_loading" : self.port_of_loading,
				"port_of_discharge" : self.port_of_discharge,
				"purchase_invoice" : self.name,
			})

			aal.total_import_qty = sum([flt(d.quantity) for d in aal.imports])
			aal.total_import_amount = sum([flt(d.cif_value) for d in aal.imports])
			aal.save()
	# else:
	# 	frappe.db.commit()

def import_lic_cancel(self):
	doc_list = list(set([row.advance_authorisation_license for row in self.items if row.advance_authorisation_license]))

	for doc_name in doc_list:
		doc = frappe.get_doc("Advance Authorisation License", doc_name)
		to_remove = []

		for row in doc.imports:
			if row.parent == doc_name and row.purchase_invoice == self.name:
				to_remove.append(row)

		[doc.remove(row) for row in to_remove]
		doc.total_import_qty = sum([flt(d.quantity) for d in doc.imports])
		doc.total_import_amount = sum([flt(d.cif_value) for d in doc.imports])
		doc.save()