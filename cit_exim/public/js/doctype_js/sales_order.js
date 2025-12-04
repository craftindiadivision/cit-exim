
// // SALES ORDER ITEM SCRIPT
// frappe.ui.form.on("Sales Order Item", {
//     item_code(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         if (!row.item_code) return;

//         // Get Item Group of selected Item
//         frappe.db.get_value("Item", row.item_code, "item_group")
//             .then(r => {
//                 let item_group = r.message.item_group;
//                 if (!item_group) return;

//                 // Get matching Variable Template
//                 frappe.db.get_list("Variable Template", {
//                     fields: ["name"],
//                     filters: { item_group: item_group },
//                     limit: 1
//                 }).then(res => {
//                     if (res && res.length > 0) {

//                         // Avoid infinite loop
//                         if (frm.doc.custom_product !== res[0].name) {
//                             frm._template_loaded_for = null;
//                             frm.set_value("custom_product", res[0].name);
//                         }
//                     }
//                 });
//             });
//     }
// });


// // SALES ORDER MAIN SCRIPT
// frappe.ui.form.on("Sales Order", {


//     // LOAD TEMPLATE FOR QUALITY & SPECIFICATIONS
//     custom_product(frm) {

//         if (frm._template_loaded_for === frm.doc.custom_product) return;

//         frm._template_loaded_for = frm.doc.custom_product;

//         frm.clear_table("custom_quality_and_specification");

//         if (!frm.doc.custom_product) {
//             frm.refresh_field("custom_quality_and_specification");
//             return;
//         }

//         frappe.db.get_doc("Variable Template", frm.doc.custom_product)
//             .then(template => {
//                 (template.lab_variable || []).forEach(t => {
//                     let child = frm.add_child("custom_quality_and_specification");
//                     child.test = t.test;
//                     child.value = t.value;
//                 });

//                 frm.refresh_field("custom_quality_and_specification");
//             });
//     },


//     // REFRESH FUNCTION
//     refresh(frm) {

//         // AUTO SET START AND END DATES
//         if (frm.doc.transaction_date && !frm.doc.custom_shipment_period_start) {
//             frm.set_value("custom_shipment_period_start", frm.doc.transaction_date);
//         }
//         if (frm.doc.delivery_date && !frm.doc.custom_shipment_period_end) {
//             frm.set_value("custom_shipment_period_end", frm.doc.delivery_date);
//         }

//         // CONSIGNEE FILTER
//         frm.set_query("custom_consignee", function() {
//             return {
//                 filters: {
//                     custom_is_consignee: 1,
//                     link_doctype: "Customer",
//                     link_name: frm.doc.customer || ""
//                 }
//             };
//         });

//         // AGENT FILTER
//         frm.set_query("custom_agent", function() {
//             return {
//                 filters: { custom_is_agent: 1 }
//             };
//         });

//         // PORT FILTERS
//         frm.set_query("port_of_loading", () => ({
//             filters: { custom_is_in_india: 1 }
//         }));

//         frm.set_query("port_of_discharge", () => ({
//             filters: { custom_is_in_india: 0 }
//         }));

//         frm.trigger("set_signing_authority_options");
//         frm.trigger("calculate_shipping_period");
//         toggle_other_insurance_field(frm);
//     },


 
//     // AUTO UPDATE SHIPMENT DATES
//     transaction_date(frm) {
//         if (frm.doc.transaction_date) {
//             frm.set_value("custom_shipment_period_start", frm.doc.transaction_date);
//         }
//     },

//     delivery_date(frm) {
//         if (frm.doc.delivery_date) {
//             frm.set_value("custom_shipment_period_end", frm.doc.delivery_date);
//         }
//     },



//     // AUTO FILL SHIPPING ADDRESS BASED ON CONSIGNEE
//     custom_consignee(frm) {
//         if (!frm.doc.custom_consignee) return;

//         frm.set_value("shipping_address_name", frm.doc.custom_consignee);

//         frappe.call({
//             method: "frappe.contacts.doctype.address.address.get_address_display",
//             args: { address_dict: frm.doc.custom_consignee },
//             callback(r) {
//                 if (r.message) {
//                     frm.set_value("shipping_address", r.message);
//                 }
//             }
//         });
//     },



//     // SIGNING AUTHORITY
//     customer(frm) { frm.trigger("set_signing_authority_options"); },
//     custom_agent(frm) { frm.trigger("set_signing_authority_options"); },



//     // INSURANCE OPTION
//     custom_insurance(frm) { toggle_other_insurance_field(frm); },



//     // SHIPPING PERIOD CALCULATION
//     custom_shipment_period_start(frm) { frm.trigger("calculate_shipping_period"); },
//     custom_shipment_period_end(frm) { frm.trigger("calculate_shipping_period"); },


  
//     // UPDATE COUNTRY OF DESTINATION FROM PORT

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
//     },



//     // CALCULATE SHIPPING PERIOD MONTHS
//     calculate_shipping_period(frm) {
//         let start = frm.doc.custom_shipment_period_start;
//         let end = frm.doc.custom_shipment_period_end;

//         if (start && end) {
//             let startDate = frappe.datetime.str_to_obj(start);
//             let endDate = frappe.datetime.str_to_obj(end);

//             let years = endDate.getFullYear() - startDate.getFullYear();
//             let months = endDate.getMonth() - startDate.getMonth();

//             let totalMonths = years * 12 + months + 1;
//             if (totalMonths < 0) totalMonths = 0;

//             frm.set_value("custom_shipping_period", totalMonths + " Months");
//         }
//     },



//     // UPDATE SIGNING AUTHORITY OPTIONS
//     set_signing_authority_options(frm) {
//         let options = [];

//         if (frm.doc.custom_agent)
//             options.push("Agent: " + frm.doc.custom_agent);

//         if (frm.doc.customer_name)
//             options.push("Buyer: " + frm.doc.customer_name);

//         frm.set_df_property(
//             "custom_signing_authority",
//             "options",
//             options.join("\n")
//         );
//     }
// });



// // INSURANCE FIELD SHOW/HIDE FUNCTION
// function toggle_other_insurance_field(frm) {
//     if (frm.doc.custom_insurance === "Other (Specify)") {
//         frm.set_df_property("custom_specify_other_insurance_term", "hidden", false);
//     } else {
//         frm.set_df_property("custom_specify_other_insurance_term", "hidden", true);
//         frm.set_value("custom_specify_other_insurance_term", "");
//     }
// }



cur_frm.cscript.onload = function (frm) {
    // Billing Address Filter
    cur_frm.set_query("customer_address", function () {
        return {
            query: "frappe.contacts.doctype.address.address.address_query",
            filters: { link_doctype: "Customer", link_name: cur_frm.doc.customer }
        };
    });

    // Shipping Address Filter
    cur_frm.set_query("shipping_address_name", function () {
        return {
            query: "frappe.contacts.doctype.address.address.address_query",
            filters: { }
        };
    });

    // Supplier Contact Filter
    cur_frm.set_query("contact_person", function () {
        return {
            query: "frappe.contacts.doctype.contact.contact.contact_query",
            filters: { link_doctype: "Customer", link_name: cur_frm.doc.customer }
        };
    });

    cur_frm.fields_dict.items.grid.get_field("ref_no").get_query = function (doc, cdt, cdn) {
        let d = locals[cdt][cdn];
        return {
            filters: {
                "product_name": d.item_code,
            }
        }
    };

}

frappe.ui.form.on("Sales Order", {
    before_save: function (frm) {
        frm.trigger("cal_total");
        frappe.call({
            method: 'cit_exim.api.company_address',
            args: {
                'company': frm.doc.company
            },
            callback: function (r) {
                if (r.message && frm.doc.__islocal) {
                    frm.set_value("company_address", r.message.company_address);
                }
            }
        })
    },

    refresh: function (frm) {
        if (!in_list(["Closed", "Completed"], frm.doc.status)) {
            if (frm.doc.docstatus == 1) {
                frm.add_custom_button(__("Contract Term"), function () {
                    frappe.model.open_mapped_doc({
                        method: "cit_exim.api.make_lc",
                        frm: cur_frm
                    })
                }, __("Create"))
            }
        }

    },

    onload:function(frm){
        if(frm.doc.customer_address || frm.doc.shipping_address_name){
            frappe.db.get_value("Address", frm.doc.customer_address, "country", function (r) {
                frappe.db.get_value("Address", frm.doc.shipping_address_name, "country", function (d) {
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

    onload_post_render: function(frm){
        // hide delivery note from make button
        let $group = cur_frm.page.get_inner_group_button("Make");
        
        let li_length = $group.find("ul li");
        for (let i = 0; i < li_length.length -1; i++) {        
            var li = $group.find(".dropdown-menu").children("li")[i];
            if (li.getElementsByTagName("a")[0].innerHTML == "Delivery")
                $group.find(".dropdown-menu").children("li")[i].remove();
        }
    },

    cal_total: function (frm) {
        let total_qty = 0.0;
        let total_gr_wt = 0.0;

        frm.doc.items.forEach(function (d) {
            total_qty += flt(d.qty);
            d.gross_wt = flt(d.tare_wt) + (d.qty * (flt(d.weight_per_unit) || 1));
            total_gr_wt += flt(d.gross_wt);
        });

        frm.set_value("total_qty", total_qty);
        frm.set_value("total_gr_wt", total_gr_wt);
    },

    box_cal: function (frm) {
        frm.doc.items.forEach(function (d, i) {
            if (i == 0) {
                d.packages_from = 1;
                d.packages_to = d.no_of_packages;
            }
            else {
                d.packages_from = Math.round(frm.doc.items[i - 1].packages_to + 1);
                d.packages_to = Math.round(d.packages_from + d.no_of_packages - 1);
            }
        });
        frm.refresh_field('items');
    },

    pallet_cal: function (frm) {
        frm.doc.items.forEach(function (d, i) {
            if (d.palleted) {
                if (i == 0) {
                    d.pallet_no_from = 1;
                    d.pallet_no_to = Math.round(d.total_pallets);
                }
                else {
                    d.pallet_no_from = Math.round(frm.doc.items[i - 1].pallet_no_to + 1);
                    d.pallet_no_to = Math.round(d.pallet_no_from + d.total_pallets - 1);
                }
            }
        });
        frm.refresh_field('items');
    },




    // LOAD TEMPLATE FOR QUALITY & SPECIFICATIONS
    custom_product(frm) {

        if (frm._template_loaded_for === frm.doc.custom_product) return;

        frm._template_loaded_for = frm.doc.custom_product;

        frm.clear_table("custom_quality_and_specification");

        if (!frm.doc.custom_product) {
            frm.refresh_field("custom_quality_and_specification");
            return;
        }

        frappe.db.get_doc("Variable Template", frm.doc.custom_product)
            .then(template => {
                (template.lab_variable || []).forEach(t => {
                    let child = frm.add_child("custom_quality_and_specification");
                    child.test = t.test;
                    child.value = t.value;
                });

                frm.refresh_field("custom_quality_and_specification");
            });
    },

    // REFRESH FUNCTION
    refresh(frm) {

        // AUTO SET START AND END DATES
        if (frm.doc.transaction_date && !frm.doc.custom_shipment_period_start) {
            frm.set_value("custom_shipment_period_start", frm.doc.transaction_date);
        }
        if (frm.doc.delivery_date && !frm.doc.custom_shipment_period_end) {
            frm.set_value("custom_shipment_period_end", frm.doc.delivery_date);
        }

        // CONSIGNEE FILTER
        frm.set_query("custom_consignee", function() {
            return {
                filters: {
                    custom_is_consignee: 1,
                    link_doctype: "Customer",
                    link_name: frm.doc.customer || ""
                }
            };
        });

        // AGENT FILTER
        frm.set_query("custom_agent", function() {
            return {
                filters: { custom_is_agent: 1 }
            };
        });

        // PORT FILTERS
        frm.set_query("port_of_loading", () => ({
            filters: { is_in_india: 1 }
        }));

        frm.set_query("port_of_discharge", () => ({
            filters: { is_in_india: 0 }
        }));

        frm.trigger("set_signing_authority_options");
        frm.trigger("calculate_shipping_period");
        toggle_other_insurance_field(frm);
    },

    // AUTO UPDATE SHIPMENT DATES
    transaction_date(frm) {
        if (frm.doc.transaction_date) {
            frm.set_value("custom_shipment_period_start", frm.doc.transaction_date);
        }
    },

    delivery_date(frm) {
        if (frm.doc.delivery_date) {
            frm.set_value("custom_shipment_period_end", frm.doc.delivery_date);
        }
    },

    // AUTO FILL SHIPPING ADDRESS BASED ON CONSIGNEE
    custom_consignee(frm) {
        if (!frm.doc.custom_consignee) return;

        frm.set_value("shipping_address_name", frm.doc.custom_consignee);

        frappe.call({
            method: "frappe.contacts.doctype.address.address.get_address_display",
            args: { address_dict: frm.doc.custom_consignee },
            callback(r) {
                if (r.message) {
                    frm.set_value("shipping_address", r.message);
                }
            }
        });
    },

    // SIGNING AUTHORITY
    customer(frm) { frm.trigger("set_signing_authority_options"); },
    custom_agent(frm) { frm.trigger("set_signing_authority_options"); },

    // INSURANCE OPTION
    custom_insurance(frm) { toggle_other_insurance_field(frm); },

    // SHIPPING PERIOD CALCULATION
    custom_shipment_period_start(frm) { frm.trigger("calculate_shipping_period"); },
    custom_shipment_period_end(frm) { frm.trigger("calculate_shipping_period"); },

    // UPDATE COUNTRY OF DESTINATION FROM PORT
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
    },

    // CALCULATE SHIPPING PERIOD MONTHS
    calculate_shipping_period(frm) {
        let start = frm.doc.custom_shipment_period_start;
        let end = frm.doc.custom_shipment_period_end;

        if (start && end) {
            let startDate = frappe.datetime.str_to_obj(start);
            let endDate = frappe.datetime.str_to_obj(end);

            let years = endDate.getFullYear() - startDate.getFullYear();
            let months = endDate.getMonth() - startDate.getMonth();

            let totalMonths = years * 12 + months + 1;
            if (totalMonths < 0) totalMonths = 0;

            frm.set_value("custom_shipping_period", totalMonths + " Months");
        }
    },

    // UPDATE SIGNING AUTHORITY OPTIONS
    set_signing_authority_options(frm) {
        let options = [];

        if (frm.doc.custom_agent)
            options.push("Agent: " + frm.doc.custom_agent);

        if (frm.doc.customer_name)
            options.push("Buyer: " + frm.doc.customer_name);

        frm.set_df_property(
            "custom_signing_authority",
            "options",
            options.join("\n")
        );
    }
});


// INSURANCE FIELD SHOW/HIDE FUNCTION
function toggle_other_insurance_field(frm) {
    if (frm.doc.custom_insurance === "Other (Specify)") {
        frm.set_df_property("custom_specify_other_insurance_term", "hidden", false);
    } else {
        frm.set_df_property("custom_specify_other_insurance_term", "hidden", true);
        frm.set_value("custom_specify_other_insurance_term", "");
    }
}



// SALES ORDER ITEM SCRIPT (SECOND SCRIPT)
frappe.ui.form.on("Sales Order Item", {
    pallet_size: function (frm, cdt, cdn) {
        frappe.run_serially([
            () => {
                let d = locals[cdt][cdn];
                frappe.model.set_value(cdt, cdn, "total_pallets", Math.round(d.qty / d.pallet_size));
            },
            () => {
                frm.events.pallet_cal(frm);
            }
        ]);
    },

    qty: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if(d.qty > 0 && d.packing_size > 0){
            frappe.model.set_value(cdt, cdn, "no_of_packages", flt(d.qty / d.packing_size));
        }
    },

    packing_size: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.qty > 0 && d.packing_size > 0){
            frappe.model.set_value(cdt, cdn, "no_of_packages", flt(d.qty / d.packing_size));
        }
    },

    no_of_packages: function (frm, cdt, cdn) {
        frm.events.box_cal(frm);
        frm.events.cal_total(frm);
    },



    // ADDITIONAL SCRIPT (ITEM TEMPLATE MATCHING)
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        // Get Item Group of selected Item
        frappe.db.get_value("Item", row.item_code, "item_group")
            .then(r => {
                let item_group = r.message.item_group;
                if (!item_group) return;

                // Get matching Variable Template
                frappe.db.get_list("Variable Template", {
                    fields: ["name"],
                    filters: { item_group: item_group },
                    limit: 1
                }).then(res => {
                    if (res && res.length > 0) {

                        // Avoid infinite loop
                        if (frm.doc.custom_product !== res[0].name) {
                            frm._template_loaded_for = null;
                            frm.set_value("custom_product", res[0].name);
                        }
                    }
                });
            });
    }
});
