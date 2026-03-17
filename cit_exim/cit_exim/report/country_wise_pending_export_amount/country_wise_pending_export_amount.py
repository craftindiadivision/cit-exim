# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters: filters = {}
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     # Adding "options": "currency" tells Frappe to look at the 'currency' field in each row
#     return [
#         {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "options": "currency", "width": 150},
#     ]

# def get_data(filters):
#     conditions = ""
    
#     if filters.get("company"):
#         conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    
#     if filters.get("from_date"):
#         conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
        
#     if filters.get("to_date"):
#         conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"
#     else:
#         conditions += " AND si.posting_date <= CURDATE()"

#     query = f"""
#         /* 1. Country-wise Rows (USD) */
#         SELECT
#             si.country_of_destination AS country,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount ELSE 0 END) AS fo,
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount ELSE 0 END) AS fsp,
#             SUM(sii.net_amount) AS grand_total,
#             si.currency AS currency,
#             0 as row_order
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1 
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             AND si.country_of_destination IS NOT NULL
#             {conditions}
#         GROUP BY si.country_of_destination

#         UNION ALL

#         /* 2. Grand Total Row (USD) */
#         SELECT
#             'Grand Total' AS country,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount ELSE 0 END),
#             SUM(sii.net_amount),
#             MAX(si.currency),
#             1 as row_order
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1 
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             {conditions}

#         UNION ALL

#         /* 3. Total INR Row (Forced INR) */
#         SELECT
#             'TOTAL (INR)' AS country,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.net_amount * si.conversion_rate ELSE 0 END),
#             SUM(sii.net_amount * si.conversion_rate),
#             'INR',
#             2 as row_order
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1 
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             {conditions}
        
#         ORDER BY row_order ASC, country ASC
#     """
    
#     return frappe.db.sql(query, as_dict=True)










# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters: 
#         filters = {}

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def get_columns():
#     return [
#         {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Currency", "options": "currency", "width": 120},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "options": "currency", "width": 150},
#     ]


# def get_data(filters):

#     conditions = ""

#     if filters.get("company"):
#         conditions += f" AND so.company = {frappe.db.escape(filters.get('company'))}"

#     if filters.get("from_date"):
#         conditions += f" AND so.transaction_date >= {frappe.db.escape(filters.get('from_date'))}"

#     if filters.get("to_date"):
#         conditions += f" AND so.transaction_date <= {frappe.db.escape(filters.get('to_date'))}"
#     else:
#         conditions += " AND so.transaction_date <= CURDATE()"


#     query = f"""

#         /* Pending calculation subquery */
#         WITH pending_data AS (
#             SELECT
#                 so.country_of_destination AS country,
#                 soi.item_code,
#                 (soi.net_amount - IFNULL(inv.invoiced_amount,0)) AS pending_amount,
#                 so.currency,
#                 so.conversion_rate
#             FROM `tabSales Order` so

#             JOIN `tabSales Order Item` soi
#                 ON soi.parent = so.name

#             LEFT JOIN (
#                 SELECT
#                     sii.so_detail,
#                     SUM(sii.net_amount) AS invoiced_amount
#                 FROM `tabSales Invoice Item` sii
#                 JOIN `tabSales Invoice` si
#                     ON si.name = sii.parent
#                 WHERE si.docstatus = 1
#                 GROUP BY sii.so_detail
#             ) inv
#                 ON inv.so_detail = soi.name

#             WHERE
#                 so.docstatus = 1
#                 AND so.country_of_destination IS NOT NULL
#                 {conditions}
#         )


#         /* 1. Country Rows */
#         SELECT
#             country,
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 60' THEN pending_amount ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 62' THEN pending_amount ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 65' THEN pending_amount ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN item_code = 'Fish Oil' THEN pending_amount ELSE 0 END) AS fo,
#             SUM(CASE WHEN item_code = 'Soluble Paste' THEN pending_amount ELSE 0 END) AS fsp,
#             SUM(pending_amount) AS grand_total,
#             MAX(currency) AS currency,
#             0 AS row_order
#         FROM pending_data
#         GROUP BY country


#         UNION ALL


#         /* 2. Grand Total (USD) */
#         SELECT
#             'Grand Total',
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 60' THEN pending_amount ELSE 0 END),
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 62' THEN pending_amount ELSE 0 END),
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 65' THEN pending_amount ELSE 0 END),
#             SUM(CASE WHEN item_code = 'Fish Oil' THEN pending_amount ELSE 0 END),
#             SUM(CASE WHEN item_code = 'Soluble Paste' THEN pending_amount ELSE 0 END),
#             SUM(pending_amount),
#             MAX(currency),
#             1
#         FROM pending_data


#         UNION ALL


#         /* 3. Total INR */
#         SELECT
#             'TOTAL (INR)',
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 60' THEN pending_amount * conversion_rate ELSE 0 END),
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 62' THEN pending_amount * conversion_rate ELSE 0 END),
#             SUM(CASE WHEN item_code = 'FG-Fish Meal 65' THEN pending_amount * conversion_rate ELSE 0 END),
#             SUM(CASE WHEN item_code = 'Fish Oil' THEN pending_amount * conversion_rate ELSE 0 END),
#             SUM(CASE WHEN item_code = 'Soluble Paste' THEN pending_amount * conversion_rate ELSE 0 END),
#             SUM(pending_amount * conversion_rate),
#             'INR',
#             2
#         FROM pending_data

#         ORDER BY row_order ASC, country ASC
#     """

#     return frappe.db.sql(query, as_dict=True)















import frappe


def execute(filters=None):
    items = get_items()
    columns = get_columns(items)
    data = get_data(items)

    return columns, data


def get_items():
    return frappe.db.sql("""
        SELECT DISTINCT soi.item_code, i.item_name
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON so.name = soi.parent
        JOIN `tabItem` i ON i.name = soi.item_code
        WHERE so.docstatus = 1
        ORDER BY i.item_name
    """, as_dict=1)


def get_columns(items):

    columns = [
        {
            "label": "Country",
            "fieldname": "country",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    for item in items:
        columns.append({
            "label": item.item_name,
            "fieldname": frappe.scrub(item.item_code),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140
        })

    columns.append({
        "label": "Grand Total",
        "fieldname": "grand_total",
        "fieldtype": "Currency",
        "options": "currency",
        "width": 160
    })

    return columns


def get_data(items):

    rows = frappe.db.sql("""
        SELECT
            so.country_of_destination AS country,
            so.currency,
            so.conversion_rate,
            soi.item_code,
            SUM(soi.amount) AS so_amount,
            IFNULL(SUM(sii.amount),0) AS si_amount

        FROM `tabSales Order` so

        JOIN `tabSales Order Item` soi
            ON soi.parent = so.name

        LEFT JOIN `tabSales Invoice Item` sii
            ON sii.sales_order = so.name
            AND sii.item_code = soi.item_code
            AND sii.docstatus = 1

        WHERE so.docstatus = 1

        GROUP BY so.country_of_destination, soi.item_code, so.currency, so.conversion_rate
    """, as_dict=1)

    result = {}
    column_totals = {}
    currency_value = None
    total_inr = 0

    for r in rows:

        pending = r.so_amount - r.si_amount

        if pending <= 0:
            continue

        currency_value = r.currency
        country = r.country or ""

        if country not in result:
            result[country] = {
                "country": country,
                "currency": currency_value,
                "grand_total": 0
            }

        fieldname = frappe.scrub(r.item_code)

        result[country][fieldname] = result[country].get(fieldname, 0) + pending
        result[country]["grand_total"] += pending

        column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

        # INR conversion
        total_inr += pending * r.conversion_rate

    data = list(result.values())

    # Grand Total Row (USD)
    total_row = {
        "country": "Grand Total",
        "currency": currency_value
    }

    grand_total_sum = 0

    for field in column_totals:
        total_row[field] = column_totals[field]
        grand_total_sum += column_totals[field]

    total_row["grand_total"] = grand_total_sum

    data.append(total_row)

    # INR Total Row
    inr_row = {
        "country": "Grand Total (INR)",
        "grand_total": total_inr
    }

    data.append(inr_row)

    return data