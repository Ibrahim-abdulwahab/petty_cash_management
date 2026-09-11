# Copyright (c) 2026, OmniSync and contributors
# For license information, please see license.txt..

import frappe

from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, flt, formatdate
from frappe.utils.pdf import get_pdf


class PettyCashSettlement(Document):

    def validate(self):
        self.validate_center_officer_and_month()
        self.load_petty_cash_configuration()
        self.validate_expenses()
        self.calculate_totals()

    def on_update(self):
        if (
            self.workflow_state == "Completed"
            and self.has_value_changed("workflow_state")
        ):
            self.create_whish_journal_entry()
            self.reload()
            self.generate_pdf_report()

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
    def generate_pdf_report(self):
        html = self.build_pdf_html()

        pdf_content = get_pdf(html)

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{self.name}.pdf",
            "content": pdf_content,
            "is_private": 1,
            "attached_to_doctype": "Petty Cash Settlement",
            "attached_to_name": self.name,
        })

        file_doc.save(ignore_permissions=True)

        return file_doc.file_url

    def build_pdf_html(self):
        expense_rows = []

        for number, expense in enumerate(self.expenses, start=1):
            expense_rows.append(
                f"""
                <tr>
                    <td class="number">{number}</td>
                    <td>{escape_html(str(expense.expense_date or ""))}</td>
                    <td>{escape_html(expense.expense_item or "")}</td>
                    <td>{escape_html(expense.invoice_number or "")}</td>
                    <td>{escape_html(expense.supplier or "")}</td>
                    <td>{escape_html(expense.related_details or "")}</td>
                    <td class="amount">
                        {flt(expense.amount, 2):,.2f}
                    </td>
                </tr>
                """
            )

        return f"""
        <style>

            @page {{
                size: A4 landscape;
                margin: 0.6in;
            }}

            .report {{
                font-family: Calibri, Arial, sans-serif;
                font-size: 10pt;
                color: #000;
            }}

            .title {{
                text-align: center;
                font-size: 20pt;
                font-weight: bold;
                margin-bottom: 20px;
            }}

            .subtitle {{
                text-align: center;
                font-size: 10pt;
                margin-bottom: 20px;
            }}

            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}

            .info-table td {{
                border: 1px solid #000;
                padding: 6px;
            }}

            .info-label {{
                font-weight: bold;
                background: #d9eaf7;
                width: 16%;
            }}

            .expense-table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}

            .expense-table th,
            .expense-table td {{
                border: 1px solid #000;
                padding: 4px;
                vertical-align: middle;
            }}

            .expense-table th {{
                background: #9dc3e6;
                font-weight: bold;
                text-align: center;
                font-size: 9pt;
            }}

            .expense-table td {{
                font-size: 9pt;
            }}

            .number {{
                width: 4%;
                text-align: center;
            }}

            .date {{
                width: 9%;
            }}

            .item {{
                width: 17%;
            }}

            .invoice {{
                width: 11%;
            }}

            .supplier {{
                width: 14%;
            }}

            .details {{
                width: 29%;
            }}

            .amount {{
                width: 16%;
                text-align: right;
            }}

            .totals-table {{
                width: 40%;
                margin-left: auto;
                margin-top: 20px;
                border-collapse: collapse;
            }}

            .totals-table td {{
                border: 1px solid #000;
                padding: 6px;
            }}

            .total-label {{
                font-weight: bold;
                background: #d9eaf7;
            }}

            .footer {{
                margin-top: 30px;
                font-size: 9pt;
            }}

        </style>

        <div class="report">

            <div class="title">
                PETTY CASH SETTLEMENT REPORT
            </div>

            <div class="subtitle">
                Settlement: {escape_html(self.name)}
            </div>

            <table class="info-table">

                <tr>
                    <td class="info-label">Center Officer</td>
                    <td>{escape_html(self.center_officer or "")}</td>

                    <td class="info-label">Month</td>
                    <td>{formatdate(self.month) if self.month else ""}</td>
                </tr>

                <tr>
                    <td class="info-label">Cost Center</td>
                    <td>{escape_html(self.cost_center or "")}</td>

                    <td class="info-label">Petty Cash Account</td>
                    <td>{escape_html(self.petty_cash_account or "")}</td>
                </tr>

                <tr>
                    <td class="info-label">Petty Cash Limit</td>
                    <td>{flt(self.petty_cash_limit, 2):,.2f}</td>

                    <td class="info-label">Payment Method</td>
                    <td>{escape_html(self.payment_method or "")}</td>
                </tr>

                <tr>
                    <td class="info-label">Payment Date</td>
                    <td>{formatdate(self.payment_date) if self.payment_date else ""}</td>

                    <td class="info-label">Payment Status</td>
                    <td>{escape_html(self.payment_status or "")}</td>
                </tr>

            </table>

            <table class="expense-table">

                <thead>
                    <tr>
                        <th class="number">No.</th>
                        <th class="date">Date</th>
                        <th class="item">Expense Item</th>
                        <th class="invoice">Invoice No.</th>
                        <th class="supplier">Supplier</th>
                        <th class="details">Related Details</th>
                        <th class="amount">Amount</th>
                    </tr>
                </thead>

                <tbody>
                    {"".join(expense_rows)}
                </tbody>

            </table>

            <table class="totals-table">

                <tr>
                    <td class="total-label">Petty Cash Limit</td>
                    <td class="amount">
                        {flt(self.petty_cash_limit, 2):,.2f}
                    </td>
                </tr>

                <tr>
                    <td class="total-label">Total Expenses</td>
                    <td class="amount">
                        {flt(self.total_expenses, 2):,.2f}
                    </td>
                </tr>

                <tr>
                    <td class="total-label">Remaining Balance</td>
                    <td class="amount">
                        {flt(self.remaining_balance, 2):,.2f}
                    </td>
                </tr>

            </table>

            <div class="footer">

                <p>
                    <strong>Journal Entry:</strong>
                    {escape_html(self.journal_entry or "")}
                </p>

                <p>
                    <strong>Payment Status:</strong>
                    {escape_html(self.payment_status or "")}
                </p>

                <p>
                    This report was generated automatically by the
                    Center Expense Management system.
                </p>

            </div>

        </div>
        """
