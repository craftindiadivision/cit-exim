// Copyright (c) 2025, craft and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Rodtep Claim", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Rodtep Claim', {
  
  get_rodtep_entries:function(frm){
    if (frm.doc.rodtep_details) {
            for (var j = frm.doc.rodtep_details.length - 1; j >= 0; j--) {
                cur_frm.get_field("rodtep_details").grid.grid_rows[j].remove();
            }
        }
    frappe.call({
    //   method : "exim.exim.doctype.rodtep_claim.rodtep_claim.journal_entry_list",
      method : "cit_exim.cit_exim.doctype.rodtep_claim.rodtep_claim.journal_entry_list",

      args:{
        "start_date":frm.doc.start_date,
        "end_date":frm.doc.end_date,
        "company":frm.doc.company
      },
      callback: function(r) {
        if(r.message){
        r.message.forEach(function(res) {
          
          var childTable = cur_frm.add_child("rodtep_details");
          childTable.je_no = res['je_no']
          childTable.shipping_bill_no = res['shipping_bill_no']
          childTable.account = res['account']
          childTable.debit_amount = res['debit_amount']
          childTable.cheque_date = res['cheque_date']
          childTable.cheque_no = res['cheque_no']
                   }
           )
        
       
      }
      else{
        cur_frm.doc.rodtep_details = []

      }
        // cur_frm.refresh();
        cur_frm.refresh_field("rodtep_details")
          
        
      }
    });
    
  },
  
});


frappe.ui.form.on('Rodtep Claim', {
  onload(frm) {
      set_credit_account_filter(frm);
  },

  company(frm) {
      frm.set_value('credit_account', null); // clear old value
      set_credit_account_filter(frm);
  }
});

function set_credit_account_filter(frm) {
  frm.set_query('credit_account', function () {
      if (!frm.doc.company) {
          return {};
      }

      return {
          filters: {
              company: frm.doc.company,
              is_group: 0
          }
      };
  });
}