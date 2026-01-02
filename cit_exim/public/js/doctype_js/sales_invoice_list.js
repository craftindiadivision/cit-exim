frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) {
        listview.page.add_action_item(__('Consolidate Sales Invoice'), function() {

            const selected = listview.get_checked_items();

            if (!selected.length) {
                frappe.msgprint(__('Please select at least one Sales Invoice'));
                return;
            }

            frappe.call({
                method: "cit_exim.cit_exim.doc_events.sales_invoice.create_consolidated_invoice",
                args: {
                    sales_invoices: selected.map(d => d.name)
                },
                callback: function(r) {
                    if (!r.exc && r.message) {
                        const doc = frappe.model.sync(r.message)[0];
                        frappe.set_route("Form", doc.doctype, doc.name);
                    }
                }
            });

        });
    }
};