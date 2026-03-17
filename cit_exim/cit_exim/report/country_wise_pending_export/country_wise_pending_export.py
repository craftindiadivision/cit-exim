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
#     return [
#         {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Float", "width": 120},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Float", "width": 120},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Float", "width": 120},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Float", "width": 120},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Float", "width": 120},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Float", "width": 150},
#     ]

# def get_data(filters):
#     conditions = ""
    
#     if filters.get("company"):
#         conditions += f" AND si.company = {frappe.db.escape(filters.get('company'))}"
    
#     if filters.get("from_date"):
#         conditions += f" AND si.posting_date >= {frappe.db.escape(filters.get('from_date'))}"
        
#     if filters.get("to_date"):
#         conditions += f" AND si.posting_date <= {frappe.db.escape(filters.get('to_date'))}"

#     query = f"""
#         SELECT
#             si.country_of_destination AS country,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.qty ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.qty ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.qty ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.qty ELSE 0 END) AS fo,
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.qty ELSE 0 END) AS fsp,
#             SUM(CASE WHEN sii.item_group = 'FG-Fish Meal' THEN sii.qty ELSE 0 END) AS grand_total
#         FROM 
#             `tabSales Invoice` si
#         JOIN 
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1 
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             AND si.country_of_destination IS NOT NULL
#             {conditions}
#         GROUP BY 
#             si.country_of_destination
#         ORDER BY 
#             si.country_of_destination ASC
#     """
    
#     return frappe.db.sql(query, as_dict=True)




# import frappe
# from frappe import _
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns()
#     data = get_data(filters)

#     # Remove zero values
#     numeric_fields = ["fm_60","fm_62","fm_65","fo","fsp","grand_total"]

#     for row in data:
#         for field in numeric_fields:
#             if flt(row.get(field)) == 0:
#                 row[field] = ""

#     # Add Grand Total row
#     if data:
#         grand_total_row = calculate_grand_total(data)
#         data.append(grand_total_row)

#     return columns, data


# def get_columns():
#     return [
#         {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 120},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 120},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 120},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 120},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 120},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 150},
#     ]


# def get_data(filters):

#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND si.company = %(company)s"

#     if filters.get("from_date"):
#         conditions += " AND si.posting_date >= %(from_date)s"

#     if filters.get("to_date"):
#         conditions += " AND si.posting_date <= %(to_date)s"

#     query = f"""
#         SELECT
#             si.country_of_destination AS country,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 60' THEN sii.qty ELSE 0 END) AS fm_60,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 62' THEN sii.qty ELSE 0 END) AS fm_62,
#             SUM(CASE WHEN sii.item_code = 'FG-Fish Meal 65' THEN sii.qty ELSE 0 END) AS fm_65,
#             SUM(CASE WHEN sii.item_code = 'Fish Oil' THEN sii.qty ELSE 0 END) AS fo,
#             SUM(CASE WHEN sii.item_code = 'Soluble Paste' THEN sii.qty ELSE 0 END) AS fsp,
#             SUM(CASE WHEN sii.item_group = 'FG-Fish Meal' THEN sii.qty ELSE 0 END) AS grand_total
#         FROM 
#             `tabSales Invoice` si
#         JOIN 
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND IFNULL(si.custom_payment_status, 0) != 1
#             AND si.country_of_destination IS NOT NULL
#             {conditions}
#         GROUP BY 
#             si.country_of_destination
#         ORDER BY 
#             si.country_of_destination ASC
#     """

#     return frappe.db.sql(query, filters, as_dict=True)


# def calculate_grand_total(data):

#     totals = {
#         "country": "<b>" + _("Grand Total") + "</b>",
#         "fm_60": 0,
#         "fm_62": 0,
#         "fm_65": 0,
#         "fo": 0,
#         "fsp": 0,
#         "grand_total": 0
#     }

#     for row in data:
#         totals["fm_60"] += flt(row.get("fm_60"))
#         totals["fm_62"] += flt(row.get("fm_62"))
#         totals["fm_65"] += flt(row.get("fm_65"))
#         totals["fo"] += flt(row.get("fo"))
#         totals["fsp"] += flt(row.get("fsp"))
#         totals["grand_total"] += flt(row.get("grand_total"))

#     # Make totals bold and remove zero
#     for field in ["fm_60","fm_62","fm_65","fo","fsp","grand_total"]:
#         if totals[field] == 0:
#             totals[field] = ""
#         else:
#             totals[field] = f"<b>{totals[field]}</b>"

#     return totals




# import frappe
# from frappe import _
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns()
#     data = get_data(filters)

#     numeric_fields = ["fm_60","fm_62","fm_65","fo","fsp","grand_total"]

#     for row in data:
#         for field in numeric_fields:
#             if flt(row.get(field)) == 0:
#                 row[field] = ""

#     if data:
#         grand_total_row = calculate_grand_total(data)
#         data.append(grand_total_row)

#     return columns, data


# def get_columns():
#     return [
#         {"label": _("Country"), "fieldname": "country", "fieldtype": "Data", "width": 180},
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 120},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 120},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 120},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 120},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 120},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 150},
#     ]


# def get_data(filters):

#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND so.company = %(company)s"

#     if filters.get("from_date"):
#         conditions += " AND so.transaction_date >= %(from_date)s"

#     if filters.get("to_date"):
#         conditions += " AND so.transaction_date <= %(to_date)s"


#     query = f"""
#         SELECT
#             so.country_of_destination AS country,

#             SUM(
#                 CASE 
#                     WHEN soi.item_code = 'FG-Fish Meal 60' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS fm_60,

#             SUM(
#                 CASE 
#                     WHEN soi.item_code = 'FG-Fish Meal 62' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS fm_62,

#             SUM(
#                 CASE 
#                     WHEN soi.item_code = 'FG-Fish Meal 65' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS fm_65,

#             SUM(
#                 CASE 
#                     WHEN soi.item_code = 'Fish Oil' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS fo,

#             SUM(
#                 CASE 
#                     WHEN soi.item_code = 'Soluble Paste' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS fsp,

#             SUM(
#                 CASE 
#                     WHEN soi.item_group = 'FG-Fish Meal' 
#                     THEN (soi.qty - IFNULL(inv.invoiced_qty,0))
#                     ELSE 0 
#                 END
#             ) AS grand_total

#         FROM `tabSales Order` so

#         JOIN `tabSales Order Item` soi 
#             ON soi.parent = so.name

#         LEFT JOIN (
#             SELECT
#                 sii.so_detail,
#                 SUM(sii.qty) AS invoiced_qty
#             FROM `tabSales Invoice Item` sii
#             JOIN `tabSales Invoice` si 
#                 ON si.name = sii.parent
#             WHERE si.docstatus = 1
#             GROUP BY sii.so_detail
#         ) inv
#         ON inv.so_detail = soi.name

#         WHERE
#             so.docstatus = 1
#             AND so.status NOT IN ('Closed','Completed')
#             AND so.country_of_destination IS NOT NULL
#             {conditions}

#         GROUP BY
#             so.country_of_destination

#         ORDER BY
#             so.country_of_destination ASC
#     """

#     return frappe.db.sql(query, filters, as_dict=True)



# def calculate_grand_total(data):

#     totals = {
#         "country": "<b>" + _("Grand Total") + "</b>",
#         "fm_60": 0,
#         "fm_62": 0,
#         "fm_65": 0,
#         "fo": 0,
#         "fsp": 0,
#         "grand_total": 0
#     }

#     for row in data:
#         totals["fm_60"] += flt(row.get("fm_60"))
#         totals["fm_62"] += flt(row.get("fm_62"))
#         totals["fm_65"] += flt(row.get("fm_65"))
#         totals["fo"] += flt(row.get("fo"))
#         totals["fsp"] += flt(row.get("fsp"))
#         totals["grand_total"] += flt(row.get("grand_total"))

#     for field in ["fm_60","fm_62","fm_65","fo","fsp","grand_total"]:
#         if totals[field] == 0:
#             totals[field] = ""
#         else:
#             totals[field] = f"<b>{totals[field]}</b>"

#     return totals










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
            "fieldtype": "Float",
            "width": 120
        })

    columns.append({
        "label": "Grand Total",
        "fieldname": "grand_total",
        "fieldtype": "Float",
        "width": 140
    })

    return columns


def get_data(items):

    rows = frappe.db.sql("""
        SELECT
            so.country_of_destination AS country,
            soi.item_code,
            SUM(soi.qty) AS so_qty,
            IFNULL(SUM(sii.qty),0) AS si_qty

        FROM `tabSales Order` so

        JOIN `tabSales Order Item` soi
            ON soi.parent = so.name

        LEFT JOIN `tabSales Invoice Item` sii
            ON sii.sales_order = so.name
            AND sii.item_code = soi.item_code
            AND sii.docstatus = 1

        WHERE so.docstatus = 1

        GROUP BY so.country_of_destination, soi.item_code
    """, as_dict=1)

    result = {}
    column_totals = {}

    for r in rows:

        pending = r.so_qty - r.si_qty

        if pending <= 0:
            continue

        country = r.country or ""

        if country not in result:
            result[country] = {"country": country, "grand_total": 0}

        fieldname = frappe.scrub(r.item_code)

        result[country][fieldname] = result[country].get(fieldname, 0) + pending
        result[country]["grand_total"] += pending

        column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

    data = list(result.values())

    # create final grand total row
    total_row = {"country": "Grand Total"}
    grand_total_sum = 0

    for field in column_totals:
        total_row[field] = column_totals[field]
        grand_total_sum += column_totals[field]

    total_row["grand_total"] = grand_total_sum

    data.append(total_row)

    return data