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
