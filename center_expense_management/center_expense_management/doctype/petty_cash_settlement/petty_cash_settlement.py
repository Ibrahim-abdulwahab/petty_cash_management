# Copyright (c) 2026, OmniSync and contributors
# For license information, please see license.txt..

import frappe
from frappe.model.document import Document


class PettyCashSettlement(Document):

    def validate(self):
        self.validate_center_officer_and_month()
        self.load_petty_cash_configuration()
        self.validate_expenses()
        self.calculate_totals()

    def validate_center_officer_and_month(self):
        if not self.center_officer or not self.month:
            return

        existing = frappe.db.exists(
            "Petty Cash Settlement",
            {
                "center_officer": self.center_officer,
                "month": self.month,
                "name": ["!=", self.name]
            }
        )

        if existing:
            frappe.throw(
                "A Petty Cash Settlement already exists for this Center Officer and month."
            )

    def load_petty_cash_configuration(self):
        config = frappe.db.get_value(
            "Petty Cash Configuration",
            {"center_officer": self.center_officer},
            ["cost_center", "petty_cash_account", "petty_cash_limit"],
            as_dict=True
        )

        if not config:
            frappe.throw(
                "No Petty Cash Configuration was found for this Center Officer."
            )

        self.cost_center = config.cost_center
        self.petty_cash_account = config.petty_cash_account
        self.petty_cash_limit = config.petty_cash_limit

    def validate_expenses(self):
        if not self.expenses:
            frappe.throw(
                "At least one expense is required."
            )

        for expense in self.expenses:

            if not expense.amount or expense.amount <= 0:
                frappe.throw(
                    f"Expense row {expense.idx}: Amount must be greater than zero."
                )

            if not expense.expense_account:
                frappe.throw(
                    f"Expense row {expense.idx}: Expense Account is required."
                )

            if not expense.receipt:
                frappe.throw(
                    f"Receipt is required for expense row {expense.idx}."
                )

    def calculate_totals(self):
        total = sum(
            expense.amount or 0
            for expense in self.expenses
        )

        self.total_expenses = total
        self.remaining_balance = self.petty_cash_limit - total

        if self.total_expenses > self.petty_cash_limit:
            frappe.throw(
                "Total Expenses cannot exceed the Petty Cash Limit."
            )
