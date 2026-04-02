// Copyright (c) 2025, craft and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Consolidated Sales Invoice", {
// 	refresh(frm) {

// 	},
// });






frappe.ui.form.on("Consolidated Sales Invoice", {
	refresh(frm) {

	},
})
frappe.ui.form.on("Consolidated Sales Invoice Item", {
    item_code(frm, cdt, cdn) {
        console.log("helooooooooo");
    },

    pick_serial_and_batch(frm, cdt, cdn) {
    console.log("11111111111111");

    const item = locals[cdt][cdn];

    if (!frm || !frm.doc) {
        console.error("frm or frm.doc is missing");
        return;
    }

    if (!item.item_code) {
        frappe.msgprint(__("Please select Item first"));
        return;
    }

    frappe.db
        .get_value("Item", item.item_code, [
            "has_batch_no",
            "has_serial_no",
        ])
        .then((r) => {
            if (!r.message) return;

            if (!(r.message.has_batch_no || r.message.has_serial_no)) {
                return;
            }

            item.has_serial_no = r.message.has_serial_no;
            item.has_batch_no = r.message.has_batch_no;
            item.type_of_transaction =
                item.qty > 0 ? "Outward" : "Inward";

            item.title = item.has_serial_no
                ? __("Select Serial No")
                : __("Select Batch No");

            if (item.has_serial_no && item.has_batch_no) {
                item.title = __("Select Serial and Batch");
            }

            //  FIX START
            let conversion_factor = flt(item.conversion_factor || 1);

            let original_qty = item.qty;
            let converted_qty = original_qty * conversion_factor;

            item.qty = converted_qty;
            // FIX END

            new erpnext.SerialBatchPackageSelector(
                frm,
                item,
                (r) => {
                    if (!r) return;

                    let qty = Math.abs(r.total_qty);

                    if (frm.doc.is_return) {
                        qty = qty * -1;
                    }

                    //  Restore original qty
                    item.qty = original_qty;

                    frappe.model.set_value(item.doctype, item.name, {
                        serial_and_batch_bundle: r.name,
                        use_serial_batch_fields: 0,
                        incoming_rate: r.avg_rate,
                        qty:
                            qty /
                            flt(
                                item.conversion_factor || 1,
                                precision(
                                    "conversion_factor",
                                    item
                                )
                            ),
                    });
                }
            );
        });
},
});





frappe.ui.form.on('Consolidated Sales Invoice', {
    refresh(frm) {
        if (!frm.doc.__islocal && frm.doc.workflow_state === "Loading In-progress") {

            
frm.add_custom_button(__('Split Invoice'), () => {
                frappe.prompt([
                    {
                        fieldtype: 'Int',
                        fieldname: 'count',
                        label: 'Number of Splits',
                        default: 2,
                        reqd: 1
                    }
                ], (data) => {
                    if (data.count <= 0) {
                        frappe.msgprint(__('Please enter a split count greater than 0.'));
                        return;
                    }

                    // --------------------------
                    // CREATE DIALOG FOR SPLIT
                    // --------------------------
                    let d = new frappe.ui.Dialog({
                        title: "Split Invoice Batch Allocation",
                        size: "extra-large",
                        fields: [
                            { fieldtype: "HTML", fieldname: "batch_info" },
                            { fieldtype: "HTML", fieldname: "invoice_tables" }
                        ],
                        primary_action_label: "Create Split Invoices",
                        primary_action() {
                            let split_data = [];

                            $(".batch-row").each(function () {
                                 {
                                    split_data.push({
                                        invoice: parseInt($(this).attr("data-invoice")),
                                        batch: $(this).find(".batch").val(),
                                        qty: parseFloat($(this).find(".qty").val() || 0),
                                        item_code: frm.doc.items[0].item_code
                                    });
                                }
                            });

                            frappe.call({
                            method: "cit_exim.cit_exim.doctype.consolidated_sales_invoice.consolidated_sales_invoice.split_consolidated_invoice",
                            args: {
                                source_name: frm.doc.name,
                                split_count: data.count,
                                split_data: split_data
                            },
                            freeze: true,
                            freeze_message: __("Creating Split Invoices..."),
                            callback(r) {

                                if (!r.exc && r.message) {

                                    frappe.show_alert({
                                        message: __("{0} Sales Invoices created.", [r.message.length]),
                                        indicator: 'green'
                                    });

                                    d.hide();   

                                    frappe.set_route("List", "Sales Invoice", {
                                        "custom_consolidated_invoice_reference": frm.doc.name
                                    });
                                }

                            }
                        });
                        }
                    });

                    // --------------------------
                    // GET BATCHES FROM BUNDLE
                    // --------------------------
                    let bundle = frm.doc.items[0].serial_and_batch_bundle;

                    if (!bundle){
                        frappe.msgprint("No Serial and Batch Bundle found");
                        return;
                    }

                    frappe.call({
                        method: "cit_exim.cit_exim.doctype.consolidated_sales_invoice.consolidated_sales_invoice.get_serial_batch_bundle",
                        args: {
                            bundle_name: bundle
                        },
                        callback: function(r){
                            if(!r.message) return;

                            // Already formatted from backend
                            d.batches = r.message;

                            render_tables(d.batches);
                        }
                    });

                    // --------------------------
                    // RENDER TABLES
                    // --------------------------
                    function render_tables(batches){
                        let batch_html = `
                            <h4>Batches Used in Consolidated Invoice</h4>
                            <table class="table table-bordered">
                                <tr><th>Batch</th><th>Qty</th></tr>`;
                        batches.forEach(b => {
                            batch_html += `<tr><td>${b.batch_no}</td><td>${b.qty}</td></tr>`;
                        });
                        batch_html += "</table>";
                        d.fields_dict.batch_info.$wrapper.html(batch_html);

                        let invoice_html = "";
                        for (let i = 1; i <= data.count; i++) {
                            invoice_html += `
                                <h4>Invoice ${i}</h4>
                                <table class="table table-bordered invoice-table" data-invoice="${i}">
                                    <thead>
                                        <tr>
                                            <th style="width:60px"></th>
                                            <th>Batch No</th>
                                            <th>Quantity</th>
                                        </tr>
                                    </thead>
                                    <tbody>`;
                            batches.forEach(b => {
                                let split_qty = (b.qty / data.count).toFixed(2);
                                invoice_html += `
                                    <tr class="batch-row" data-invoice="${i}">
                                        <td><input type="checkbox" class="select-row"></td>
                                        <td><input class="form-control batch" value="${b.batch_no}"></td>
                                        <td><input class="form-control qty" type="number" value="${split_qty}"></td>
                                    </tr>`;
                            });
                            invoice_html += `
                                    </tbody>
                                </table>
                                <div style="margin-bottom:10px;">
                                    <button class="btn btn-sm btn-primary add-row" data-invoice="${i}">Add Row</button>
                                    <button class="btn btn-sm btn-danger delete-row" data-invoice="${i}" style="display:none;">Delete Row</button>
                                </div>`;
                        }
                        d.fields_dict.invoice_tables.$wrapper.html(invoice_html);
                        d.show();
                    }

                    // --------------------------
                    // ADD ROW
                    // --------------------------
                    d.$wrapper.off("click", ".add-row").on("click", ".add-row", function() {
                    let invoice = $(this).data("invoice");

                    // Build batch options
                    let batch_options = d.batches.map(b => `<option value="${b.batch_no}" data-qty="${b.qty}">${b.batch_no}</option>`).join("");

                    let row = `<tr class="batch-row" data-invoice="${invoice}">
                        <td><input type="checkbox" class="select-row"></td>
                        <td>
                            <select class="form-control batch">
                                <option value=""></option>
                                ${batch_options}
                            </select>
                        </td>
                        <td><input class="form-control qty" type="number" value="0"></td>
                    </tr>`;

                    $(`table[data-invoice="${invoice}"] tbody`).append(row);
                });

                // --------------------------
                // FILL QTY ON BATCH SELECT
                // --------------------------
                $(document).on("change", ".batch-row .batch", function() {
                    let selected_batch = $(this).find("option:selected");
                    let qty = parseFloat(selected_batch.data("qty") || 0);

                    // Optionally divide by total split count if needed
                    let invoice_table = $(this).closest("table");
                    let split_count = invoice_table.data("invoice"); // not needed if using total qty
                    $(this).closest("tr").find(".qty").val(qty);
                });

                    // --------------------------
                    // DELETE ROW
                    // --------------------------
                    $(document).on("click", ".delete-row", function(){
                        let invoice = $(this).data("invoice");
                        $(`table[data-invoice="${invoice}"] tbody tr`).each(function(){
                            if($(this).find(".select-row").is(":checked")){
                                $(this).remove();
                            }
                        });

                        let any_selected = $(`table[data-invoice="${invoice}"] tbody .select-row:checked`).length > 0;
                        if(!any_selected){
                            $(this).hide();
                        }
                    });

                    // --------------------------
                    // TOGGLE DELETE BUTTON ON CHECKBOX
                    // --------------------------
                    $(document).on("change", ".select-row", function(){
                        let invoice = $(this).closest("table").data("invoice");
                        let any_selected = $(`table[data-invoice="${invoice}"] tbody .select-row:checked`).length > 0;
                        $(`.delete-row[data-invoice="${invoice}"]`).toggle(any_selected);
                    });

                }, __('Split Parameters'), __('Split Now'));
            });
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
});


//----------------producer table--------------------------

frappe.ui.form.on('Consolidated Sales Invoice', {
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

// frappe.ui.form.on("Consolidated Sales Invoice", {
//     refresh(frm) {
//         update_number_of_containers(frm);
//     }
// });

// frappe.ui.form.on("container_detail", {
//     lot_no(frm) {
//         update_number_of_containers(frm);
//     },

//     container_detail_add(frm) {
//         update_number_of_containers(frm);
//     },

//     container_detail_remove(frm) {
//         update_number_of_containers(frm);
//     }
// });

// function update_number_of_containers(frm) {
//     let count = 0;

//     if (frm.doc.container_detail) {
//         frm.doc.container_detail.forEach(row => {
//             if (row.lot_no) {
//                 count += 1;
//             }
//         });
//     }

//     frm.set_value("number_of_containers", count);
// }
frappe.ui.form.on("Batches For Loading", {
    pick_container: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.batch_no) {
            frappe.msgprint(__("Please select a Batch No first"));
            return;
        }

        // Get unique containers
        let containers = [];
        if (frm.doc.container_detail) {
            frm.doc.container_detail.forEach(c => {
                if (c.container_no && !containers.includes(c.container_no)) {
                    containers.push(c.container_no);
                }
            });
        }

        if (containers.length === 0) {
            frappe.msgprint(__("No containers found in Container Detail table"));
            return;
        }

        let d = new frappe.ui.Dialog({
            title: __("Assign Batch {0} to Containers", [row.batch_no]),
            size: "large",
            fields: [
                {
                    label: __("Split Information"),
                    fieldname: "split_table",
                    fieldtype: "Table",
                    cannot_add_rows: true,
                    in_place_edit: true,
                    fields: [
                        {
                            fieldname: "container_no",
                            fieldtype: "Data",
                            label: __("Container No"),
                            in_list_view: 1,
                            read_only: 1
                        },
                        {
                            fieldname: "packages",
                            fieldtype: "Int",
                            label: __("No of Packages"),
                            in_list_view: 1,
                            reqd: 1
                        }
                    ],
                    data: containers.map(c => ({
                        container_no: c,
                        packages: 0
                    }))
                }
            ],

            primary_action_label: __("Update"),

            primary_action(values) {
                if (!values.split_table || values.split_table.length === 0) {
                    frappe.msgprint(__("Please add at least one row"));
                    return;
                }

                // Validate total
                let total_packages = values.split_table.reduce((sum, r) => {
                    return sum + (r.packages || 0);
                }, 0);

                if (total_packages > row.no_of_packages) {
                    frappe.msgprint(__(
                        "Total packages ({0}) exceeds batch packages ({1})",
                        [total_packages, row.no_of_packages]
                    ));
                    return;
                }

                values.split_table.forEach(split => {
                    if (!split.container_no || !split.packages) return;

                    let found = false;

                    if (frm.doc.container_detail) {
                        frm.doc.container_detail.forEach(cd => {
                            if (cd.container_no === split.container_no) {

                                //  EXISTING CONTAINER FOUND → MERGE
                                let existing_batches = cd.lot_no ? cd.lot_no.split(",") : [];

                                // Trim spaces
                                existing_batches = existing_batches.map(b => b.trim());

                                // Add batch if not already present
                                if (!existing_batches.includes(row.batch_no)) {
                                    existing_batches.push(row.batch_no);
                                }

                                cd.lot_no = existing_batches.join(", ");

                                //  SUM packages instead of overwrite
                                cd.no_of_packages = (cd.no_of_packages || 0) + split.packages;

                                found = true;
                            }
                        });
                    }




                    //  If container not found → create new
                    if (!found) {
                        let child = frm.add_child("container_detail");
                        child.container_no = split.container_no;
                        child.lot_no = row.batch_no;
                        child.no_of_packages = split.packages;
                    }
                });

                frm.refresh_field("container_detail");

                d.hide();

                frappe.show_alert({
                    message: __("Containers updated for batch {0}", [row.batch_no]),
                    indicator: "green"
                });
            }
        });

        d.show();
    }
});
// frappe.ui.form.on('Consolidated Sales Invoice', {
//     refresh: function(frm) {

//         frm.fields_dict['items'].grid.get_field("export_uom").get_query = function(doc, cdt, cdn) {

//             let row = locals[cdt][cdn];

//             return {
               
//                 filters: {
//                     item_group: row.item_group
//                 }
//             };
//         };
//     }
// });


// frappe.ui.form.on('Consolidated Sales Invoice Item', {
//     item_code: function(frm, cdt, cdn) {

//         let row = locals[cdt][cdn];

//         if (row.item_code) {
//             console.log("222222222",row.item_group)
//             frappe.db.get_value('Item', row.item_code, 'item_group')
//                 .then(r => {
//                     if (r.message) {

//                         //Set item_group in row (must exist as field)
//                         row.item_group = r.message.item_group;
//                         console.log("11111111",row.item_group)

//                         // Apply row-wise filter dynamically
//                         frm.fields_dict['items'].grid.get_field("export_uom").get_query = function(doc, cdt, cdn) {

//                             let child = locals[cdt][cdn];

//                             return {
//                                 filters: {
//                                     item_group: child.item_group
//                                 }
//                             };
//                         };

//                         frm.refresh_field('items');
//                     }
//                 });
//         }
//     }
// });

frappe.ui.form.on('Consolidated Sales Invoice', {
    refresh: function(frm) {

        frm.fields_dict['items'].grid.get_field("export_uom").get_query = function(doc, cdt, cdn) {

            let row = locals[cdt][cdn];

            if (!row.item_code) {
                return {};
            }

            return {
                query: "cit_exim.cit_exim.doctype.consolidated_sales_invoice.consolidated_sales_invoice.get_package_type_by_item",
                filters: {
                    item_code: row.item_code
                }
            };
        };
    }
});

// frappe.ui.form.on("Consolidated Sales Invoice", {
//     refresh(frm) {
//         update_number_of_containers(frm);
//     }
// });

// frappe.ui.form.on("Container Details", {
//     lot_no(frm) {
//         update_number_of_containers(frm);
//     },

//     container_detail_add(frm) {
//         update_number_of_containers(frm);
//     },

//     container_detail_remove(frm) {
//         update_number_of_containers(frm);
//     }
// });

// function update_number_of_containers(frm) {
//     let count = 0;

//     if (frm.doc.container_detail) {
//         frm.doc.container_detail.forEach(row => {
//             if (row.lot_no) {
//                 count += 1;
//             }
//         });
//     }

//     frm.set_value("number_of_containers", count);
// }

frappe.ui.form.on('Consolidated Sales Invoice', {

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

frappe.ui.form.on('Consolidated Sales Invoice Export Document Item', {

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
frappe.ui.form.on('Consolidated Sales Invoice', {
    onload: function(frm) {

        frm.set_query("contract_and_lc", function() {

            let sales_orders = [];

            (frm.doc.items || []).forEach(row => {
                if (row.sales_order && !sales_orders.includes(row.sales_order)) {
                    sales_orders.push(row.sales_order);
                }
            });

            return {
                query: "cit_exim.cit_exim.doctype.consolidated_sales_invoice.consolidated_sales_invoice.contract_and_lc_filter",
                filters: {
                    sales_orders: sales_orders
                }
            };
        });
    }
});


