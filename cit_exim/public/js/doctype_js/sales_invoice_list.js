// frappe.listview_settings['Sales Invoice'] = {
//     add_fields: ["status", "gst_category"],

//     get_indicator(doc) {

//         // Condition: Only show status indicator when GST Category is NOT Overseas
//         if (doc.gst_category !== "Overseas") {

//             if (doc.status === "Draft") {
//                 return [__("Draft"), "orange", "status,=,Draft"];
//             }

//             if (doc.status === "Submitted") {
//                 return [__("Submitted"), "blue", "status,=,Submitted"];
//             }

//             if (doc.status === "Paid") {
//                 return [__("Paid"), "green", "status,=,Paid"];
//             }

//             if (doc.status === "Cancelled") {
//                 return [__("Cancelled"), "red", "status,=,Cancelled"];
//             }
//         }
//     }
// };


// frappe.listview_settings['Sales Invoice'] = {
//     add_fields: ["status", "gst_category"],

//     get_indicator(doc) {

//         if (doc.gst_category !== "Overseas" && doc.status) {
//             let color = "blue"; 

//             if (doc.status === "Completed") color = "green";
//             if (doc.status === "Cancelled") color = "red";
//             if (doc.status === "Pending") color = "orange";

//             return [__(doc.status), color, `status,=,${doc.status}`];
//         }
//     }
// };


// frappe.listview_settings['Sales Invoice'] = {
//     get_indicator: function (doc) {

        
//         if (doc.gst_category != "Overseas" && doc.workflow_state === "Submit") {
//             return [
//                 (doc.status),          
//                 "blue",         
//                 "status,=," + doc.status
//             ];
//         }

//         // Default → show workflow state
//         if (doc.workflow_state) {
//             return [
//                 (doc.workflow_state),
//                 "grey",
//                 "workflow_state,=," + doc.workflow_state
//             ];
//         }
//     }
// };


frappe.listview_settings['Sales Invoice'] = {
    add_fields: ['status', 'gst_category', 'workflow_state'],

    get_indicator(doc) {

        // Apply ONLY for non-overseas & submitted invoices
        if (doc.gst_category !== "Overseas" && doc.workflow_state === "Submitted") {

            if (doc.status === "Paid") {
                return [("Paid"), "green", "status,=,Paid"];
            }

            if (doc.status === "Partly Paid") {
                return [("Partly Paid"), "blue", "status,=,Partly Paid"];
            }

            if (doc.status === "Unpaid") {
                return [("Unpaid"), "orange", "status,=,Unpaid"];
            }

            if (doc.status === "Unpaid and Discounted") {
                return [("Unpaid and Discounted"), "orange", "status,=,Unpaid and Discounted"];
            }

            if (doc.status === "Partly Paid and Discounted") {
                return [("Partly Paid and Discounted"), "blue", "status,=,Partly Paid and Discounted"];
            }

            if (doc.status === "Overdue and Discounted") {
                return [("Overdue and Discounted"), "red", "status,=,Overdue and Discounted"];
            }

            if (doc.status === "Overdue") {
                return [("Overdue"), "red", "status,=,Overdue"];
            }

            if (doc.status === "Cancelled") {
                return [("Cancelled"), "darkgrey", "status,=,Cancelled"];
            }

            if (doc.status === "Internal Transfer") {
                return [__("Internal Transfer"), "purple", "status,=,Internal Transfer"];
            }
        }
    }
};