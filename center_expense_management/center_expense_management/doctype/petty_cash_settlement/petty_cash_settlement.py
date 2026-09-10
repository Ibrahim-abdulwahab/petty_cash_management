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

    def on_submit(self):
        if self.workflow_state == "Completed":
            self.create_whish_journal_entry()

    def validate_center_officer_and_month(self):
        if not self.center_officer or not self.month:
            return

        month_start = frappe.utils.get_first_day(self.month)
        month_end = frappe.utils.get_last_day(self.month)

        existing = frappe.db.exists(
            "Petty Cash Settlement",
            {
                "center_officer": self.center_officer,
                "month": ["between", [month_start, month_end]],
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
    def create_whish_journal_entry(self):
        if self.payment_status == "Paid":
            frappe.throw(
                "This Petty Cash Settlement has already been paid."
            )

        if self.journal_entry:
            frappe.throw(
                "A Journal Entry is already linked to this settlement."
            )

        if self.payment_method != "Whish":
            frappe.throw(
                "Payment Method must be Whish."
            )

        if not self.payment_date:
            frappe.throw(
                "Payment Date is required before creating the Journal Entry."
            )

        whish_account = frappe.db.get_value(
            "Account",
            {
                "name": "Whish - OS",
                "is_group": 0,
                "disabled": 0
            },
            ["name", "company"],
            as_dict=True
        )

        if not whish_account:
            frappe.throw(
                "The Whish - OS account could not be found or is disabled."
            )

        company = whish_account.company

        cost_center_company = frappe.db.get_value(
            "Cost Center",
            self.cost_center,
            "company"
        )

        if cost_center_company != company:
            frappe.throw(
                "The Cost Center and Whish account belong to different companies."
            )

        for expense in self.expenses:
            expense_account_company = frappe.db.get_value(
                "Account",
                expense.expense_account,
                "company"
            )

            if expense_account_company != company:
                frappe.throw(
                    f"Expense row {expense.idx}: "
                    f"Expense Account {expense.expense_account} "
                    f"does not belong to Company {company}."
                )

        journal_entry = frappe.new_doc("Journal Entry")

        journal_entry.posting_date = self.payment_date
        journal_entry.company = company
        journal_entry.user_remark = (
            f"Petty Cash Settlement {self.name}"
        )

        for expense in self.expenses:
            journal_entry.append(
                "accounts",
                {
                    "account": expense.expense_account,
                    "debit_in_account_currency": expense.amount,
                    "cost_center": self.cost_center
                }
            )

        journal_entry.append(
            "accounts",
            {
                "account": whish_account.name,
                "credit_in_account_currency": self.total_expenses
            }
        )

        journal_entry.insert()
        journal_entry.submit()

        self.db_set("journal_entry", journal_entry.name)
        self.db_set("payment_status", "Paid")

        return journal_entry.name
