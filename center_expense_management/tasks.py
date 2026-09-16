import frappe
from frappe.utils import get_first_day, today


def create_monthly_petty_cash_whish():
    month = get_first_day(today())

    existing = frappe.db.exists(
        "Petty Cash Whish",
        {
            "month_and_year": month
        }
    )

    if existing:
        return

    whish = frappe.get_doc({
        "doctype": "Petty Cash Whish",
        "month_and_year": month
    })

    whish.insert(ignore_permissions=True)

    frappe.db.commit()
