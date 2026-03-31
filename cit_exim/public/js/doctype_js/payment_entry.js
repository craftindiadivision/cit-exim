
cur_frm.add_fetch('forward_contract', 'booking_rate', 'forward_rate');
cur_frm.add_fetch('forward_contract', 'amount', 'amount');
cur_frm.add_fetch('forward_contract', 'maturity_from', 'maturity_from');
cur_frm.add_fetch('forward_contract', 'maturity_to', 'maturity_to');
cur_frm.add_fetch('forward_contract', 'amount_outstanding', 'amount_outstanding');
cur_frm.add_fetch('forward_contract', 'amount_outstanding', 'amount_utilized');

cur_frm.cscript.onload = function(frm) {
	// if (cur_frm.doc.paid_to_account_currency == 'INR'){
		cur_frm.set_query("forward_contract","forwards", function() {
			return {
				"filters": {
					"hedge": "Export",
					"status": "Open",
					"docstatus": 1,
					"amount_outstanding": ['>', '0'],
					"currency": cur_frm.doc.paid_from_account_currency
				}
			};
		});
	}
	// else {
	// 	cur_frm.set_query("forward_contract","forwards", function() {
	// 		return {
	// 			"filters": {
	// 				"hedge": "Import",
	// 				"status": "Open",
	// 				"docstatus": 1,
	// 				"amount_outstanding": ['>', '0'],
	// 				"currency": cur_frm.doc.paid_to_account_currency
	// 			}
	// 		};
	// 	});
	// }
// }

frappe.ui.form.on("Payment Entry", {
    paid_to: function(frm){
        cur_frm.refresh();
    // if (frm.doc.paid_to_account_currency == 'INR'){
	// 	frm.set_query("forward_contract","forwards", function() {
	// 		return {
	// 			"filters": {
	// 				"hedge": "Export",
	// 				"status": "Open",
	// 				"docstatus": 1,
	// 				"amount_outstanding": ['>', '0'],
	// 				"currency": cur_frm.doc.paid_from_account_currency
	// 			}
	// 		};
	// 	});
	// }
	// else {
	// 	frm.set_query("forward_contract","forwards", function() {
	// 		return {
	// 			"filters": {
	// 				"hedge": "Import",
	// 				"status": "Open",
	// 				"docstatus": 1,
	// 				"amount_outstanding": ['>', '0'],
	// 				"currency": cur_frm.doc.paid_to_account_currency
	// 			}
	// 		};
	// 	});
	// }
        
    },
	onload: function(frm){
		if(frm.doc.__islocal && frm.doc.payment_type== "Pay"){
			frm.set_value('print_heading', "Payment Advice");
		}
		var df = frappe.meta.get_docfield("Forward Utilization","forward_amount", cur_frm.doc.name);
		df.options="paid_from_account_currency";
		
		df = frappe.meta.get_docfield("Forward Utilization","amount_outstanding", cur_frm.doc.name);
		df.options="paid_from_account_currency";

		df = frappe.meta.get_docfield("Forward Utilization","amount_utilized", cur_frm.doc.name);
		df.options="paid_from_account_currency";
	},
	
	validate: function(frm){
		if(cstr(frm.doc.forwards)){
			if(frm.doc.total_amount_utilized != frm.doc.paid_amount) {
				frappe.throw(__("Total Amount Utilized must be same as Paid Amount."))
			}
		}

		frm.trigger("cal_average_forward_rate");
	},

	payment_type: function(frm){
		if(frm.payment_type == "Pay"){
			frm.set_value('print_heading', "Payment Advice");
		}
		if(frm.payment_type == "Receive"){
			frm.set_value('print_heading', "Payment Receipt");
		}
	},
// 	party: function(frm) {
// 		frappe.call({
// 			method:"elkins.api.get_party_details",
// 			args:{
// 				party: frm.doc.party,
// 				party_type: frm.doc.party_type
// 			},
// 			callback: function(r){
// 				if(r.message){
// 					frm.set_value('contact_person', r.message.contact_person)
// 					frm.set_value('email_id', r.message.contact_email)
// 					frm.set_value ('party_name', frm.doc.party)
// 				}
// 			}
// 		});
// 	},
	contact_person: function(frm) {
		erpnext.utils.get_contact_details(frm);
	},
	average_forward_rate: function(frm) {
		if(frm.doc.average_forward_rate){
			frm.set_value('source_exchange_rate', frm.doc.average_forward_rate);
		}
		else {
			var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;
			frm.events.set_current_exchange_rate(frm, "source_exchange_rate", frm.doc.paid_from_account_currency, company_currency);
		}
	},
	cal_average_forward_rate: function(frm){
		let total_forward_amount = 0;
		let total_forward_inr_amount = 0;
		frm.doc.forwards.forEach((row) => {
			total_forward_amount += flt(row.amount_utilized);
			total_forward_inr_amount += (flt(row.forward_rate)*flt(row.amount_utilized));
		});
		frm.set_value("average_forward_rate", flt(total_forward_inr_amount / (total_forward_amount|| 1)));
	},
	cal_total_amount_utilized: function(frm){
		let total_amount_utilized = 0;
		frm.doc.forwards.forEach((row) => {
			total_amount_utilized += flt(row.amount_utilized);
		});
		frm.set_value("total_amount_utilized", total_amount_utilized);
	},
});

frappe.ui.form.on("Forward Utilization", {
	forwards_remove:function(frm,cdt,cdn){
		frm.events.cal_average_forward_rate(frm);
		frm.events.cal_total_amount_utilized(frm);
	},
	forward_rate:function(frm,cdt,cdn){
		frm.events.cal_average_forward_rate(frm);
	},
	amount_utilized:function(frm,cdt,cdn){
		frm.events.cal_total_amount_utilized(frm);
	},
});

frappe.ui.form.on("Payment Entry", {
    onload: function(frm) {
        // Ignore cancellation for all linked documents of respective DocTypes.
        frm.ignore_doctypes_on_cancel_all = ["Forward Booking"];
    }
})

frappe.ui.form.on('Payment Entry', {
    refresh: function(frm) {
        // Always keep this field read-only as it is system-generated on submit
        frm.set_df_property('custom_payment_received_date', 'read_only', 1);
    }
});



frappe.ui.form.on('Payment Entry', {
    received_amount: function(frm) {
        calculate_usd_amount(frm);
    },
    source_exchange_rate: function(frm) {
        calculate_usd_amount(frm);
    }
});

function calculate_usd_amount(frm) {
    if (frm.doc.received_amount && frm.doc.source_exchange_rate) {
        let usd_val = frm.doc.received_amount / frm.doc.source_exchange_rate;
        frm.set_value('custom_received_amountusd', usd_val);
    }
}














// -------------------------------------------------------------------------------------------------------------------------







// cur_frm.add_fetch('forward_contract', 'booking_rate', 'forward_rate');
// cur_frm.add_fetch('forward_contract', 'amount', 'amount');
// cur_frm.add_fetch('forward_contract', 'maturity_from', 'maturity_from');
// cur_frm.add_fetch('forward_contract', 'maturity_to', 'maturity_to');
// cur_frm.add_fetch('forward_contract', 'amount_outstanding', 'amount_outstanding');
// cur_frm.add_fetch('forward_contract', 'amount_outstanding', 'amount_utilized');

// cur_frm.cscript.onload = function(frm) {
//     cur_frm.set_query("forward_contract","forwards", function() {
//         return {
//             "filters": {
//                 "hedge": "Export",
//                 "status": "Open",
//                 "docstatus": 1,
//                 "amount_outstanding": ['>', '0'],
//                 "currency": cur_frm.doc.paid_from_account_currency
//             }
//         };
//     });
// }

// frappe.ui.form.on("Payment Entry", {
//     // TRIGGER: When page is loaded or refreshed
//     refresh: function(frm) {
//         frm.set_df_property('custom_payment_received_date', 'read_only', 1);
//         frm.trigger("calculate_usd_amount");
//     },

//     // TRIGGER: When Received Amount changes
//     received_amount: function(frm) {
//         frm.trigger("calculate_usd_amount");
//     },

//     // TRIGGER: When Exchange Rate changes
//     source_exchange_rate: function(frm) {
//         frm.trigger("calculate_usd_amount");
//     },

//     // THE CALCULATION FUNCTION
//     calculate_usd_amount: function(frm) {
//         if (frm.doc.received_amount && frm.doc.source_exchange_rate && frm.doc.source_exchange_rate != 0) {
//             let usd_val = flt(frm.doc.received_amount) / flt(frm.doc.source_exchange_rate);
//             frm.set_value('custom_received_amountusd', usd_val);
//         } else {
//             frm.set_value('custom_received_amountusd', 0);
//         }
//     },

//     paid_to: function(frm){
//         cur_frm.refresh();
//     },

//     onload: function(frm){
//         if(frm.doc.__islocal && frm.doc.payment_type== "Pay"){
//             frm.set_value('print_heading', "Payment Advice");
//         }
        
//         // Dynamic field options for child table
//         var df = frappe.meta.get_docfield("Forward Utilization","forward_amount", cur_frm.doc.name);
//         if(df) df.options="paid_from_account_currency";
        
//         df = frappe.meta.get_docfield("Forward Utilization","amount_outstanding", cur_frm.doc.name);
//         if(df) df.options="paid_from_account_currency";

//         df = frappe.meta.get_docfield("Forward Utilization","amount_utilized", cur_frm.doc.name);
//         if(df) df.options="paid_from_account_currency";

//         frm.ignore_doctypes_on_cancel_all = ["Forward Booking"];
//     },
    
//     validate: function(frm){
//         if(frm.doc.forwards && frm.doc.forwards.length > 0){
//             if(flt(frm.doc.total_amount_utilized) != flt(frm.doc.paid_amount)) {
//                 frappe.throw(__("Total Amount Utilized must be same as Paid Amount."))
//             }
//         }

//         frm.trigger("cal_average_forward_rate");
//         frm.trigger("calculate_usd_amount"); // Recalculate before save
//     },

//     payment_type: function(frm){
//         if(frm.doc.payment_type == "Pay"){
//             frm.set_value('print_heading', "Payment Advice");
//         }
//         if(frm.doc.payment_type == "Receive"){
//             frm.set_value('print_heading', "Payment Receipt");
//         }
//     },

//     contact_person: function(frm) {
//         erpnext.utils.get_contact_details(frm);
//     },

//     average_forward_rate: function(frm) {
//         if(frm.doc.average_forward_rate){
//             frm.set_value('source_exchange_rate', frm.doc.average_forward_rate);
//         }
//         else {
//             var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;
//             frm.events.set_current_exchange_rate(frm, "source_exchange_rate", frm.doc.paid_from_account_currency, company_currency);
//         }
//     },

//     cal_average_forward_rate: function(frm){
//         let total_forward_amount = 0;
//         let total_forward_inr_amount = 0;
//         (frm.doc.forwards || []).forEach((row) => {
//             total_forward_amount += flt(row.amount_utilized);
//             total_forward_inr_amount += (flt(row.forward_rate) * flt(row.amount_utilized));
//         });
//         frm.set_value("average_forward_rate", flt(total_forward_inr_amount / (total_forward_amount || 1)));
//     },

//     cal_total_amount_utilized: function(frm){
//         let total_amount_utilized = 0;
//         (frm.doc.forwards || []).forEach((row) => {
//             total_amount_utilized += flt(row.amount_utilized);
//         });
//         frm.set_value("total_amount_utilized", total_amount_utilized);
//     },
// });

// // Child Table Triggers
// frappe.ui.form.on("Forward Utilization", {
//     forwards_remove: function(frm, cdt, cdn){
//         frm.trigger("cal_average_forward_rate");
//         frm.trigger("cal_total_amount_utilized");
//     },
//     forward_rate: function(frm, cdt, cdn){
//         frm.trigger("cal_average_forward_rate");
//     },
//     amount_utilized: function(frm, cdt, cdn){
//         frm.trigger("cal_total_amount_utilized");
//     },
// });
frappe.ui.form.on("Payment Entry", {

    custom_consolidated_sales_invoice: function(frm) {
        load_invoices(frm);
    },

    paid_amount: function(frm) {
        apply_fifo(frm);
    }

});

function load_invoices(frm) {

    if (!frm.doc.custom_get_from_consolidated_sales_invoice) return;

    let consolidated = frm.doc.custom_consolidated_sales_invoice;
    if (!consolidated) return;

    frm.clear_table("references");

    frappe.call({
        method: "cit_exim.cit_exim.doc_events.payment_entry.get_sales_invoices",
        args: {
            consolidated_invoice: consolidated
        },
        callback: function(r) {

            if (r.message) {

                r.message.forEach(inv => {

                    let row = frm.add_child("references");

                    row.reference_doctype = "Sales Invoice";
                    row.reference_name = inv.name;
                    row.total_amount = inv.grand_total || 0;
                    row.outstanding_amount = inv.outstanding_amount || 0;
                    row.allocated_amount = 0; //  initially 0

                });

                frm.refresh_field("references");

                //  Apply FIFO after loading
                apply_fifo(frm);
            }
        }
    });
}

function apply_fifo(frm) {

    let remaining = frm.doc.paid_amount || 0;

    (frm.doc.references || []).forEach(row => {

        let outstanding = row.outstanding_amount || 0;

        if (remaining <= 0) {
            row.allocated_amount = 0;
        } else if (remaining >= outstanding) {
            row.allocated_amount = outstanding;
            remaining -= outstanding;
        } else {
            row.allocated_amount = remaining;
            remaining = 0;
        }
    });

    frm.refresh_field("references");
}