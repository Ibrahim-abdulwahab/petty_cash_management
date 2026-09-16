# Copyright (c) 2026, OmniSync and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PettyCashWhish(Document):

    def before_insert(self):
        if not self.month_and_year:
            frappe.throw("Month and Year is required.")

        month = self.month_and_year.month
        year = self.month_and_year.year

        self.name = f"PCW-{month:02d}-{year}"
