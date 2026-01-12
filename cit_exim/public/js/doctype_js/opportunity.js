// ==================================================
//  VARIABLE TEMPLATE LOADER
// ==================================================
function load_variable_template(frm, template_name) {

    if (!template_name) {
        frm.clear_table("custom_quality_and_specification");
        frm.refresh_field("custom_quality_and_specification");
        frm._template_loaded_for = null;
        return;
    }

    // Prevent duplicate reload
    if (frm._template_loaded_for === template_name) return;
    frm._template_loaded_for = template_name;

    frm.clear_table("custom_quality_and_specification");

    frappe.db.get_doc("Variable Template", template_name)
        .then(doc => {
            (doc.lab_variable || []).forEach(row => {
                let child = frm.add_child("custom_quality_and_specification");
                child.test = row.test;
                child.value = row.value;
            });

            frm.refresh_field("custom_quality_and_specification");
        });
}


// ==================================================
//  LOAD TEMPLATE FROM OPPORTUNITY ITEM
// ==================================================
frappe.ui.form.on("Opportunity Item", {
    item_code(frm, cdt, cdn) {

        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.db.get_value(
            "Item",
            row.item_code,
            "custom_template"
        ).then(r => {

            let template = r.message && r.message.custom_template;

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


// ==================================================
//  LOAD TEMPLATE ON MANUAL CHANGE
// ==================================================
frappe.ui.form.on("Opportunity", {
    custom_product(frm) {
        load_variable_template(frm, frm.doc.custom_product);
    }
});


// ==================================================
//  LOAD TEMPLATE ON REFRESH (EXISTING OPPORTUNITY)
// ==================================================
frappe.ui.form.on("Opportunity", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.custom_product) {
            load_variable_template(frm, frm.doc.custom_product);
        }
    }
});
