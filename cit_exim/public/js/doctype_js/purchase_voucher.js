// ================================
//  LOADING THE TEMPLATES 
// ================================
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

// ================================
// LOAD FROM ITEM (Child Table)
// ================================
frappe.ui.form.on("Fish items", {
    fish_variety(frm, cdt, cdn) {

        const row = locals[cdt][cdn];
        if (!row.fish_variety) return;

        frappe.db.get_value(
            "Item",
            row.fish_variety,
            "custom_template"
        ).then(r => {

            const template = r.message?.custom_template;

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

// ================================
// LOAD FROM MANUAL TEMPLATE CHANGE
// ================================
frappe.ui.form.on("Purchase Voucher", {
    custom_product(frm) {
        load_variable_template(frm, frm.doc.custom_product);
    }
});