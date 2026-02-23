app_name = "cit_exim"
app_title = "CIT Exim"
app_publisher = "craft"
app_description = "CIT EXIM"
app_email = "craft@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "cit_exim",
# 		"logo": "/assets/cit_exim/logo.png",
# 		"title": "CIT Exim",
# 		"route": "/cit_exim",
# 		"has_permission": "cit_exim.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cit_exim/css/cit_exim.css"
# app_include_js = "/assets/cit_exim/js/cit_exim.js"

# include js, css files in header of web template
# web_include_css = "/assets/cit_exim/css/cit_exim.css"
# web_include_js = "/assets/cit_exim/js/cit_exim.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cit_exim/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "cit_exim/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "cit_exim.utils.jinja_methods",
# 	"filters": "cit_exim.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cit_exim.install.before_install"
# after_install = "cit_exim.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cit_exim.uninstall.before_uninstall"
# after_uninstall = "cit_exim.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "cit_exim.utils.before_app_install"
# after_app_install = "cit_exim.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "cit_exim.utils.before_app_uninstall"
# after_app_uninstall = "cit_exim.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cit_exim.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"cit_exim.tasks.all"
# 	],
# 	"daily": [
# 		"cit_exim.tasks.daily"
# 	],
# 	"hourly": [
# 		"cit_exim.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cit_exim.tasks.weekly"
# 	],
# 	"monthly": [
# 		"cit_exim.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "cit_exim.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cit_exim.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cit_exim.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["cit_exim.utils.before_request"]
# after_request = ["cit_exim.utils.after_request"]

# Job Events
# ----------
# before_job = ["cit_exim.utils.before_job"]
# after_job = ["cit_exim.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# payment term override
from cit_exim.cit_exim.monkey_patch.accounts_controller import get_due_date
from erpnext.controllers import accounts_controller

accounts_controller.get_due_date = get_due_date

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cit_exim.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures=[
    # {"dt": "Custom Field", "filters": [["module", "in", ["CIT Exim"]]]},
    {
    "dt": "Custom Field",
    "filters": [
        ["dt", "in", ["Sales Order","Address","Supplier","Sales Invoice","Sales Invoice Item","Sales Order Item","Payment Entry","Journal Entry","Company","Item","Purchase Order",
                      "Purchase Invoice","Purchase Receipt","Opportunity"]]
    ]
    },
    {
    "dt": "Property Setter",
    "filters": [
        ["name", "in", [
           "Sales Order-main-field_order","Sales Order-shipping_terms-label","Sales Order-po_no-label","Supplier-main-field_order","Sales Order-customer-label","Address-is_shipping_address-depends_on",
           "Address-main-field_order","Journal Entry-voucher_type-options","Contract Term-custom_document_no","Item-main-field_order","Sales Invoice-main-field_order","Address-main-field_order","Item-main-field_order",
           "Sales Invoice-main-field_order","Purchase Order-main-field_order","Sales Order-main-field_order","Purchase Invoice-main-field_order","Sales Order-main-field_order","Purchase Order-main-field_order","Item-main-field_order",
           "Sales Order-main-field_order","Purchase Voucher-main-field_order","Packing Template-naming_series-options","Sales Order Item-main-field_order","Sales Order-main-field_order","Sales Invoice-main-field_order","Sales Order-main-field_order",
           "Sales Order-main-default_print_format","Bank Account-main-field_order","Sales Invoice-main-field_order","Sales Invoice-naming_series-default","Sales Invoice-naming_series-options","Sales Order-naming_series-default","Sales Order-naming_series-options",
           "Opportunity-main-field_order","Sales Invoice-exim_packing_details-hidden","Sales Invoice-main-field_order","Sales Invoice-main-field_order","Sales Invoice-main-field_order","Payment Entry-reference_date-label",
           "Payment Entry-reference_no-label","Payment Entry-main-field_order","Sales Invoice-main-field_order","Sales Invoice Item-description-allow_on_submit","Sales Order-main-links_order",
           "Sales Invoice Item-advanced_authorization_details-hidden","Sales Invoice Item-duty_calculation-depends_on","Sales Invoice-main-field_order","Sales Invoice-subscription_section-depends_on","Sales Invoice-section_break2-depends_on",
           "Sales Invoice-sales_team_section_break-depends_on","Sales Invoice-section_break_49-depends_on","Sales Order-main-links_order","Sales Order-main-links_order","Sales Invoice-is_pos-hidden","Sales Invoice-mode_of_transport-Options",
           "Sales Order-requirement_of_sample_approval-hidden","Sales Order-main-links_order","Sales Invoice-amount_hedged-hidden","Sales Invoice-natural_hedge-hidden","Sales Invoice-amount_unhedged-hidden","Sales Invoice-container_size-options",
           "Sales Invoice-mode_of_transport-options","Split Sales Invoice-container_size-options","Sales Invoice Item-main-field_order","Sales Invoice Item-capped_rate-label","Sales Invoice Item-capped_amount-depends_on",
           "Sales Invoice Item-effective_rate-depends_on","Sales Invoice Item-capped_rate-depends_on","Sales Invoice Item-maximum_cap-hidden","Sales Invoice-main-field_order","Container Details-batch_no-hidden"
        
           
        ]]
    ]
    },
    {"dt":"Translation",
    "filters":[
        ["name","in",(
            "tiqpvmc2p2",
        )]
    ]
    },



]

 
doctype_js = {
    "Sales Order": "public/js/doctype_js/sales_order.js",
    "Address":"public/js/doctype_js/address.js",
    "Delivery Note":"public/js/doctype_js/delivery_note.js",
    "Sales Invoice":"public/js/doctype_js/sales_invoice.js",
    "Lead":"public/js/doctype_js/lead.js",
    "Customize Form":"public/js/doctype_js/customize_form.js",
    "Payment Entry":"public/js/doctype_js/payment_entry.js",
    "Purchase Invoice":"public/js/doctype_js/purchase_invoice.js",
    "Purchase Order":"public/js/doctype_js/purchase_order.js",
    "Purchase Receipt":"public/js/doctype_js/purchase_receipt.js",
    "Purchase Voucher":"public/js/doctype_js/purchase_voucher.js",
    "Opportunity":"public/js/doctype_js/opportunity.js"
}

doctype_list_js = {
    "Sales Invoice": "public/js/doctype_js/sales_invoice_list.js"
}
# /home/user/v15/apps/cit_exim/cit_exim/public/js/doctype_js/sales_invoice_list.js

doc_events = {
    # "Sales Invoice": {
    #     "before_save": "cit_exim.cit_exim.doc_events.sales_invoice.before_save",
    #     "validate": "cit_exim.cit_exim.doc_events.sales_invoice.validate",
    #     "on_update_after_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_update_after_submit",
    #     "on_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_submit",
    #     "on_cancel": "cit_exim.cit_exim.doc_events.sales_invoice.on_cancel",
    #     # "before_save":"cit_exim.cit_exim.doc_events.sales_invoice.before_save",
    #     "before_insert":"cit_exim.cit_exim.doc_events.sales_invoice.before_insert",
    #     "before_submit":"cit_exim.cit_exim.doc_events.sales_invoice.before_submit",
        
    # },
        "Sales Invoice": {
        # "before_insert": "cit_exim.cit_exim.doc_events.sales_invoice.before_insert",
        # "before_save": "cit_exim.cit_exim.doc_events.sales_invoice.before_save",
        # "validate": "cit_exim.cit_exim.doc_events.sales_invoice.validate",
        # "before_submit": "cit_exim.cit_exim.doc_events.sales_invoice.before_submit",

        # "on_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_submit",
        # "on_update_after_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_update_after_submit",
        # "on_cancel": "cit_exim.cit_exim.doc_events.sales_invoice.on_cancel",

        "before_insert": "cit_exim.cit_exim.doc_events.sales_invoice.before_insert",
        "before_save": "cit_exim.cit_exim.doc_events.sales_invoice.before_save",
        "validate": "cit_exim.cit_exim.doc_events.sales_invoice.validate",
        "before_submit": "cit_exim.cit_exim.doc_events.sales_invoice.before_submit",
        "on_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_submit",
        "on_update_after_submit": "cit_exim.cit_exim.doc_events.sales_invoice.on_update_after_submit",
        "on_cancel": "cit_exim.cit_exim.doc_events.sales_invoice.on_cancel",
       

    },
    


        "Sales Order": {
        "validate": "cit_exim.cit_exim.doc_events.sales_order.validate"
        # "before_save": "cit_exim.cit_exim.doc_events.sales_order.before_save"
    },

    # /home/user/v15/apps/cit_exim/cit_exim/cit_exim/doc_events/sales_order.py
    # "Purchase Invoice": {
    #      "on_submit": "cit_exim.cit_exim.doc_events.purchase_invoice.pi_on_submit",
    #     "on_cancel": "cit_exim.cit_exim.doc_events.purchase_invoice.pi_on_cancel",
    # },
    (
        "Purchase Invoice",
        "Payment Request",
        "Payment Entry",
        "Journal Entry",
        "Material Request",
        "Purchase Order",
        "Work Order",
        "Production Plan",
        "Stock Entry",
        "Quotation",
        "Sales Order",
        "Delivery Note",
        "Purchase Receipt",
        "Packing Slip",
    ): {
        # "before_naming": "cit_exim.api.docs_before_naming",
    },
    "Rodtep Claim": {
        "on_submit": "cit_exim.cit_exim.doctype.rodtep_claim.rodtep_claim.create_jv_on_submit"
    },
    "Duty DrawBack Claim": {
        "on_submit": "cit_exim.cit_exim.doctype.duty_drawback_claim.duty_drawback_claim.create_jv_on_submit"
    },

    ("Delivery Note", "Sales Invoice"): {
        "validate": "cit_exim.cit_exim.doc_events.igst_calculation.cal_igst",
          
    },
    # "Delivery Note":{
    #     "before_insert":"cit_exim.cit_exim.doc_events.delivery_note.before_insert"
    # },
   
    "Payment Entry": {
        "on_submit": [
            "cit_exim.cit_exim.doc_events.payment_entry.on_submit",
            "cit_exim.cit_exim.doc_events.payment_entry.on_submit_update_sales_invoice"
        ],
        "on_cancel": [
            "cit_exim.cit_exim.doc_events.payment_entry.on_cancel"
        ]
    },



     "Vehicle Queue": {
        "on_submit": "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.create_purchase_voucher"
    }

    #    "Vehicle Queue": {
    #     "on_submit": "cit_exim.cit_exim.doctype.vehicle_queue.vehicle_queue.create_purchase_documents"
    # }
   
}