# Copyright (c) 2026, craft and contributors
# For license information, please see license.txt




# import frappe


# def execute(filters=None):
#     items = get_items()
#     columns = get_columns(items)
#     data = get_data(items)

#     return columns, data


# def get_items():
#     return frappe.db.sql("""
#         SELECT DISTINCT soi.item_code, i.item_name
#         FROM `tabSales Order Item` soi
#         JOIN `tabSales Order` so ON so.name = soi.parent
#         JOIN `tabItem` i ON i.name = soi.item_code
#         WHERE so.docstatus = 1
#         ORDER BY i.item_name
#     """, as_dict=1)


# def get_columns(items):

#     columns = [
#         {
#             "label": "Country",
#             "fieldname": "country",
#             "fieldtype": "Data",
#             "width": 200
#         }
#     ]

#     for item in items:
#         columns.append({
#             "label": item.item_name,
#             "fieldname": frappe.scrub(item.item_code),
#             "fieldtype": "Currency",
#             "options": "currency",
#             "width": 140
#         })

#     columns.append({
#         "label": "Grand Total",
#         "fieldname": "grand_total",
#         "fieldtype": "Currency",
#         "options": "currency",
#         "width": 160
#     })

#     return columns


# def get_data(items):

#     rows = frappe.db.sql("""
#         SELECT
#             so.country_of_destination AS country,
#             so.currency,
#             so.conversion_rate,
#             soi.item_code,
#             SUM(soi.amount) AS so_amount,
#             IFNULL(SUM(sii.amount),0) AS si_amount

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi
#             ON soi.parent = so.name

#         LEFT JOIN `tabSales Invoice Item` sii
#             ON sii.sales_order = so.name
#             AND sii.item_code = soi.item_code
#             AND sii.docstatus = 1

#         WHERE so.docstatus = 1

#         GROUP BY so.country_of_destination, soi.item_code, so.currency, so.conversion_rate
#     """, as_dict=1)

#     result = {}
#     column_totals = {}
#     currency_value = None
#     total_inr = 0

#     for r in rows:

#         pending = r.so_amount - r.si_amount

#         if pending <= 0:
#             continue

#         currency_value = r.currency
#         country = r.country or ""

#         if country not in result:
#             result[country] = {
#                 "country": country,
#                 "currency": currency_value,
#                 "grand_total": 0
#             }

#         fieldname = frappe.scrub(r.item_code)

#         result[country][fieldname] = result[country].get(fieldname, 0) + pending
#         result[country]["grand_total"] += pending

#         column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

#         # INR conversion
#         total_inr += pending * r.conversion_rate

#     data = list(result.values())

#     # Grand Total Row (USD)
#     total_row = {
#         "country": "Grand Total",
#         "currency": currency_value
#     }

#     grand_total_sum = 0

#     for field in column_totals:
#         total_row[field] = column_totals[field]
#         grand_total_sum += column_totals[field]

#     total_row["grand_total"] = grand_total_sum

#     data.append(total_row)

#     # INR Total Row
#     inr_row = {
#         "country": "Grand Total (INR)",
#         "grand_total": total_inr
#     }

#     data.append(inr_row)

#     return data




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
        -- Requirement: Filter out items from orders with no country mentioned
        AND so.country_of_destination IS NOT NULL 
        AND so.country_of_destination <> ''
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
    # Requirement: Added WHERE condition to exclude empty/null country_of_destination
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
            AND so.country_of_destination IS NOT NULL
            AND so.country_of_destination <> ''
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
        country = r.country # No longer needs fallback to "" due to SQL filter

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

    # Only add total rows if there is actual data
    if data:
        # Grand Total Row (Original Currency)
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