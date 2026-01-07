// Copyright (c) 2025, craft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Queue", {
    gross_weight: function(frm) {
        calculate_net_weight(frm);
    },
    tare_weight: function(frm) {
        calculate_net_weight(frm);
    }
});

function calculate_net_weight(frm) {
    if(frm.doc.gross_weight != null && frm.doc.tare_weight != null){
        frm.set_value("net_weight", frm.doc.gross_weight - frm.doc.tare_weight);
    } else {
        frm.set_value("net_weight", 0);
    }
}



frappe.ui.form.on("Vehicle Queue", {
    product: function (frm) {

        // If no Item Group selected, remove filter
        if (!frm.doc.product) {
            frm.set_query("item", "item", function () {
                return {};
            });
            return;
        }

        // Set dropdown filter for Item field inside child table
        frm.set_query("item", "item", function () {
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
