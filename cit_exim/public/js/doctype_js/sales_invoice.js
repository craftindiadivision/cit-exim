


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
// -----------------------------------------------------------------------------------------------------------

frappe.ui.form.on("Sales Invoice", {
    refresh: function (frm) {
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

                //  fetch LC No from Contract Term → Sales Invoice
                frm.set_value("custom_lc_no", doc.lc_no);

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
//set port oof loading and discharge
// ------------------------------------------------------------------------

frappe.ui.form.on("Sales Invoice", {

    refresh(frm) {

        frm.set_query("port_of_loading", () => {
            return {
                filters: {
                    is_in_india: 1
                }
            };
        });

        frm.set_query("port_of_discharge", () => {
            return {
                filters: {
                    is_in_india: 0
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

//----------------producer table--------------------------

frappe.ui.form.on('Sales Invoice', {
    onload(frm) {
        // Hide the real table
        frm.set_df_property('custom_producer_table', 'hidden', 1);

        // Render HTML table
        render_producer_html(frm);
    },

    refresh(frm) {
        render_producer_html(frm);
    }
});

function render_producer_html(frm) {
    if (!frm.doc.custom_producer_table || !frm.fields_dict.custom_producer_list) return;

    let html = `
        <div style="
            background-color: #f2f2f2;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            width: 95%;
            display: flex;
            flex-wrap: wrap;
            gap: 40px;
        ">
    `;

    // Show only selected rows
    frm.doc.custom_producer_table
        .filter(row => row.selected == 1)
        .forEach((row) => {
            html += `
                <div style="flex:0 0 45%; display:flex; flex-direction:column;">
                    <div style="display:flex; align-items:center;">
                        <input type="checkbox"
                            class="producer-check"
                            data-name="${row.name}"
                            ${row.selected ? 'checked' : ''}>
                        <label style="margin-left:5px;">${row.producer}</label>
                    </div>
                    ${row.address ? `<div style="font-size:12px; color:#555; margin-left:20px;">${row.address}</div>` : ``}
                </div>
            `;
        });

    html += `</div>`;

    frm.fields_dict.custom_producer_list.$wrapper.html(html);

    // Sync checkbox changes back to child table
    frm.fields_dict.custom_producer_list.$wrapper
        .off('change', '.producer-check')
        .on('change', '.producer-check', function () {
            const row_name = $(this).data('name');
            const is_checked = $(this).is(':checked');

            frm.doc.custom_producer_table.forEach(row => {
                if (row.name === row_name) {
                    row.selected = is_checked ? 1 : 0;
                }
            });

            frm.dirty();
            frm.refresh_field('custom_producer_table');
        });
}

//----------------set container no: in to field---------------

frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        update_number_of_containers(frm);
    }
});

frappe.ui.form.on("container_detail", {
    lot_no(frm) {
        update_number_of_containers(frm);
    },

    container_detail_add(frm) {
        update_number_of_containers(frm);
    },

    container_detail_remove(frm) {
        update_number_of_containers(frm);
    }
});

function update_number_of_containers(frm) {
    let count = 0;

    if (frm.doc.container_detail) {
        frm.doc.container_detail.forEach(row => {
            if (row.lot_no) {
                count += 1;
            }
        });
    }

    frm.set_value("number_of_containers", count);
}




//----------------- set no of packages ------------------

frappe.ui.form.on("Sales Invoice Item", {
    qty: function (frm, cdt, cdn) {
        update_no_of_packages(frm, cdt, cdn);
    },

    item_code: function (frm, cdt, cdn) {
        update_no_of_packages(frm, cdt, cdn);
    }
});

function update_no_of_packages(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.item_code || !row.qty) return;

    //SET THE  BASE LOT QTY 20(MT) 
    const BASE_LOT_QTY = 20;

    frappe.db.get_value(
        "Item",
        row.item_code,
        "custom_no_of_packages_per_lot"
    ).then(r => {
        let packages_per_lot = r.message.custom_no_of_packages_per_lot;

        if (!packages_per_lot) return;

        let calculated_packages =
            (row.qty / BASE_LOT_QTY) * packages_per_lot;

        // Safety: round to whole packages
        row.no_of_packages = Math.round(calculated_packages);

        frm.refresh_field("items");
    });
}




// Template Code without mapping sales contract 

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
frappe.ui.form.on("Sales Invoice Item", {
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
frappe.ui.form.on("Sales Invoice", {
    custom_product(frm) {
        load_variable_template(frm, frm.doc.custom_product);
    }
});


//--------------------------------------------------------------------------------

// =======================================================
// SALES INVOICE : DOCUMENT CHECK VALIDATION
// =======================================================

frappe.ui.form.on('Sales Invoice', {

    onload(frm) {
        update_custom_document_checked(frm);
    },

    refresh(frm) {
        update_custom_document_checked(frm);
    },

    // Prevent manual edit
    custom_document_checked(frm) {
        update_custom_document_checked(frm);
    }
});


// =======================================================
// CHILD TABLE 1 : Sales Invoice Contract Term Check
// =======================================================

// frappe.ui.form.on('Sales Invoice Contract Term Check', {

//     checked(frm, cdt, cdn) {
//         update_custom_document_checked(frm);
//     },

//     sales_invoice_contract_term_check_add(frm) {
//         update_custom_document_checked(frm);
//     },

//     sales_invoice_contract_term_check_remove(frm) {
//         update_custom_document_checked(frm);
//     }
// });


// =======================================================
// CHILD TABLE 2 : Sales Invoice Export Document Item
// =======================================================

frappe.ui.form.on('Sales Invoice Export Document Item', {

    checked(frm, cdt, cdn) {
        update_custom_document_checked(frm);
    },

    sales_invoice_export_document_item_add(frm) {
        update_custom_document_checked(frm);
    },

    sales_invoice_export_document_item_remove(frm) {
        update_custom_document_checked(frm);
    }
});


// =======================================================
// COMMON VALIDATION FUNCTION
// =======================================================

function update_custom_document_checked(frm) {

    let all_checked = true;

    // // ---------- Validate Contract Term Check ----------
    // if (!frm.doc.sales_invoice_contract_term_check ||
    //     frm.doc.sales_invoice_contract_term_check.length === 0) {

    //     all_checked = false;

    // } else {
    //     frm.doc.sales_invoice_contract_term_check.forEach(row => {
    //         if (row.checked !== 1) {
    //             all_checked = false;
    //         }
    //     });
    // }

    // ---------- Validate Export Document Item ----------
    if (!frm.doc.sales_invoice_export_document_item ||
        frm.doc.sales_invoice_export_document_item.length === 0) {

        all_checked = false;

    } else {
        frm.doc.sales_invoice_export_document_item.forEach(row => {
            if (row.checked !== 1) {
                all_checked = false;
            }
        });
    }

    // ---------- Apply Result ----------
    if (all_checked) {
        frm.set_value('custom_document_checked', 1);
        frm.set_df_property('custom_document_checked', 'read_only', 0);
    } else {
        frm.set_value('custom_document_checked', 0);
        frm.set_df_property('custom_document_checked', 'read_only', 1);
    }

    frm.refresh_field('custom_document_checked');
}




//PACKING 

// FETCH PACKING DETAILS FROM ITEM MASTER (DIRECT SALES INVOICE)
frappe.ui.form.on("Sales Invoice Item", {
    item_code(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        // If item removed, clear parent fields
        if (!row.item_code) {
            frm.set_value("custom_packing_template", "");
            frm.set_value("custom_packing_detailsfor_sales_contract", "");
            frm.set_value("custom_packing_detailsfor_sales_invoice", "");
            return;
        }

        // Fetch values from Item master
        frappe.db.get_value(
            "Item",
            row.item_code,
            [
                "custom_name_of_packing",
                "custom_details_of_packing",
                "custom_packing_detailsfor_sales_contract"
            ]
        ).then(r => {
            if (r && r.message) {

                // Set values in Sales Invoice (parent)
                frm.set_value(
                    "custom_packing_template",
                    r.message.custom_name_of_packing || ""
                );

                frm.set_value(
                    "custom_packing_detailsfor_sales_contract",
                    r.message.custom_packing_detailsfor_sales_contract || ""
                );

                frm.set_value(
                    "custom_packing_detailsfor_sales_invoice",
                    r.message.custom_details_of_packing || ""
                );
            }
        });
    }
});








//set readonly the button payment status

frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        // Make checkbox read-only once payment is completed
        if (frm.doc.custom_payment_status === 1) {
            frm.set_df_property(
                "custom_payment_status",
                "read_only",
                1
            );
        }
    }
});


// show corresponding item from fetched item group

frappe.ui.form.on("Sales Invoice", {
    custom_item_group: function (frm) {

        // If Item Group is empty, remove item filter
        if (!frm.doc.custom_item_group) {
            frm.set_query("item_code", "items", () => {
                return {};
            });
            return;
        }

        // Apply item group based filter to item_code dropdown
        frm.set_query("item_code", "items", () => {
            return {
                filters: {
                    item_group: frm.doc.custom_item_group,
                    disabled: 0
                }
            };
        });
    }
});


frappe.ui.form.on("Sales Invoice", {
    customer: function(frm) {
        frm.set_query("custom_consignee", function() {
            return {
                query: "cit_exim.cit_exim.doc_events.sales_order.get_consignee_list",
                filters: {
                    customer: frm.doc.customer
                }
            };
        });
    }
});


// frappe.ui.form.on("Sales Invoice", {
//     refresh(frm) {
//         if (frm.doc.custom_submission_date) {
//             frm.set_df_property(
//                 "custom_submission_date",
//                 "read_only",
//                 1
//             );
//         }
//     }
// });

// frappe.ui.form.on('Sales Invoice', {
//     refresh: function(frm) {
//         // Locks the field visually if it contains a date
//         if (frm.doc.custom_submission_date) {
//             frm.set_df_property('custom_submission_date', 'read_only', 1);
//         }
//     }
// });



frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Lock the field if it has a value or if it's in the target state
        if (frm.doc.custom_submission_date || frm.doc.workflow_state === "Document Submitted & Awaiting Payments") {
            frm.set_df_property('custom_submission_date', 'read_only', 1);
        }
    }
});



// frappe.ui.form.on('Sales Invoice', {
//     refresh(frm) {
//         if (
//             frm.doc.docstatus === 1 &&
//             frm.doc.custom_loading_point === "MUNDRA"
//         ) {
//             frm.add_custom_button(
//                 __('Split Sales Invoice'),
//                 () => {
//                     let dialog = new frappe.ui.Dialog({
//                         title: __('Split Sales Invoice'),
//                         fields: [
//                             {
//                                 fieldname: 'split_count',
//                                 fieldtype: 'Int',
//                                 label: __('How Many Sales Invoice Can be Split'),
//                                 reqd: 1,
//                                 default: 2,
//                                 min: 1
//                             }
//                         ],
//                         primary_action_label: __('Create'),
//                         primary_action(values) {
//                             frappe.call({
//                                 method: "cit_exim.cit_exim.doc_events.sales_invoice.split_sales_invoice",
//                                 args: {
//                                     sales_invoice: frm.doc.name,
//                                     split_count: values.split_count
//                                 },
//                                 callback: function (r) {
//                                     if (r.message && r.message.length) {
//                                         frappe.msgprint({
//                                             title: __('Success'),
//                                             message: __('{0} Split Sales Invoices created', [r.message.length]),
//                                             indicator: 'green'
//                                         });

//                                         // open first created split invoice
//                                         frappe.set_route(
//                                             'Form',
//                                             'Split Sales Invoice',
//                                             r.message[0]
//                                         );
//                                     }
//                                 }
//                             });
//                             dialog.hide();
//                         }
//                     });

//                     dialog.show();
//                 },
//                 __('Create')
//             );
//         }
//     }
// });



// frappe.ui.form.on('Sales Invoice', {
//     refresh(frm) {
//         if (
//             frm.doc.docstatus === 1 &&
//             frm.doc.custom_loading_point === "MUNDRA"
//         ) {
//             frm.add_custom_button(__('Split Sales Invoice'), () => {

//                 let d = new frappe.ui.Dialog({
//                     title: __('Split Sales Invoice'),
//                     fields: [
//                         {
//                             fieldname: 'split_count',
//                             fieldtype: 'Int',
//                             label: __('How many Sales Invoices Can be Splitted?'),
//                             reqd: 1,
//                             min: 1
//                         }
//                     ],
//                     primary_action_label: __('Create'),
//                     primary_action(values) {

//                         frappe.call({
//                             method: "cit_exim.cit_exim.doc_events.sales_invoice.split_sales_invoice",
//                             args: {
//                                 sales_invoice: frm.doc.name,
//                                 split_count: values.split_count
//                             },
//                             callback(r) {
//                                 if (r.message) {
//                                     frappe.msgprint(
//                                         __('{0} Split Sales Invoices created', [r.message.length])
//                                     );

//                                     frappe.set_route(
//                                         'Form',
//                                         'Split Sales Invoice',
//                                         r.message[0]
//                                     );
//                                 }
//                             }
//                         });

//                         d.hide();
//                     }
//                 });

//                 d.show();
//             }, __('Create'));
//         }
//     }
// });





// frappe.ui.form.on('Sales Invoice', {
//     refresh(frm) {
//         if (
//             frm.doc.docstatus === 1 &&
//             frm.doc.custom_loading_point === "MUNDRA"
//         ) {
//             // Remove button first to prevent duplicates on refresh
//             frm.remove_custom_button(__('Split Sales Invoice'), __('Create'));

//             frm.add_custom_button(__('Split Sales Invoice'), () => {
//                 let d = new frappe.ui.Dialog({
//                     title: __('Split Sales Invoice'),
//                     fields: [
//                         {
//                             fieldname: 'split_count',
//                             fieldtype: 'Int',
//                             label: __('How many Sales Invoices should this be split into?'),
//                             reqd: 1,
//                             default: 2
//                         }
//                     ],
//                     primary_action_label: __('Split'),
//                     primary_action(values) {
//                         if (values.split_count < 2) {
//                             frappe.msgprint(__('Split count must be 2 or more'));
//                             return;
//                         }

//                         frappe.call({
//                             method: "cit_exim.cit_exim.doc_events.sales_invoice.split_sales_invoice",
//                             args: {
//                                 sales_invoice: frm.doc.name,
//                                 split_count: values.split_count
//                             },
//                             freeze: true,
//                             freeze_message: __("Splitting Invoice..."),
//                             callback(r) {
//                                 if (r.message) {
//                                     frappe.msgprint(
//                                         __('{0} Draft Sales Invoices created', [r.message.length])
//                                     );
//                                     // Redirect to the first one created
//                                     frappe.set_route('Form', 'Sales Invoice', r.message[0]);
//                                 }
//                             }
//                         });
//                         d.hide();
//                     }
//                 });
//                 d.show();
//             }, __('Create'));
//         }
//     }
// });


// frappe.ui.form.on('Sales Invoice', {
//     refresh(frm) {
//         if (frm.doc.docstatus === 1 && frm.doc.custom_loading_point === "MUNDRA") {
            
//             frm.remove_custom_button(__('Split Sales Invoice'), __('Create'));

//             frm.add_custom_button(__('Split Sales Invoice'), () => {
//                 let d = new frappe.ui.Dialog({
//                     title: __('Split into Separate Records'),
//                     fields: [
//                         {
//                             fieldname: 'split_count',
//                             fieldtype: 'Int',
//                             label: __('Number of Split Records'),
//                             reqd: 1,
//                             default: 2
//                         }
//                     ],
//                     primary_action_label: __('Split'),
//                     primary_action(values) {
//                         if (values.split_count < 2) {
//                             frappe.msgprint(__('Split count must be 2 or more'));
//                             return;
//                         }

//                         frappe.call({
//                             method: "cit_exim.cit_exim.doc_events.sales_invoice.split_sales_invoice",
//                             args: {
//                                 sales_invoice: frm.doc.name,
//                                 split_count: values.split_count
//                             },
//                             freeze: true,
//                             freeze_message: __("Creating Split Records..."),
//                             callback(r) {
//                                 if (r.message) {
//                                     frappe.msgprint(
//                                         __('{0} records created in Split Sales Invoice  list', [r.message.length])
//                                     );
//                                     // Redirect to the new DocType list or the first record
//                                     frappe.set_route('List', 'Split Sales Invoice');
//                                 }
//                             }
//                         });
//                         d.hide();
//                     }
//                 });
//                 d.show();
//             }, __('Create'));
//         }
//     }
// });



































// frappe.ui.form.on('Sales Invoice', {
//     refresh: function(frm) {
//         manage_split_button(frm);
//     },
//     // Triggers whenever the Loading Point field is changed
//     custom_loading_point: function(frm) {
//         manage_split_button(frm);
//     }
// });

// function manage_split_button(frm) {
//     // 1. Clear existing button to prevent duplicates
//     frm.remove_custom_button(__('Split Sales Invoice'), __('Create'));

//     // 2. Conditions: 
//     // - Doc is not Cancelled (docstatus != 2)
//     // - custom_loading_point is exactly "MUNDRA"
//     if (frm.doc.docstatus !== 2 && frm.doc.custom_loading_point === "MUNDRA") {
        
//         frm.add_custom_button(__('Split Sales Invoice'), () => {
            
//             // Validation: Ensure the document is saved before splitting
//             if (frm.is_dirty()) {
//                 frappe.msgprint(__('Please save the document before splitting.'));
//                 return;
//             }

//             let d = new frappe.ui.Dialog({
//                 title: __('Split into Separate Records'),
//                 fields: [
//                     {
//                         fieldname: 'split_count',
//                         fieldtype: 'Int',
//                         label: __('Number of Split Records'),
//                         reqd: 1,
//                         default: 2
//                     }
//                 ],
//                 primary_action_label: __('Split'),
//                 primary_action(values) {
//                     if (values.split_count < 2) {
//                         frappe.msgprint(__('Split count must be 2 or more'));
//                         return;
//                     }

//                     frappe.call({
//                         method: "cit_exim.cit_exim.doc_events.sales_invoice.split_sales_invoice",
//                         args: {
//                             sales_invoice: frm.doc.name,
//                             split_count: values.split_count
//                         },
//                         freeze: true,
//                         freeze_message: __("Creating Split Records..."),
//                         callback(r) {
//                             if (r.message) {
//                                 frappe.msgprint({
//                                     title: __('Success'),
//                                     indicator: 'green',
//                                     message: __('{0} split records created.', [r.message.length])
//                                 });
//                                 frappe.set_route('List', 'Split Sales Invoice');
//                             }
//                         }
//                     });
//                     d.hide();
//                 }
//             });
//             d.show();
//         }, __('Create'));
//     }
// }





























frappe.ui.form.on('Sales Invoice', {
    branch: function(frm) {
        
        if (frm.doc.branch) {
            frappe.db.get_value('Address', {
                custom_branch: frm.doc.branch,
                is_your_company_address: 1
            },
            'name').then(r => {
                if (r && r.message && r.message.name) {
                    frm.set_value('company_address', r.message.name);
                
                }
            });
        }
    }
});





frappe.ui.form.on("Sales Invoice", {
    customer: function(frm) {
        frm.set_query("custom_consignee", function() {
            return {
                query: "cit_exim.cit_exim.doc_events.sales_invoice.get_consignee_list",
                filters: {
                    customer: frm.doc.customer
                }
            };
        });
    }
});

// /////////////////////////////////////////Address changing based on Buyer and consignee//////////////////////////////////////////////////////////////




frappe.ui.form.on("Sales Invoice", {
    custom_consignee: function(frm) {
        if (!frm.doc.custom_consignee) {
            frm.set_value("shipping_address_name", "");
            return;
        }

        frappe.call({
            method: "cit_exim.cit_exim.doc_events.sales_invoice.get_customer_shipping_address",
            args: {
                customer: frm.doc.customer
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("shipping_address_name", r.message);
                } else {
                    frm.set_value("shipping_address_name", "");
                    frappe.msgprint({
                        title: "Shipping Address",
                        message: "No Shipping Address found for this Consignee",
                        indicator: "orange"
                    });
                }
            }
        });
    }
});


frappe.ui.form.on("Sales Invoice", {
    custom_is_consignee_same_as_buyer(frm) {
        if (!frm.doc.customer) {
            frappe.msgprint("Please select a customer first.");
            frm.set_value("custom_is_consignee_same_as_buyer", 0);
            return;
        }

        if (frm.doc.custom_is_consignee_same_as_buyer) {
            frappe.call({
                method: "cit_exim.cit_exim.doc_events.sales_invoice.get_billing_address_for_customer",

                args: {
                   
                    customer: frm.doc.customer
                },
                callback(r) {
                    if (r.message) {
                        frm.set_value("customer_address", r.message);
                        frm.set_value("shipping_address_name", r.message);
                    } else {
                        frappe.msgprint("No billing address found for this customer.");
                    }
                }
            });
        }
        if(frm.doc.custom_is_consignee_same_as_buyer === 1 && frm.doc.custom_consignee){
            frm.set_value("shipping_address_name",frm.doc.customer_address)
        }
    }
});





// -------------------------------------------------------------------------------------------------------------



