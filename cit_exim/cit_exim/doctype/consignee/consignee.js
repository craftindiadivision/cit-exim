// Copyright (c) 2025, craft and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Consignee", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Consignee', {
//     address: function(frm) {

//         if (!frm.doc.buyer) {
//             frappe.msgprint("Please select Buyer first");
//             return;
//         }

//         frappe.set_route('List', 'Address', {
//             link_doctype: 'Customer',
//             link_name: frm.doc.buyer
//         });

//     }
// });
frappe.ui.form.on('Consignee', {
    address: function(frm) {

        if (!frm.doc.buyer) {
            frappe.msgprint("Please select Buyer first");
            return;
        }

        frappe.new_doc('Address', {
            links: [
                {
                    link_doctype: 'Customer',
                    link_name: frm.doc.buyer
                }
            ],
            custom_consignee_name: frm.doc.consignee_name,
            custom_is_consignee: 1,
            is_shipping_address:1,
            address_type:'Shipping'
        });

    }
});