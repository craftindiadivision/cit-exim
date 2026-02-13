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
    },
    item_add: function(frm) {
        calculate_totals(frm);
    },

    item_remove: function(frm) {
        calculate_totals(frm);
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
frappe.ui.form.on("Vehicle Queue", {
  refresh(frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(
        ("Purchase Order"),
        () => {
          if (!frm.doc.supplier) {
            frappe.throw(("Please select Supplier"));
          }

          erpnext.utils.map_current_doc({
            method: "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.make_vehicle_queue_from_po",
            source_doctype: "Purchase Order",
            target: frm,
            setters: {
              supplier: frm.doc.supplier,
            },
            get_query_filters: {
              docstatus: 1,
              status: ["not in", ["Closed", "On Hold"]],
              supplier: frm.doc.supplier,
              company: frm.doc.company,
              per_received: ["<", 100]
            },
            allow_child_item_selection: true,
            child_fieldname: "items",
            child_columns: ["item_code", "item_name"],
          });
        },
        __("Get Items From")
      );
    }
  },
});
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
frappe.ui.form.on("Vehicle Queue", {
    refresh(frm) {
        update_no_of_bags_label(frm);
    },
    product(frm) {
        update_no_of_bags_label(frm);
    }
});

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

    if (product === "RM-Fish Meal") {

        frm.fields_dict["item"].grid.toggle_display("avg_per_box", false);
        frm.fields_dict["item"].grid.toggle_display("net_wt", false);

    } else {

        frm.fields_dict["item"].grid.toggle_display("avg_per_box", true);
        frm.fields_dict["item"].grid.toggle_display("net_wt", true);
    }
}

