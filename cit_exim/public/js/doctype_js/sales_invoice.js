// frappe.ui.form.on("Sales Invoice", {

//     refresh(frm) {

//         frm.set_query("port_of_loading", () => {
//             return {
//                 filters: {
//                     custom_is_in_india: 1
//                 }
//             };
//         });

//         frm.set_query("port_of_discharge", () => {
//             return {
//                 filters: {
//                     custom_is_in_india: 0
//                 }
//             };
//         });
//     },

//     port_of_discharge(frm) {
//         if (frm.doc.port_of_discharge) {
//             frappe.db.get_value("Port Details", frm.doc.port_of_discharge, "country")
//                 .then(r => {
//                     if (r && r.message) {
//                         frm.set_value("country_of_destination", r.message.country);
//                     }
//                 });
//         } else {
//             frm.set_value("country_of_destination", "");
//         }
//     }

// });




//EXIM
cur_frm.add_fetch('advance_authorisation_license', 'approved_qty', 'license_qty');
cur_frm.add_fetch('advance_authorisation_license', 'remaining_export_qty', 'license_remaining_qty');
cur_frm.add_fetch('advance_authorisation_license', 'approved_amount', 'license_amount');
cur_frm.add_fetch('advance_authorisation_license', 'remaining_license_amount', 'license_remaining_amount');

// Address Filter
cur_frm.set_query("notify_party", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: { link_doctype: "Customer", link_name: cur_frm.doc.customer }
    };
});
frappe.db.get_single_value('Exim Settings', 'use_advance_authorization_license_based_on_cas_no_of_item').then(function(data) {
    if (data) {
        cur_frm.fields_dict.items.grid.get_field("advance_authorisation_license").get_query = function (doc, cdt, cdn) {
            let d = locals[cdt][cdn];
           
                return {
                    filters: {
                        "cas_number": d.cas_number
                    }
                };
        };
    } else {
        cur_frm.fields_dict.items.grid.get_field("advance_authorisation_license").get_query = function (doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                    "export_item": d.item_code
                }
            };
        };
    }
});
cur_frm.fields_dict.items.grid.get_field("advance_authorisation_license").get_query = function (doc, cdt, cdn) {
    let d = locals[cdt][cdn];
    return {
        filters: {
            "export_item": d.item_code,
        }
    }
};

// Customer Address Filter
cur_frm.set_query("customer_address", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: {
            link_doctype: "Customer",
            link_name: cur_frm.doc.customer
        }
    };
});

// Shipping Address Filter
cur_frm.set_query("shipping_address_name", function () {
    return {
        query: "frappe.contacts.doctype.address.address.address_query",
        filters: {}
    };
});

// Customer Contact Filter
cur_frm.set_query("contact_person", function () {
    return {
        query: "frappe.contacts.doctype.contact.contact.contact_query",
        filters: { link_doctype: "Customer", link_name: cur_frm.doc.customer }
    };
});

frappe.ui.form.on("Sales Invoice", {
    onload: function (frm) {
        // frm.trigger("set_package");
        if (frm.doc.customer_address || frm.doc.shipping_address_name) {
            frappe.db.get_value("Address", frm.doc.customer_address, "country", function (r) {
                frappe.db.get_value("Address", frm.doc.shipping_address_name, "country", function (d) {
                    if (r.country == "India" || d.country == "India") {
                        cur_frm.set_df_property("shipping_details", "hidden", 1);
                    }
                    else {
                        cur_frm.set_df_property("shipping_details", "hidden", 0);
                    }
                });
            });
        }
        var so_list_item = [];
        frm.doc.items.forEach(function (d) {
            if (d.sales_order) {
                so_list_item.push(d.sales_order)
            }
        })
        if (so_list_item.length) {
            frm.set_query("contract_and_lc", function () {
                return {
                    query: "cit_exim.api.contract_and_lc_filter",
                    filters: {
                        'sales_order_item': so_list_item
                    }
                }
            })
        }
    },
    contract_and_lc: function (frm) {
        if (frm.doc.contract_and_lc) {
            frappe.model.with_doc("Contract Term", frm.doc.contract_and_lc, function () {
                var doc = frappe.model.get_doc("Contract Term", frm.doc.contract_and_lc)

                frm.clear_table('sales_invoice_export_document_item')
                $.each(doc.document || [], function (i, d) {
                    let c = frm.add_child('sales_invoice_export_document_item')
                    c.contract_term = doc.name;
                    c.export_document = d.export_document
                    c.number = d.number
                    c.copy = d.copy
                })

                frm.clear_table('sales_invoice_contract_term_check')
                $.each(doc.contract_term_check || [], function (i, d) {
                    let c = frm.add_child('sales_invoice_contract_term_check')
                    c.contract_term = doc.name;
                    c.document_check = d.document_check
                })

                frm.refresh_field('sales_invoice_export_document_item')
                frm.refresh_field('sales_invoice_contract_term_check')
            });
        }
    },
    bl_date: function (frm) {
        frm.trigger('maturity_date')
    },
    maturity_date: function (frm) {
        frappe.db.get_value("Payment Term", frm.doc.payment_schedule[0].payment_term, "credit_days", function (n) {
            frm.set_value("maturity_date", frappe.datetime.add_days(frm.doc.bl_date, n.credit_days));
        });
    },
  // fob_value: function (frm, cdt, cdn) {
    //     frm.events.caclulate_total(frm);
    //     frm.events.duty_calculation(frm);
    //     frm.events.meis_calculation(frm);
    // },

});

// ---- Notify Party Section ----
frappe.ui.form.on('Notify Party Address', {
    notify_party: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.notify_party) {
            return frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: {
                    "address_dict": d.notify_party
                },
                callback: function (r) {
                    if (r.message)
                        frappe.model.set_value(cdt, cdn, "notify_address_display", r.message);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "notify_address_display", " ");
        }
    }
});


// ------------------------------------------------------------------------
// *** YOUR NEW CODE ADDED EXACTLY AS REQUESTED (NO CHANGES MADE ABOVE) ***
// ------------------------------------------------------------------------

frappe.ui.form.on("Sales Invoice", {

    refresh(frm) {

        frm.set_query("port_of_loading", () => {
            return {
                filters: {
                    custom_is_in_india: 1
                }
            };
        });

        frm.set_query("port_of_discharge", () => {
            return {
                filters: {
                    custom_is_in_india: 0
                }
            };
        });
    },

    port_of_discharge(frm) {
        if (frm.doc.port_of_discharge) {
            frappe.db.get_value("Port Details", frm.doc.port_of_discharge, "country")
                .then(r => {
                    if (r && r.message) {
                        frm.set_value("country_of_destination", r.message.country);
                    }
                });
        } else {
            frm.set_value("country_of_destination", "");
        }
    }

});
