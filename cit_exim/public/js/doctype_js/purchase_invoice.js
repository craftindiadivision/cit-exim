
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

frappe.ui.form.on("Purchase Invoice", {
    setup: function (frm) {
        frappe.db.get_single_value('Exim Settings', 'use_advance_authorization_license_based_on_cas_no_of_item')
            .then(function(data) {
                frm.set_query("advance_authorisation_license", "items", function (doc, cdt, cdn) {
                    let d = locals[cdt][cdn];
                    if (data) {
                        return {
                                query: "cit_exim.cit_exim.doctype.advance_authorisation_license.advance_authorisation_license.cas_number_details",
                                filters: {
                                    'cas_number': d.cas_number
                                }
                            };
                    }
                    else{
                        return {
                            query: "cit_exim.cit_exim.doctype.advance_authorisation_license.advance_authorisation_license.license_query",
                                    filters: {
                                        'item_code': d.item_code
                                    }
                        };
                }});
            });
    },

    before_submit: function (frm) {
        frm.doc.items.forEach(function (d) {
            if (d.advance_authorisation_license) {
                if (d.qty > d.license_qty) {
                    frappe.throw(__(`Row:${d.idx} Qty should be less than or equal to License Qty.`))
                }
            }
        });
    },
	onload:function(frm){
		if(frm.doc.supplier_address || frm.doc.shipping_address){
			frappe.db.get_value("Address", frm.doc.supplier_address, "country", function (r) {
				frappe.db.get_value("Address", frm.doc.shipping_address, "country", function (d) {
					if(r.country == "India" || d.country == "India"){
						cur_frm.set_df_property("shipping_details", "hidden", 1);
					}
					else{
						cur_frm.set_df_property("shipping_details", "hidden", 0);
					}
				});
			});
		}
	},
});

frappe.ui.form.on("Purchase Invoice Item", {
	/* duplicate: function(frm, cdt, cdn) {
		let d = locals[cdt][cdn];
		let m = frm.add_child("items");
		m.item_code = d.item_code;
		m.item_name = d.item_name;
		m.description = d.description;
		m.evergreen_description = d.evergreen_description;
		m.uom = d.uom;
		m.stock_uom = d.stock_uom;
		m.qty = d.qty;
		m.rate = d.rate;
		m.lot_no = d.lot_no;
		m.price_list_rate = d.price_list_rate;
		m.discount_percentage = d.discount_percentage;
		m.packaging_material = d.packaging_material;
		m.packing_size = d.packing_size;
		m.batch_yield = d.batch_yield;
		m.concentration = d.concentration;
		m.item_group = d.item_group;
		m.purchase_order = d.purchase_order;
		m.purchase_receipt = d.purchase_receipt;
		m.po_detail = d.po_detail;
		m.pr_detail = d.pr_detail;
		frm.refresh();
	}, */
    item_code: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        setTimeout(() => {
            frappe.model.set_value(cdt, cdn, 'cif_value', d.amount)
        }, 1000);

        frappe.model.set_value(cdt, cdn, 'advance_authorisation_license', '');
    },

    qty: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'cif_value', flt(d.rate * d.qty));
    },

    advance_authorisation_license: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];

        if (d.advance_authorisation_license) {
            frappe.call({
                method: "cit_exim.cit_exim.doctype.advance_authorisation_license.advance_authorisation_license.get_license_details",
                args: {
                    'aal': d.advance_authorisation_license,
                    'item_code': d.item_code,
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'license_qty', r.message.approved_qty);
                        frappe.model.set_value(cdt, cdn, 'license_remaining_qty', r.message.remaining_qty);
                        //frappe.model.set_value(cdt, cdn, 'license_amount', r.message.approved_amount);
                        //frappe.model.set_value(cdt, cdn, 'license_remaining_amount', r.message.remaining_amount);
                    }
                }
            });
        }
        else {
            frappe.model.set_value(cdt, cdn, 'license_qty', 0);
            frappe.model.set_value(cdt, cdn, 'license_remaining_qty', 0);
            frappe.model.set_value(cdt, cdn, 'license_amount', 0);
            frappe.model.set_value(cdt, cdn, 'license_remaining_amount', 0);
        }
    }
});




//Template Code without mapping the purchase order

// ================================
//  LOADING THE TEMPLATES 
// ================================
function load_variable_template_pi(frm, template_name) {

    if (!template_name) {
        frm.clear_table("custom_quality_and_specification");
        frm.refresh_field("custom_quality_and_specification");
        frm._template_loaded_for = null;
        return;
    }

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
// LOAD FROM ITEM CHANGE (Child Table)
// ================================
frappe.ui.form.on("Purchase Invoice Item", {
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.db.get_value("Item", row.item_code, "custom_template")
            .then(r => {
                let template = r.message?.custom_template;

                if (template) {
                    frm.set_value("custom_product", template);
                    load_variable_template_pi(frm, template);
                } else {
                    frm.set_value("custom_product", "");
                    load_variable_template_pi(frm, null);
                }
            });
    }
});

// ================================
// MANUAL PRODUCT SELECTION
// ================================
frappe.ui.form.on("Purchase Invoice", {
    custom_product(frm) {
        load_variable_template_pi(frm, frm.doc.custom_product);
    }
});
