// Copyright (c) 2025, craft and contributors
// For license information, please see license.txt
frappe.ui.form.on("Vehicle Queue", {
    refresh: function(frm) {
        calculate_totals(frm);
    }
});
frappe.ui.form.on("Vehicle Queue Item", {
    no_of_bags: function(frm) {
        calculate_totals(frm);
        // calculate_totals_non_rawfish(frm);
    },
    item_add: function(frm) {
        calculate_totals(frm);
        // calculate_totals_non_rawfish(frm);
    },

    item_remove: function(frm) {
        calculate_totals(frm);
        // calculate_totals_non_rawfish(frm);
    }
});
function calculate_totals(frm) {
    let total_boxes = 0;
    let total_amount = 0;

    (frm.doc.item || []).forEach(row => {
        total_boxes += row.no_of_bags || 0;
    });

    frm.set_value("total_no_of_boxes", total_boxes);


    frm.refresh_field("total_no_of_boxes");

}
// function calculate_totals_non_rawfish(frm) {

//     let item_map = {};

//     (frm.doc.item || []).forEach(row => {

//         // Skip if no item or raw fish
//         if (!row.item || row.item_group === "Raw Fish") {
//             return;
//         }

//         let key = row.unit;  // grouping by item

//         if (!item_map[key]) {
//             item_map[key] = {
//                 item: row.item,
//                 unit: row.unit,
//                 total: 0
//             };
//         }

//         item_map[key].total += row.no_of_bags || 0;
//     });

//     // Clear existing child table
//     frm.clear_table("total");

//     // Rebuild child table
//     Object.values(item_map).forEach(data => {
//         let child = frm.add_child("total");

//         child.unit = data.unit;   // make sure field exists
//         child.total_number = data.total;
//     });

//     frm.refresh_field("total");
// }
frappe.ui.form.on("Vehicle Queue", {
    gross_weight: function(frm) {
        calculate_net_weight(frm);
    },
    tare_weight: function(frm) {
        calculate_net_weight(frm);
    },
    ice_weight: function(frm) {
        calculate_net_weight(frm);
    },
    total_no_of_boxes: function(frm) {
        update_avg_per_box(frm);
    },
    company: function (frm) {
        if (frm.doc.company) {
            frm.set_query("warehouse", function () {
                return {
                    filters: {
                        company: frm.doc.company
                    }
                };
            });
        } else {
            // Clear warehouse if company is removed
            frm.set_value("warehouse", null);
        }
    }
});

function update_avg_per_box(frm) {

    let net = frm.doc.net_weight || 0;
    let total_boxes = frm.doc.total_no_of_boxes || 0;

    if (total_boxes <= 0) return;

    let avg = net / total_boxes;

    // ITEM TABLE ONLY
    (frm.doc.item || []).forEach(row => {

        // set avg_per_box
        frappe.model.set_value(row.doctype, row.name, "avg_per_box", avg);

        // calculate net_wt = no_of_boxes * avg_per_box
        let nb = row.no_of_bags || 0;
        frappe.model.set_value(row.doctype, row.name, "net_wt", nb * avg);

    });
}

function calculate_net_weight(frm) {

    let gross = frm.doc.gross_weight || 0;
    let tare = frm.doc.tare_weight || 0;
    let ice = frm.doc.ice_weight || 0;
    console.log(434444444)
    let net = gross - tare - ice;

    frappe.model.set_value(
        frm.doctype,
        frm.doc.name,
        "net_weight",
        net
    );

    update_avg_per_box(frm);
}




frappe.ui.form.on("Vehicle Queue", {
    product: function (frm) {

        // If no Item Group selected, remove filter
        if (!frm.doc.product) {

            // Item table
            frm.set_query("item", "item", function () {
                return {};
            });

            // Mixed Items table
            frm.set_query("item", "mixed_items", function () {
                return {};
            });

            return;
        }

        // Filter for Item table
        // frm.set_query("item", "item", function () {
        //     return {
        //         filters: {
        //             item_group: frm.doc.product,
        //             disabled: 0
        //         }
        //     };
        // });

        //  Added filter for Mixed Items table
        frm.set_query("item", "mixed_items", function () {
            return {
                filters: {
                    item_group: frm.doc.product,
                    disabled: 0
                }
            };
        });
    }
});
frappe.ui.form.on("Vehicle Queue", {
    invoice_qty(frm) {
        calculate_difference(frm);
    },
    net_weight(frm) {
        calculate_difference(frm);
    }
});

function calculate_difference(frm) {
    let invoice_qty = frm.doc.invoice_qty || 0;
    let net_weight = frm.doc.net_weight || 0;

    frm.set_value("difference_in_qty", invoice_qty - net_weight);
}
// frappe.ui.form.on("Vehicle Queue", {
//   refresh(frm) {
//     if (frm.doc.docstatus === 0) {
//       frm.add_custom_button(
//         ("Purchase Order"),
//         () => {
//           if (!frm.doc.supplier) {
//             frappe.throw(("Please select Supplier"));
//           }

//           erpnext.utils.map_current_doc({
//             method: "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.make_vehicle_queue_from_po",
//             source_doctype: "Purchase Order",
//             target: frm,
//             setters: {
//               supplier: frm.doc.supplier,
//             },
//             get_query_filters: {
//               docstatus: 1,
//               status: ["not in", ["Closed", "On Hold"]],
//               supplier: frm.doc.supplier,
//               company: frm.doc.company,
//               per_received: ["<", 100]
//             },
//             allow_child_item_selection: true,
//             child_fieldname: "items",
//             child_columns: ["item_code", "item_name"],
//           });
//         },
//         __("Get Items From")
//       );
//     }
//   },
// });
frappe.ui.form.on("Vehicle Queue", {
    vehicle_no(frm) {
        if (frm.doc.vehicle_no) {
            frm.set_value(
                "vehicle_no",
                frm.doc.vehicle_no.replace(/\s+/g, "").toUpperCase()
            );
        }
    }
});
// frappe.ui.form.on("Vehicle Queue", {
//     refresh(frm) {
//         update_no_of_bags_label(frm);
//     },
//     product(frm) {
//         update_no_of_bags_label(frm);
//     }
// });

function update_no_of_bags_label(frm) {
    setTimeout(() => {
        if (!frm.fields_dict.item) return;

        const is_fish_meal = frm.doc.product === "RM-Fish Meal";

        // Get grid field
        const grid = frm.fields_dict.item.grid;

        // Change column label
        grid.update_docfield_property(
            "no_of_bags",
            "label",
            is_fish_meal ? "No of Bags" : "No of Boxes"
        );

        // Refresh grid to apply label change
        grid.refresh();
         frm.set_df_property(
            "total_no_of_boxes",
            "label",
            is_fish_meal ? "Total No.of Bags" : "Total No.of Boxes"
        );

        frm.refresh_field("total_no_of_boxes");

    }, 300);
}
frappe.ui.form.on("Vehicle Queue", {
    refresh(frm) {
        hide_fields_based_on_product(frm);
    },
    onload(frm) {
        hide_fields_based_on_product(frm);
    },
    product(frm) {
        hide_fields_based_on_product(frm);
    }
});

function hide_fields_based_on_product(frm) {

    let product = frm.doc.product;

    if (product === "Raw Fish") {

        frm.fields_dict["item"].grid.toggle_display("avg_per_box", true);
        frm.fields_dict["item"].grid.toggle_display("net_wt", true);
        frm.fields_dict["item"].grid.toggle_display("count", true);
        // frm.fields_dict["item"].grid.toggle_display("rate", false);


    } else {

        frm.fields_dict["item"].grid.toggle_display("avg_per_box", false);
        frm.fields_dict["item"].grid.toggle_display("net_wt", false);
        frm.fields_dict["item"].grid.toggle_display("count", false);

    }
}

frappe.ui.form.on("Vehicle Queue Item", {
    item: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (row.item) {

            // Fetch Item Group from Item master
            frappe.db.get_value("Item", row.item, "item_group")
                .then(r => {
                    if (r.message) {
                        
                        // Set Item Group into parent field "product"
                        frm.set_value("product", r.message.item_group);
                    }
                });
        }
    }
});

frappe.ui.form.on("Vehicle Queue", {
    refresh: function(frm) {
        calculate_and_append(frm);
    }
});

frappe.ui.form.on("Mixed Items Details", {

    percentage: function(frm, cdt, cdn) {
        calculate_and_append(frm);
    },

    noof_boxes: function(frm, cdt, cdn) {
        calculate_and_append(frm);
    },

    item: function(frm, cdt, cdn) {
        calculate_and_append(frm);
    },

    mixed_items_remove: function(frm, cdt, cdn) {

        // Get remaining mixed item names
        let remaining_items = (frm.doc.mixed_items || []).map(d => d.item);

        // Remove rows from item table not present in mixed_items
        frm.doc.item = (frm.doc.item || []).filter(d => {
            return remaining_items.includes(d.item);
        });

        frm.refresh_field("item");

        // Recalculate total
        calculate_total(frm);
    }
});


function calculate_and_append(frm) {

    if (!frm.doc.mixed_items || frm.doc.mixed_items.length === 0) {
        calculate_total(frm);
        return;
    }

    frm.doc.mixed_items.forEach(row => {

        if (row.item && row.percentage && row.noof_boxes) {

            let calculated_boxes = (row.percentage / 100) * row.noof_boxes;

            let existing_row = (frm.doc.item || []).find(d => d.item === row.item);

            if (existing_row) {
                existing_row.no_of_bags = calculated_boxes;
            } else {
                let new_row = frm.add_child("item");
                new_row.item = row.item;
                new_row.no_of_bags = calculated_boxes;
                new_row.mixed_item = 1;
            }
        }
    });

    frm.refresh_field("item");

    // Calculate total after updating items
    calculate_total(frm);
}


function calculate_total(frm) {

    let total = 0;

    if (frm.doc.item && frm.doc.item.length > 0) {
        frm.doc.item.forEach(row => {
            total += flt(row.no_of_bags);
        });
    }

    frm.set_value("total_no_of_boxes", total);
}

// //////////////////Pop up//////////////////////////
frappe.ui.form.on("Vehicle Queue", {
    refresh(frm) {
        if (frm.doc.docstatus !== 0) return;

        frm.add_custom_button("Purchase Order", () => {
            if (!frm.doc.supplier) {
                frappe.throw("Please select Supplier");
            }

            const dialog = new frappe.ui.Dialog({
                title: "Select Purchase Order Items",
                size: "extra-large",
                fields: [
                    // {
                    //     // fieldtype: "Check",
                    //     // fieldname: "select_all",
                    //     // label: "Select All",
                    //     // onchange: function () {
                    //     //     const checked = dialog.get_value("select_all");
                    //     //     const grid = dialog.fields_dict.po_items.grid;

                    //     //     grid.df.data.forEach(row => {
                    //     //         row.select = checked;
                    //     //     });

                    //     //     grid.refresh();
                    //     // }
                    // },
                    {
                        fieldname: "po_items",
                        fieldtype: "Table",
                        cannot_add_rows: true,
                        in_place_edit: false,
                        fields: [
                            // {
                            //     fieldtype: "Link",
                            //     fieldname: "custom_default_receiving_uom",
                            //     label: "Receiving UOM",
                            //     columns: 1
                            // },
                            {
                                fieldtype: "Link",
                                fieldname: "purchase_order",
                                label: "PO Number",
                                options: "Purchase Order",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: "Date",
                                fieldname: "transaction_date",
                                label: "PO Date",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 1
                            },
                            {
                                fieldtype: "Data",
                                fieldname: "supplier",
                                label: "Supplier",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: "Link",
                                fieldname: "item_code",
                                label: "Item Code",
                                options: "Item",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: "Data",
                                fieldname: "item_name",
                                label: "Item Name",
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: "Float",
                                fieldname: "ordered_qty",
                                label: "Ordered Qty",
                                // in_list_view: 1,
                                read_only: 1,
                                columns: 1
                            },
                            {
                                fieldtype: "Float",
                                fieldname: "received_qty",
                                label: "Received Qty",
                                // in_list_view: 1,
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: "Currency",
                                fieldname: "rate",
                                label: "Price",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 1
                            },
                            {
                                fieldtype: "Float",
                                fieldname: "pending_qty",
                                label: "Pending Qty",
                                in_list_view: 1,
                                read_only: 1,
                                columns: 1
                            },
                            // {
                            //     fieldtype: "Float",
                            //     fieldname: "conversion_factor",
                            //     label: "Conversion Factor(KG)",
                            //     read_only:1,
                            //     columns:1
                            // }
                            
                        ]
                    }
                ],

                primary_action_label: "Add Items",
                primary_action() {
                    const grid = dialog.fields_dict.po_items.grid;
                    const selected = grid.get_selected_children();

                    if (!selected.length) {
                        frappe.msgprint("Please select at least one item");
                        return;
                    }

                    selected.forEach(row => {
                        let child = frm.add_child("item");
                        child.purchase_order = row.purchase_order;
                        // child.item = row.item_code;
                        frappe.model.set_value(child.doctype, child.name, "item", row.item_code);
                        frappe.model.set_value(child.doctype, child.name, "rate", row.rate);
                        // child.unit = row.custom_default_receiving_uom
                        // child.conversion_factor_kg = row.conversion_factor
                    });

                    // set product based on first item
                    frappe.db.get_value("Item", selected[0].item_code, "item_group")
                        .then(r => {
                        if (r && r.message) {
                            frm.set_value("product", r.message.item_group);
                        }
                        });

                    frm.refresh_field("item");
                    dialog.hide();
                    }
            });

            // 🔥 IMPORTANT FIXES
            setTimeout(() => {
                const grid = dialog.fields_dict.po_items.grid;

                // Show more columns
                grid.max_visible_columns = 30;

                // Enable scroll
                dialog.$wrapper.find('[data-fieldname="po_items"] .grid-body').css({
                    "overflow-x": "auto",
                    "overflow-y": "auto"
                });

                // Force width so horizontal scroll appears
                dialog.$wrapper.find('[data-fieldname="po_items"] .grid-body .rows').css({
                    "min-width": "1400px"
                });

                // Make headers sticky for horizontal scroll
                dialog.$wrapper.find('[data-fieldname="po_items"] .grid-header').css({
                    "position": "sticky",
                    "top": "0",
                    "z-index": "10",
                    "background": "white",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
                });

                // Dialog size tuning
                dialog.$wrapper.find('.modal-dialog').css({
                    "width": "95vw",
                    "max-width": "1400px"
                });

                dialog.$wrapper.find('.modal-body').css({
                    "max-height": "70vh",
                    "overflow": "auto"
                });

            }, 300);

            // Fetch data
            frappe.call({
                method: "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.get_pending_po_items",
                args: {
                    supplier: frm.doc.supplier,
                    company: frm.doc.company
                },
                callback(r) {
                    if (r.message?.length) {
                        dialog.fields_dict.po_items.df.data = r.message;
                        dialog.fields_dict.po_items.grid.refresh();
                        dialog.show();
                    } else {
                        frappe.msgprint("No pending Purchase Orders found");
                    }
                }
            });

        }, __("Get Items From"));
    }
});

frappe.ui.form.on("Vehicle Queue Item", {
  item(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!row.item) {
      row.product = "";
      frm.refresh_field("item");
      return;
    }

    frappe.db.get_value("Item", row.item, "item_group")
      .then(r => {
        if (r && r.message) {
          row.product = r.message.item_group;
          frm.refresh_field("item");
        }
      });
  }
});

frappe.ui.form.on("Vehicle Queue", {

    invoice_qty: function(frm) {
        calculate_supplier_invoice(frm);
        calculate_child_values(frm);
    },

    net_weight: function(frm) {
        calculate_child_values(frm);
    }

});

frappe.ui.form.on("Vehicle Queue Item", {

    rate: function(frm, cdt, cdn) {
        calculate_supplier_invoice(frm);
        calculate_child_values(frm);
    },
    supplier_invoiced_qty: function(frm) {
        calculate_supplier_invoice(frm);
    },
    item_add: function(frm) {
        calculate_supplier_invoice(frm);
    },
    item_remove: function(frm) {
        calculate_supplier_invoice(frm);
    },
    


});

function calculate_supplier_invoice(frm) {

    if (frm.doc.invoice_qty && frm.doc.item && frm.doc.item.length > 0) {
        (frm.doc.item || []).forEach(row => {
            if (row.rate) {
                let rate = row.rate || 0;
                let amount = frm.doc.invoice_qty * rate;

                frm.set_value("supplier_invoice_amount", amount);
            }
        });
    } 
    // else {
    //     let rate = frm.doc.item[0].rate || 0;
    //     let amount = frm.doc.invoice_qty * rate;

    //     frm.set_value("supplier_invoice_amount", amount);
    // }

}

function calculate_child_values(frm){

    let supplier_invoice_amount = frm.doc.supplier_invoice_amount || 0;
    let net_weight = frm.doc.net_weight || 0;

    let total_row_amount = 0;

    (frm.doc.item || []).forEach(function(row){

        let amount = net_weight * (row.rate || 0);

        frappe.model.set_value(row.doctype, row.name, "amount", amount);

        total_row_amount += amount;

    });

    frm.set_value("difference_in_amount", supplier_invoice_amount - total_row_amount);

}
frappe.ui.form.on('Vehicle Queue', {
    refresh: function(frm) {


        frm.fields_dict['item'].grid.get_field("unit").get_query = function(doc, cdt, cdn) {


            let row = locals[cdt][cdn];


            return {
                filters: {
                    item_group: row.item_group
                }
            };
        };
    },
    net_weight: function(frm) {

        if (!frm.doc.net_weight) return;

        (frm.doc.item || []).forEach(row => {

            frappe.model.set_value(
                row.doctype,
                row.name,
                'qty',
                frm.doc.net_weight
            );
        });

        frm.refresh_field('items');
    }        
});

frappe.ui.form.on('Vehicle Queue Item', {
    item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.item) {
            frappe.db.get_value('Item', row.item, 'item_group')
                .then(r => {
                    if (r.message) {

                        row.item_group = r.message.item_group;


                        // ✅ Apply row-wise filter
                        frm.fields_dict['item'].grid.get_field("unit").get_query = function(doc, cdt, cdn) {
                            let child = locals[cdt][cdn];

                            return {
                                filters: {
                                    item_group: child.item_group
                                }
                            };
                        };

                        frm.refresh_field('item');
                    }
                });
            frappe.db.get_value('Item', row.item, ['purchase_uom', 'stock_uom'])
                .then(r => {
                    if (r.message) {

                        let billing_uom = r.message.purchase_uom || r.message.stock_uom;

                        frappe.model.set_value(
                            cdt,
                            cdn,
                            'billing_uom',
                            billing_uom
                        );

                    }
                });
        }
    }
});

frappe.ui.form.on('Vehicle Queue Item', {
    purchase_order: function(frm, cdt, cdn) {
        calculate_po_details(frm, cdt, cdn);
    },
    item: function(frm, cdt, cdn) {
        calculate_po_details(frm, cdt, cdn);
    }
});

frappe.ui.form.on('Vehicle Queue', {
    net_weight: function(frm) {
        (frm.doc.item || []).forEach(row => {
            calculate_po_details(frm, row.doctype, row.name);
        });
    }
});

function calculate_po_details(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    if (!row.purchase_order || !row.item) return;

    frappe.call({
        method: "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.get_po_item_details",
        args: {
            purchase_order: row.purchase_order,
            item: row.item,
            net_weight: frm.doc.net_weight,
            product: row.product
        },
        callback: function(r) {

            if (!r.message) return;

            frappe.model.set_value(cdt, cdn, 'po_qty', r.message.po_qty);
            frappe.model.set_value(cdt, cdn, 'p_o_balance_qty', r.message.po_balance_qty);

        }
    });
    frm.refresh_field('items');

}