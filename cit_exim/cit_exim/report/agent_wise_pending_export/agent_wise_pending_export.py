



# import frappe
# from frappe import _
# from frappe.utils import flt


# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns()
#     raw_data = get_data(filters)

#     data = []

#     # Format normal rows
#     for row in raw_data:
#         format_row(row)
#         data.append(row)

#     # Add Grand Total row
#     if data:
#         total_row = calculate_totals(data)
#         data.append(total_row)

#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": _("Agent"),
#             "fieldname": "agent",
#             "fieldtype": "Data",
#             "width": 180
#         },
#         {"label": _("FM 60%"), "fieldname": "fm_60", "fieldtype": "Data", "width": 110},
#         {"label": _("FM 62%"), "fieldname": "fm_62", "fieldtype": "Data", "width": 110},
#         {"label": _("FM 65%"), "fieldname": "fm_65", "fieldtype": "Data", "width": 110},
#         {"label": _("FO"), "fieldname": "fo", "fieldtype": "Data", "width": 110},
#         {"label": _("FSP"), "fieldname": "fsp", "fieldtype": "Data", "width": 110},
#         {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Data", "width": 140},
#     ]


# def get_data(filters):

#     conditions = ""

#     if filters.get("agent"):
#         conditions += " AND so.custom_agent = %(agent)s"

#     if filters.get("from_date"):
#         conditions += " AND so.transaction_date >= %(from_date)s"

#     if filters.get("to_date"):
#         conditions += " AND so.transaction_date <= %(to_date)s"

#     query = f"""
#         SELECT
#             so.custom_agent AS agent,

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
#             ON inv.so_detail = soi.name

#         WHERE
#             so.docstatus = 1
#             AND so.custom_agent IS NOT NULL
#             AND so.custom_agent != ''
#             {conditions}

#         GROUP BY
#             so.custom_agent

#         ORDER BY
#             so.custom_agent ASC
#     """

#     return frappe.db.sql(query, filters, as_dict=True)


# def format_row(row):
#     numeric_fields = ["fm_60", "fm_62", "fm_65", "fo", "fsp", "grand_total"]

#     for field in numeric_fields:
#         value = flt(row.get(field))

#         if value == 0:
#             row[field] = ""
#         else:
#             row[field] = value


# def calculate_totals(data):
#     totals = {
#         "agent": "<b>" + _("Grand Total") + "</b>",
#         "fm_60": 0,
#         "fm_62": 0,
#         "fm_65": 0,
#         "fo": 0,
#         "fsp": 0,
#         "grand_total": 0
#     }

#     for row in data:
#         totals["fm_60"] += flt(row.get("fm_60", 0))
#         totals["fm_62"] += flt(row.get("fm_62", 0))
#         totals["fm_65"] += flt(row.get("fm_65", 0))
#         totals["fo"] += flt(row.get("fo", 0))
#         totals["fsp"] += flt(row.get("fsp", 0))
#         totals["grand_total"] += flt(row.get("grand_total", 0))

#     totals["fm_60"] = f"<b>{totals['fm_60']}</b>" if totals["fm_60"] else ""
#     totals["fm_62"] = f"<b>{totals['fm_62']}</b>" if totals["fm_62"] else ""
#     totals["fm_65"] = f"<b>{totals['fm_65']}</b>" if totals["fm_65"] else ""
#     totals["fo"] = f"<b>{totals['fo']}</b>" if totals["fo"] else ""
#     totals["fsp"] = f"<b>{totals['fsp']}</b>" if totals["fsp"] else ""
#     totals["grand_total"] = f"<b>{totals['grand_total']}</b>" if totals["grand_total"] else ""

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
            "label": "Agent",
            "fieldname": "agent",
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
            so.custom_agent AS agent,
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

        GROUP BY so.custom_agent, soi.item_code
    """, as_dict=1)

    result = {}
    column_totals = {}

    for r in rows:

        pending = r.so_qty - r.si_qty

        if pending <= 0:
            continue

        agent = r.agent or ""

        if agent not in result:
            result[agent] = {"agent": agent, "grand_total": 0}

        fieldname = frappe.scrub(r.item_code)

        result[agent][fieldname] = result[agent].get(fieldname, 0) + pending
        result[agent]["grand_total"] += pending

        column_totals[fieldname] = column_totals.get(fieldname, 0) + pending

    data = list(result.values())

    # Final Grand Total row
    total_row = {"agent": "Grand Total"}
    grand_total_sum = 0

    for field in column_totals:
        total_row[field] = column_totals[field]
        grand_total_sum += column_totals[field]

    total_row["grand_total"] = grand_total_sum

    data.append(total_row)

    return data