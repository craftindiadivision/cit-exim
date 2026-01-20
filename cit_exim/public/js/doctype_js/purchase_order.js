
// Supplier Address Filter
cur_frm.set_query("supplier_address", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: { link_doctype: "Supplier", link_name: cur_frm.doc.supplier }
    };
});

// Supplier Contact Filter
cur_frm.set_query("contact_person", function () {
    return {
        query: "frappe.contacts.doctype.contact.contact.contact_query",
        filters: { link_doctype: "Supplier", link_name: cur_frm.doc.supplier }
    };
});

// Shipping Address Filter
cur_frm.set_query("shipping_address", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: { link_doctype: "Company", link_name: cur_frm.doc.company }
    };
});

cur_frm.set_query("billing_address", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: { link_doctype: "Company", link_name: cur_frm.doc.company }
    };
});
frappe.ui.form.on('Purchase Order', {
    billing_address: function (frm) {
        if (frm.doc.billing_address) {
            return frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: {
                    "address_dict": frm.doc.billing_address
                },
                callback: function (r) {
                    if (r.message)
                        frm.set_value("billing_address_display", r.message);
                }
            });
        }
    },
})




// ================================
//  LOADING THE TEMPLATES 
// ================================
function load_variable_template(frm, template_name) {

    if (!template_name) {
        frm.clear_table("custom_quality_and_specification");
        frm.refresh_field("custom_quality_and_specification");
        frm._template_loaded_for = null;
        return;
    }

    // Prevent duplicate reload
    if (frm._template_loaded_for === template_name) return;
    frm._template_loaded_for = template_name;

    frm.clear_table("custom_quality_and_specification");

    frappe.db.get_doc("Variable Template", template_name)
        .then(doc => {
            (doc.lab_variable || []).forEach(row => {
                let child = frm.add_child("custom_quality_and_specification");
                child.test = row.test;
                child.value = row.value;
            });

            frm.refresh_field("custom_quality_and_specification");
        });
}

// ================================
// LOAD FROM ITEM (Child Table)
// ================================
frappe.ui.form.on("Purchase Order Item", {
    item_code(frm, cdt, cdn) {

        const row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.db.get_value(
            "Item",
            row.item_code,
            "custom_template"
        ).then(r => {

            const template = r.message?.custom_template;

            if (template) {
                frm.set_value("custom_product", template);
                load_variable_template(frm, template);
            } else {
                frm.set_value("custom_product", "");
                load_variable_template(frm, null);
            }
        });
    }
});

// ================================
// LOAD FROM MANUAL TEMPLATE CHANGE
// ================================
frappe.ui.form.on("Purchase Order", {
    custom_product(frm) {
        load_variable_template(frm, frm.doc.custom_product);
    }
});

frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        frm.clear_custom_buttons();
        if (frm.doc.per_received === 100){
            return
        }
        if (!frm.is_new()) {
            frm.add_custom_button("Vehicle Queue", () => {
                frappe.call({
                    method: "cit_exim.cit_exim.doc_events.purchase_order.create_vehicle_queue",
                    args: {
                        purchase_order: frm.doc.name
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            frappe.set_route("Form", "Vehicle Queue", r.message);
                        }
                    }
                });
            }, "Create");
        }
    }
});
