
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

        // PORT FILTERS
        // frm.set_query("port_of_loading", () => ({
        //     filters: { custom_is_in_india: 1 }
        // }));

        // frm.set_query("port_of_discharge", () => ({
        //     filters: { custom_is_in_india: 0 }
        // }));

        // frm.trigger("set_signing_authority_options");
        // frm.trigger("calculate_shipping_period");
        // toggle_other_insurance_field(frm);
    // },


 
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

// -----------------------------------------------------------------------------------------------------------------------------


cur_frm.cscript.onload = function (frm) {
    // Billing Address Filter
    cur_frm.set_query("customer_address", function () {
        return {
            query: "frappe.contacts.doctype.address.address.address_query",
            filters: { link_doctype: "Customer", link_name: cur_frm.doc.customer }
        };
    });

    // // Shipping Address Filter
    // cur_frm.set_query("shipping_address_name", function () {
    //     return {
    //         query: "frappe.contacts.doctype.address.address.address_query",
    //         filters: { }
    //     };
    // });

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





    // REFRESH FUNCTION
    refresh(frm) {
        console.log('888888888')
        if (!in_list(["Closed", "Completed"], frm.doc.status)) {
            console.log('kkkkkkkkk')
            if (frm.doc.docstatus == 1) {
                frm.add_custom_button(__("Contract Term"), function () {
                    frappe.model.open_mapped_doc({
                        method: "cit_exim.api.make_lc",
                        frm: cur_frm
                    })
                }, __("Create"))
            }
        }
        // AUTO SET START AND END DATES
        if (frm.doc.transaction_date && !frm.doc.custom_shipment_period_start) {
            frm.set_value("custom_shipment_period_start", frm.doc.transaction_date);
        }
        if (frm.doc.delivery_date && !frm.doc.custom_shipment_period_end) {
            frm.set_value("custom_shipment_period_end", frm.doc.delivery_date);
        }


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

        // frm.trigger("set_signing_authority_options");
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



});





// -------------------------------------------------------------------------------
//  SET THE PRODUCER
// --------------------------------------------------------------------------------
frappe.ui.form.on('Sales Order', {
    onload(frm) {
        // Hide your actual table
        frm.set_df_property('custom_producer_table', 'hidden', 1);
        fetch_producers(frm);
    },
    refresh(frm) {
        render_producer_html(frm);
    }
});

function fetch_producers(frm) {
    frappe.call({
        method: "cit_exim.cit_exim.doc_events.sales_order.get_producers",
        callback: function(r) {
            if (r.message) {
                const existing = frm.doc.custom_producer_table?.map(r => r.producer) || [];

                r.message.forEach(p => {
                    if (!existing.includes(p.name)) {
                        let row = frm.add_child("custom_producer_table");
                        row.producer = p.name;
                        row.selected = 0;
                    }
                });

                frm.refresh_field("custom_producer_table");
                render_producer_html(frm);
            }
        }
    });
}

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
            gap: 55px;
        ">
    `;

    frm.doc.custom_producer_table.forEach((row) => {
        html += `
            <div style="flex:0 0 45%; display:flex; flex-direction:column;">
                <div style="display:flex; align-items:center;">
                    <input type="checkbox" data-producer="${row.producer}" ${row.selected ? 'checked' : ''}>
                    <label style="margin-left:5px;">${row.producer}</label>
                </div>

                ${
                    row.address
                    ? `<div style="font-size:12px; color:#555; margin-left:20px;">${row.address}</div>`
                    : ``
                }
            </div>
        `;
    });

    html += '</div>';
    frm.fields_dict.custom_producer_list.$wrapper.html(html);

    // Checkbox event
    frm.fields_dict.custom_producer_list.$wrapper
        .off('change', 'input[type="checkbox"]')
        .on('change', 'input[type="checkbox"]', function () {
            const name = $(this).data('producer');
            const checked = $(this).is(':checked');

            const row = frm.doc.custom_producer_table.find(r => r.producer === name);
            if (row) {
                frappe.model.set_value(row.doctype, row.name, 'selected', checked);
            }

            frm.refresh_field('custom_producer_table');
        });
}



// frappe.ui.form.on("Sales Order", {
//     customer: function(frm) {
//         frm.set_query("custom_consignee", function() {
//             return {
//                 query: "cit_exim.cit_exim.doc_events.sales_order.get_consignee_list",
//                 filters: {
//                     // customer: frm.doc.customer
//                 }
//             };
//         });
//     }
// });



// /////////////////////////////////////////Address changing based on Buyer and consignee//////////////////////////////////////////////////////////////


// /////////////////////////////////////////////////////////////////////////////

// frappe.ui.form.on("Sales Order", {
//     custom_consignee: function(frm) {
//         if (!frm.doc.custom_consignee) {
//             frm.set_value("shipping_address_name", "");
//             return;
//         }

//         frappe.call({
//             method: "cit_exim.cit_exim.doc_events.sales_order.get_customer_shipping_address",
//             args: {
//                 customer: frm.doc.customer
//             },
//             callback: function(r) {
//                 if (r.message) {
//                     frm.set_value("shipping_address_name", r.message);
//                 } else {
//                     frm.set_value("shipping_address_name", "");
//                     frappe.msgprint({
//                         title: "Shipping Address",
//                         message: "No Shipping Address found for this Consignee",
//                         indicator: "orange"
//                     });
//                 }
//             }
//         });
//     }
// });






// frappe.ui.form.on("Sales Order", {

//     setup: function(frm) {

//         // Filter Shipping Address based on Consignee
//         frm.set_query("shipping_address_name", function() {

//             if (!frm.doc.custom_consignee) {
//                 return {};
//             }

//             return {
//                 query: "frappe.contacts.doctype.address.address.address_query",
//                 filters: {
//                     link_doctype: "Customer",
//                     link_name: frm.doc.custom_consignee
//                 }
//             };
//         });

//     },

//     custom_consignee: function(frm) {

//         // clear old address
//         frm.set_value("shipping_address_name", "");
//         frm.set_value("shipping_address", "");

//         if (frm.doc.custom_consignee) {

//             frappe.call({
//                 method: "cit_exim.cit_exim.doc_events.sales_order.get_consignee_default_address",
//                 args: {
//                     customer: frm.doc.custom_consignee
//                 },
//                 callback: function(r) {

//                     if (r.message) {
//                         frm.set_value("shipping_address_name", r.message.name);
//                         frm.set_value("shipping_address", r.message.display);
//                     }

//                 }
//             });

//         }

//     },

//     shipping_address_name: function(frm) {

//         if (frm.doc.shipping_address_name) {

//             frappe.call({
//                 method: "frappe.contacts.doctype.address.address.get_address_display",
//                 args: {
//                     address_dict: frm.doc.shipping_address_name
//                 },
//                 callback: function(r) {

//                     if (r.message) {
//                         frm.set_value("shipping_address", r.message);
//                     }

//                 }
//             });

//         }

//     }

// });





frappe.ui.form.on("Sales Order", {
    custom_is_consignee_same_as_buyer(frm) {
        if (!frm.doc.customer) {
            frappe.msgprint("Please select a customer first.");
            frm.set_value("custom_is_consignee_same_as_buyer", 0);
            return;
        }

        if (frm.doc.custom_is_consignee_same_as_buyer) {
            frappe.call({
                method: "cit_exim.cit_exim.doc_events.sales_order.get_billing_address_for_customer",

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


// --------------------------------------+++++++++++++++++++++------------------------------------




// frappe.ui.form.on('Sales Order', {
//     custom_map_address: function(frm) {
//         let buyer = frm.doc.customer || frm.doc.buyer; 
//         let consignee = frm.doc.custom_consignee;

//         if (!buyer || !consignee) {
//             frappe.msgprint(__('Please ensure both Buyer and Custom Consignee are selected.'));
//             return;
//         }

//         // 1. Find the Address tied to the Consignee
//         frappe.call({
//             method: 'frappe.client.get_list',
//             args: {
//                 doctype: 'Address',
//                 filters: [
//                     ['Dynamic Link', 'link_name', '=', consignee],
//                     ['Dynamic Link', 'parenttype', '=', 'Address']
//                 ],
//                 fields: ['name']
//             },
//             callback: function(r) {
//                 if (r.message && r.message.length > 0) {
//                     let address_id = r.message[0].name;
//                     update_address_and_map(frm, address_id, buyer);
//                 } else {
//                     frappe.msgprint(__('No Address found linked to Consignee: ') + consignee);
//                 }
//             }
//         });
//     }
// });

// function update_address_and_map(frm, address_id, buyer_name) {
//     frappe.call({
//         method: 'frappe.client.get',
//         args: {
//             doctype: 'Address',
//             name: address_id
//         },
//         callback: function(r) {
//             let address_doc = r.message;
            
//             // 2. Check if the "Buyer" is already in the Links table
//             let is_linked = (address_doc.links || []).some(l => l.link_name === buyer_name && l.link_doctype === 'Customer');

//             if (!is_linked) {
//                 // 3. Explicitly push a new row into the links child table
//                 if (!address_doc.links) address_doc.links = [];
                
//                 address_doc.links.push({
//                     "doctype": "Dynamic Link",
//                     "parent": address_id,
//                     "parentfield": "links",
//                     "parenttype": "Address",
//                     "link_doctype": "Customer",
//                     "link_name": buyer_name
//                 });

//                 // 4. Save the Address doc with the new link
//                 frappe.call({
//                     method: 'frappe.client.save',
//                     args: { doc: address_doc },
//                     callback: function(save_res) {
//                         if (save_res.message) {
//                             console.log("Address updated with new link:", save_res.message);
//                             apply_to_so(frm, save_res.message);
//                         }
//                     }
//                 });
//             } else {
//                 // Link already exists, just perform the mapping
//                 apply_to_so(frm, address_doc);
//             }
//         }
//     });
// }

// function apply_to_so(frm, address_doc) {
//     // 5. Map values back to Sales Order
//     frm.set_value('shipping_address_name', address_doc.name);
//     frm.set_value('shipping_address', address_doc.address_display);
    
//     frappe.show_alert({
//         message: __('Buyer linked to Address and mapped to Shipping fields.'), 
//         indicator: 'green'
//     });
// }


// ---------------------------------------------corrected code------------------------------------------------
// frappe.ui.form.on('Sales Order', {
//     custom_map_address: function(frm) {

//         let buyer = frm.doc.customer || frm.doc.buyer;
//         let consignee = frm.doc.custom_consignee;

//         if (!buyer || !consignee) {
//             frappe.msgprint(__('Please ensure both Buyer and Custom Consignee are selected.'));
//             return;
//         }

//         frappe.call({
//             method: 'cit_exim.cit_exim.doc_events.sales_order.map_buyer_to_consignee_address',
//             args: {
//                 buyer: buyer,
//                 consignee: consignee
//             },
//             callback: function(r) {
//                 if (r.message) {

//                     frm.set_value('shipping_address_name', r.message.shipping_address_name);
//                     frm.set_value('shipping_address', r.message.shipping_address);

//                     frappe.show_alert({
//                         message: __('Address mapped successfully'),
//                         indicator: 'green'
//                     });
//                 }
//             }
//         });
//     }
// });


frappe.ui.form.on('Sales Order', {

    custom_map_address: function(frm) {

        let buyer = frm.doc.customer || frm.doc.buyer;
        let consignee = frm.doc.custom_consignee;

        if (!buyer || !consignee) {
            frappe.msgprint(__('Please ensure both Buyer and Consignee are selected.'));
            return;
        }

        frappe.call({
            method: 'cit_exim.cit_exim.doc_events.sales_order.map_buyer_to_consignee_address',
            args: {
                buyer: buyer,
                consignee: consignee
            },
            callback: function(r) {
                if (r.message) {

                    // Shipping → Consignee
                    frm.set_value('shipping_address_name', r.message.shipping_address_name);
                    frm.set_value('shipping_address', r.message.shipping_address);

                    // Billing → Buyer
                    frm.set_value('customer_address', r.message.customer_address);
                    frm.set_value('address_display', r.message.address_display);

                    frappe.show_alert({
                        message: __('Shipping = Consignee, Billing = Buyer'),
                        indicator: 'green'
                    });
                }
            }
        });
    }
});













// ================================
//  LOADING THE TEMPLATES 
// ================================
function load_variable_template(frm, template_name) {

    if (!template_name) {
        frm.clear_table("custom_quality_and_specification");
        frm.refresh_field("custom_quality_and_specification");
        frm.set_value("custom_specification_details", "");
        frm.set_value("custom_shelf_life_condition","");
        frm._template_loaded_for = null;
        return;
    }

    // Prevent duplicate reload
    if (frm._template_loaded_for === template_name) return;
    frm._template_loaded_for = template_name;

    frm.clear_table("custom_quality_and_specification");

    frappe.db.get_doc("Variable Template", template_name)
        .then(doc => {

            // ===============================
            // EXISTING CHILD TABLE LOGIC
            // ===============================
            (doc.lab_variable || []).forEach(row => {
                let child = frm.add_child("custom_quality_and_specification");
                child.test = row.test;
                child.value = row.value;
            });

            frm.refresh_field("custom_quality_and_specification");

            // ===============================
            //  NEW ADDITION (SPECIFICATION)
            // ===============================
            frm.set_value(
                "custom_specification_details",
                doc.specification_details || ""
            );
            frm.set_value(
                "custom_shelf_life_condition",
                doc.shelf_life_condition || ""
            );
            
        });
}




// ================================
// LOAD FROM ITEM (Child Table)
// ================================
frappe.ui.form.on("Sales Order Item", {
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
frappe.ui.form.on("Sales Order", {
    custom_product(frm) {
        load_variable_template(frm, frm.doc.custom_product);
    }
});


// FETCH THE DOCUMENTS FROM DOCUMENT DOC

frappe.ui.form.on("Sales Order", {

    custom_document: function (frm) {
        
        
        // Clear existing rows
        frm.clear_table("custom_document_list");
        frm.refresh_field("custom_document_list");

        if (!frm.doc.custom_document) {
            return;
        }

        frappe.db.get_doc("Document", frm.doc.custom_document)
            .then(doc => {

                if (!doc.documents || doc.documents.length === 0) {
                    frappe.msgprint("No documents found in selected Document");
                    return;
                }

                doc.documents.forEach(d => {
                    let row = frm.add_child("custom_document_list");
                    row.document_name = d.document_name;
                });

                frm.refresh_field("custom_document_list");
            })
            .catch(err => {
                console.error(err);
                frappe.msgprint("Failed to fetch Document");
            });
    }

});

// FETCH CONTAMINATION DETAILS FROM CONTAMINATION DOC


frappe.ui.form.on("Sales Order", {
    custom_contamination: function(frm) {
        if (!frm.doc.custom_contamination) {
            frm.set_value("custom_contamination_details", "");
            return;
        }

        frappe.db.get_value(
            "Contamination",
            frm.doc.custom_contamination,
            "contamination_details",   // <-- field name in Contamination doctype
            function(r) {
                if (r && r.contamination_details) {
                    frm.set_value(
                        "custom_contamination_details",
                        r.contamination_details
                    );
                } else {
                    frm.set_value("custom_contamination_details", "");
                }
            }
        );
    }
});


// //FETCH THE OTHER CONDITIONS 

frappe.ui.form.on("Sales Order", {
    custom_other_conditions: function(frm) {

        // Clear target field if link is empty
        if (!frm.doc.custom_other_conditions) {
            frm.set_value("custom_description_of_conditions", "");
            return;
        }

        frappe.db.get_value(
            "Other Conditions",
            frm.doc.custom_other_conditions,
            "description_of_conditions",
            function(r) {
                if (r && r.description_of_conditions) {
                    frm.set_value(
                        "custom_description_of_conditions",
                        r.description_of_conditions
                    );
                } else {
                    frm.set_value("custom_description_of_conditions", "");
                }
            }
        );
    }
});


//FETCH PACKING DETAILS FROM ITEM MASTER
frappe.ui.form.on("Sales Order Item", {
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

                // Set values in Sales Contract (parent)
                frm.set_value(
                    "custom_packing_template",
                    r.message.custom_name_of_packing
                );

                frm.set_value(
                    "custom_packing_detailsfor_sales_contract",
                    r.message.custom_packing_detailsfor_sales_contract
                );
                 frm.set_value(
                    "custom_packing_detailsfor_sales_invoice",
                    r.message.custom_details_of_packing
                );
            }
        });
    }
});




// FECTH SHIPPING INSTRUCTION 

frappe.ui.form.on("Sales Order", {
    custom_shipping_instruction: function(frm) {

        // Clear target field if link is empty
        if (!frm.doc.custom_shipping_instruction) {
            frm.set_value("custom_description_of_instruction", "");
            return;
        }

        frappe.db.get_value(
            "Shipping Instruction",
            frm.doc.custom_shipping_instruction,
            "description_of_instruction",
            function(r) {
                if (r && r.description_of_instruction) {
                    frm.set_value(
                        "custom_description_of_instruction",
                        r.description_of_instruction
                    );
                } else {
                    frm.set_value("custom_description_of_instruction", "");
                }
            }
        );
    }
});


//code of shipment 

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        let currentYear = new Date().getFullYear();

        let options = [
            currentYear.toString(),
            (currentYear + 1).toString(),
            (currentYear + 2).toString()
        ];

        if (frm.fields_dict.custom_shipment_schedule) {
            frm.fields_dict.custom_shipment_schedule.grid.update_docfield_property(
                'fiscal_year',
                'options',
                options.join('\n')
            );
        }
    }
});

// Triggered specifically when a row is added to the child table
frappe.ui.form.on('Shipment Schedule Child Table', {
    custom_shipment_schedule_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.fiscal_year = new Date().getFullYear().toString();
        frm.refresh_field('custom_shipment_schedule');
    }
});



// frappe.ui.form.on("Sales Order", {
//     refresh(frm) {

//         // Prevent duplicate loading
//         if (frm.doc.custom_banks && frm.doc.custom_banks.length) {
//             return;
//         }

//         frappe.db.get_list("Bank", {
//             fields: ["name"],
//             limit: 0
//         }).then(banks => {

//             frm.clear_table("custom_banks");

//             banks.forEach(bank => {
//                 let row = frm.add_child("custom_banks");
//                 row.bank = bank.name;
//             });

//             frm.refresh_field("custom_banks");
//         });
//     }
// });

// show corresponding item from fetched item group

frappe.ui.form.on("Sales Order", {
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

frappe.ui.form.on('Sales Order', {
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





// ---------------------------------------------------------------------------------------------------------------------



frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {

        // Only show button if the Sales Order is submitted
        if (frm.doc.docstatus === 1) {

            if (frm.doc.custom_is_loading_from_mudra_port == 1) {

                // Remove default Create Invoice button
                frm.remove_custom_button('Sales Invoice', 'Create');

                frm.add_custom_button(__('Consolidated Sales Invoice'), function() {
                    create_consolidated_invoice(frm);
                }, __('Create'));
            }
        }
    }
});

function create_consolidated_invoice(frm) {
    // 1. Fetch Company defaults for Item rows
    frappe.db.get_value('Company', frm.doc.company, ['default_income_account', 'cost_center'], (company_data) => {
        let default_income = company_data ? company_data.default_income_account : null;
        let default_cost_center = company_data ? company_data.cost_center : null;

        // 2. Fetch Customer Account (Debit To)
        frappe.db.get_doc('Customer', frm.doc.customer).then(customer_doc => {
            let debit_to_account = null;
            if (customer_doc.accounts) {
                let account_row = customer_doc.accounts.find(acc => acc.company === frm.doc.company);
                if (account_row) {
                    debit_to_account = account_row.account;
                }
            }

            // 3. Initialize the New Document
            frappe.model.with_doctype('Consolidated Sales Invoice', function() {
                var new_doc = frappe.model.get_new_doc('Consolidated Sales Invoice');

                // Header Mapping
                new_doc.customer = frm.doc.customer;
                new_doc.company = frm.doc.company;
                new_doc.debit_to = debit_to_account;
                new_doc.sales_contract = frm.doc.name; // Mapping SO to Header field

                // Logistics & Terms
                new_doc.custom_loading_point = frm.doc.custom_loading_point;
                new_doc.port_of_loading = frm.doc.port_of_loading;
                new_doc.shipping_terms = frm.doc.shipping_terms;
                new_doc.port_of_discharge = frm.doc.port_of_discharge;
                new_doc.pre_carriage_by = frm.doc.pre_carriage_by;
                new_doc.custom_carriage_by = frm.doc.custom_carriage_by;
                new_doc.custom_product = frm.doc.custom_product;
                new_doc.custom_quality_and_specification = frm.doc.custom_quality_and_specification;
                new_doc.payment_terms_template = frm.doc.payment_terms_template;
                new_doc.tc_name = frm.doc.tc_name;
                new_doc.terms = frm.doc.terms;

                // Totals & Currency
                new_doc.currency = frm.doc.currency;
                new_doc.conversion_rate = frm.doc.conversion_rate;
                new_doc.selling_price_list = frm.doc.selling_price_list;
                new_doc.base_grand_total = frm.doc.base_grand_total;
                new_doc.base_in_words = frm.doc.base_in_words;
                new_doc.grand_total = frm.doc.grand_total;
                new_doc.in_words = frm.doc.in_words;
                new_doc.total_advance = frm.doc.total_advance;
                new_doc.outstanding_amount = frm.doc.outstanding_amount;
                new_doc.disable_rounded_total = frm.doc.disable_rounded_total;
                new_doc.total_qty = frm.doc.total_qty;
                new_doc.total_net_weight = frm.doc.total_net_weight;
                new_doc.base_total = frm.doc.base_total;
                new_doc.base_net_total = frm.doc.base_net_total;
                new_doc.total = frm.doc.total;
                new_doc.net_total = frm.doc.net_total;
                new_doc.branch = frm.doc.branch;
                new_doc.plc_conversion_rate = frm.doc.conversion_rate;
                new_doc.custom_producer_list = frm.doc.custom_producer_list;
                new_doc.custom_producer_table = frm.doc.custom_producer_table;

                // Address & GST
                new_doc.customer_address = frm.doc.customer_address;
                new_doc.address_display = frm.doc.address_display;
                new_doc.gst_category = frm.doc.gst_category;
                new_doc.place_of_supply = frm.doc.place_of_supply;
                new_doc.shipping_address_name = frm.doc.shipping_address_name;
                new_doc.shipping_address = frm.doc.shipping_address;
                new_doc.company_address = frm.doc.company_address;
                new_doc.company_address_display = frm.doc.company_address_display;
                new_doc.company_gstin = frm.doc.company_gstin;

                // Custom Tracking Fields
                new_doc.custom_item_group = frm.doc.custom_item_group;
                new_doc.custom_consignee = frm.doc.custom_consignee;
                new_doc.custom_agent = frm.doc.custom_agent;
                new_doc.custom_producer_list = frm.doc.custom_producer_list;
                new_doc.custom_packing_template = frm.doc.custom_packing_template;
                new_doc.custom_packing_detailsfor_sales_invoice = frm.doc.custom_packing_detailsfor_sales_invoice;
                new_doc.tc_name = frm.doc.tc_name
                new_doc.terms = frm.doc.terms
                

                // 4. Items Child Table Mapping
                if (frm.doc.items) {
                    frm.doc.items.forEach(item => {
                        let row = frappe.model.add_child(new_doc, 'items');
                        
                        // Reference to Source Sales Order
                        row.sales_order = frm.doc.name; // This maps the SO name to the row
                        row.so_detail = item.name;     // This maps the specific row ID
                        
                        // Item Details
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.qty = item.qty;
                        row.uom = item.uom;
                        row.stock_uom = item.stock_uom;
                        row.conversion_factor = item.conversion_factor;
                        row.warehouse = item.warehouse;
                        row.gst_hsn_code = item.gst_hsn_code;
                        row.stock_qty = item.qty * item.conversion_factor;
                        row.gst_hsn_code = item.gst_hsn_code

                        
                        // Pricing & Accounts
                        row.rate = item.rate;
                        row.amount = item.amount;
                        row.base_rate = item.base_rate;
                        row.base_amount = item.base_amount;
                        row.net_rate = item.net_rate;
                        row.net_amount = item.net_amount;
                        row.base_net_rate = item.base_net_rate;
                        row.base_net_amount = item.base_net_amount;
                        row.taxable_value = item.taxable_value;
                        
                        row.income_account = item.income_account || default_income;
                        row.cost_center = item.cost_center || default_cost_center;
                    });
                }

                // 5. Payment Schedule Mapping
                if (frm.doc.payment_schedule) {
                    frm.doc.payment_schedule.forEach(ps => {
                        let row = frappe.model.add_child(new_doc, 'payment_schedule');
                        row.payment_term = ps.payment_term;
                        row.description = ps.description;
                        row.due_date = ps.due_date;
                        row.invoice_portion = ps.invoice_portion;
                        row.payment_amount = ps.payment_amount;
                    });
                }

                // 6. Route to the new Consolidated Invoice
                frappe.set_route('Form', 'Consolidated Sales Invoice', new_doc.name);
            });
        })
    });
}









// frappe.ui.form.on('Sales Order', {
//     payment_terms_template: function(frm) {
//         if (frm.doc.payment_terms_template) {
//             // We use a short delay (200ms) to let the standard ERPNext 
//             // template logic finish before we inject our custom data.
//             setTimeout(() => {
//                 frappe.db.get_doc('Payment Terms Template', frm.doc.payment_terms_template)
//                     .then(template => {
                        
//                         // Loop through the rows already created by ERPNext
//                         // or create them if the table is empty
//                         if (!frm.doc.payment_schedule || frm.doc.payment_schedule.length === 0) {
//                             template.terms.forEach(term => {
//                                 if (term.due_date_based_on === "Day(s) after Sales Contract date") {
//                                     let child = frm.add_child('payment_schedule');
//                                     child.payment_term = term.payment_term;
//                                     child.invoice_portion = term.invoice_portion;
//                                     child.custom_days = term.custom_days;
//                                 }
//                             });
//                         } else {
//                             // If rows already exist (from ERPNext standard logic), 
//                             // we just update the custom_days field in the matching row.
//                             frm.doc.payment_schedule.forEach((row, index) => {
//                                 let template_term = template.terms[index];
//                                 if (template_term && template_term.due_date_based_on === "Day(s) after Sales Contract date") {
//                                     // Use model.set_value to ensure the UI updates correctly
//                                     frappe.model.set_value(row.doctype, row.name, 'custom_days', template_term.custom_days);
//                                 }
//                             });
//                         }
                        
//                         frm.refresh_field('payment_schedule');
//                     });
//             }, 500); // 500ms delay is usually enough to beat the core script
//         }
//     }
// });




frappe.ui.form.on('Sales Order', {
    payment_terms_template: function(frm) {
        if (frm.doc.payment_terms_template) {
            
            setTimeout(() => {
                frappe.db.get_doc('Payment Terms Template', frm.doc.payment_terms_template)
                    .then(template => {
                        
                        // If the table was empty, we build it
                        if (!frm.doc.payment_schedule || frm.doc.payment_schedule.length === 0) {
                            template.terms.forEach(term => {
                                if (term.due_date_based_on === "Day(s) after Sales Contract date") {
                                    let child = frm.add_child('payment_schedule');
                                    child.payment_term = term.payment_term;
                                    child.invoice_portion = term.invoice_portion;
                                    child.custom_days = term.custom_days;

                                    // Calculate Due Date: transaction_date + custom_days
                                    if (frm.doc.transaction_date && term.custom_days) {
                                        child.due_date = frappe.datetime.add_days(frm.doc.transaction_date, term.custom_days);
                                    }
                                }
                            });
                        } else {
                            // If rows exist, we update custom_days and due_date
                            frm.doc.payment_schedule.forEach((row, index) => {
                                let template_term = template.terms[index];
                                
                                if (template_term && template_term.due_date_based_on === "Day(s) after Sales Contract date") {
                                    
                                    // 1. Set the Custom Days
                                    frappe.model.set_value(row.doctype, row.name, 'custom_days', template_term.custom_days);
                                    
                                    // 2. Calculate and set the Due Date
                                    if (frm.doc.transaction_date && template_term.custom_days) {
                                        let new_due_date = frappe.datetime.add_days(frm.doc.transaction_date, template_term.custom_days);
                                        frappe.model.set_value(row.doctype, row.name, 'due_date', new_due_date);
                                    }
                                }
                            });
                        }
                        
                        frm.refresh_field('payment_schedule');
                    });
            }, 500);
        }
    }
});




