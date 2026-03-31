// frappe.ui.form.on('Address', {
//     custom_is_consignee(frm) {

//         // Mandatory toggle for consignee name
//         if (frm.doc.custom_is_consignee) {
//             frm.toggle_reqd('custom_consignee_name', true);

//             // Set shipping address fields
//             frm.set_value("is_shipping_address", 1);
//             frm.set_value("address_type", "Shipping");

//         } else {
//             frm.toggle_reqd('custom_consignee_name', false);
//             frm.set_value('custom_consignee_name', '');

//             // Reset shipping address fields
//             frm.set_value("is_shipping_address", 0);
//             frm.set_value("address_type", "");
//         }
//     },

//     refresh(frm) {
//         // Apply mandatory rule on refresh
//         frm.toggle_reqd('custom_consignee_name', frm.doc.custom_is_consignee);
//     }
// });

