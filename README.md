# Center Expense Management

A Frappe application for managing **center petty cash expenses and monthly petty cash settlements**.

The application allows Center Officers to record their monthly expenses, automatically calculate petty cash balances, and submit settlements through a controlled multi-stage approval workflow.

Once approved, the Treasurer can process the payment through **Whish**. The application automatically creates the corresponding ERPNext Journal Entry, marks the settlement as paid, and generates a **PDF Petty Cash Settlement Report** that is attached to the settlement.

## Features

* Petty Cash Configuration for each Center Officer
* Monthly Petty Cash Settlement
* Expense tracking with:

  * Expense Item
  * Expense Date
  * Invoice Number
  * Supplier
  * Expense Account
  * Related Details
  * Amount
  * Invoice/Receipt Attachment
* Automatic loading of:

  * Cost Center
  * Petty Cash Account
  * Petty Cash Limit
* Automatic calculation of:

  * Total Expenses
  * Remaining Balance
* Validation of expense amounts and required information
* Prevention of duplicate monthly settlements for the same Center Officer
* Mandatory receipt for every expense
* Server-side validation to prevent expenses exceeding the petty cash limit
* Multi-stage settlement approval workflow
* Accountant Review
* Finance Review
* Operations Approval
* Treasurer Processing
* Accountant return-to-Center-Officer capability
* Finance return-to-Accountant capability
* Operations return-to-Finance capability
* Whish payment processing
* Automatic Journal Entry creation when the Treasurer completes the settlement
* Automatic linking of the Journal Entry to the settlement
* Automatic payment status update to `Paid`
* Automatic PDF settlement report generation
* Automatic attachment of the PDF report to the settlement
* Prevention of duplicate payment processing
* Prevention of duplicate Journal Entry creation

## DocTypes

### Petty Cash Configuration

Stores the petty cash configuration for each Center Officer, including:

* Center Officer
* Cost Center
* Petty Cash Account
* Petty Cash Limit

The configuration determines the petty cash amount available to the Center Officer and the accounting information used by monthly settlements.

### Petty Cash Expense

Child table used to record individual expenses within a Petty Cash Settlement.

Each expense contains:

* Expense Item
* Expense Date
* Invoice Number
* Supplier
* Expense Account
* Related Details
* Amount
* Receipt

### Petty Cash Settlement

The main document used to create, review, approve, and process a Center Officer's monthly petty cash settlement.

It contains:

* Center Officer
* Month
* Cost Center
* Petty Cash Account
* Petty Cash Limit
* Total Expenses
* Remaining Balance
* Expenses
* Payment Method
* Payment Date
* Journal Entry
* Payment Status

The settlement also receives an automatically generated PDF report after successful Treasurer processing.

## Workflow

The Petty Cash Settlement follows a multi-stage approval workflow:

```text
Draft
  │
  │ Submit for Accountant Review
  ▼
Pending Accountant Review
  │
  │ Approve
  ▼
Pending Finance Review
  │
  │ Approve
  ▼
Pending Operations Approval
  │
  │ Approve
  ▼
Pending Treasurer Processing
  │
  │ Complete
  ▼
Completed
```

### Workflow Roles

| Stage                | Role           |
| -------------------- | -------------- |
| Draft / Submission   | Center Officer |
| Accountant Review    | Accountant     |
| Finance Review       | Finance        |
| Operations Approval  | Operations     |
| Treasurer Processing | Treasurer      |

### Workflow Return Paths

The workflow allows corrections to be requested at different review stages.

#### Accountant → Center Officer

```text
Pending Accountant Review
        │
        │ Return to Center Officer
        ▼
      Draft
```

#### Finance → Accountant

```text
Pending Finance Review
        │
        │ Return to Accountant
        ▼
Pending Accountant Review
```

#### Operations → Finance

```text
Pending Operations Approval
        │
        │ Return to Finance
        ▼
Pending Finance Review
```

This provides a controlled review chain where each department can return the settlement to the appropriate preceding stage rather than restarting the entire process.

## Accounting / Whish Payment

The Treasurer processes approved settlements using **Whish**.

The application automatically creates a Journal Entry when the settlement moves from:

```text
Pending Treasurer Processing
        ↓
Completed
```

The Journal Entry records:

```text
Debit  → Expense Account(s)
Credit → Whish - OS
```

For example, if a settlement contains a 100 expense:

```text
Dr  Miscellaneous Expenses - OS    100
Cr  Whish - OS                     100
```

If multiple expenses exist, each expense is posted separately:

```text
Dr  Expense Account 1              Amount 1
Dr  Expense Account 2              Amount 2
Dr  Expense Account 3              Amount 3
...
Cr  Whish - OS                     Total Expenses
```

The expense debit entries use the settlement's configured **Cost Center**.

The Journal Entry:

* Uses the settlement's Payment Date as the posting date.
* Uses the same company as the Whish account.
* Posts each expense to its selected Expense Account.
* Applies the settlement Cost Center to the expense entries.
* Credits the `Whish - OS` account with the total settlement amount.
* Is automatically submitted.
* Is automatically linked to the Petty Cash Settlement.
* Changes the settlement Payment Status to `Paid`.

The application also validates that the Whish account, Cost Center, and Expense Accounts belong to the same company.

### Payment Protection

The application prevents:

* Paying the same settlement more than once.
* Creating multiple Journal Entries for the same settlement.
* Using a disabled or missing Whish account.
* Using Expense Accounts belonging to a different company.
* Using a Cost Center belonging to a different company from the Whish account.

## PDF Settlement Report

When the Treasurer successfully completes a settlement, the application automatically generates a **Petty Cash Settlement Report PDF**.

The PDF is generated after the Journal Entry has been created and the settlement has been marked as `Paid`.

The generated report is automatically attached to the **Petty Cash Settlement** as a private Frappe File.

### PDF Report Contents

The report includes:

* Report title
* Settlement number
* Center Officer
* Month
* Cost Center
* Petty Cash Account
* Petty Cash Limit
* Payment Method
* Payment Date
* Payment Status
* Detailed expense table
* Expense Date
* Expense Item
* Invoice Number
* Supplier
* Related Details
* Expense Amount
* Total Expenses
* Remaining Balance
* Journal Entry number
* Payment Status
* System-generated report footer

The expense table contains one row for each expense recorded in the settlement.

### PDF Layout

The report is generated in **A4 landscape format** and uses a structured table-based layout with:

* Centered report title
* Settlement information section
* Expense details table
* Highlighted table headers
* Totals section
* Payment and Journal Entry information
* System-generated footer

The PDF is stored as a private file and attached directly to the corresponding settlement.

### PDF Generation Flow

```text
Treasurer clicks Complete
        │
        ▼
Validate Whish Payment
        │
        ▼
Create Journal Entry
        │
        ▼
Submit Journal Entry
        │
        ▼
Mark Payment Status = Paid
        │
        ▼
Generate PDF Report
        │
        ▼
Attach PDF to Settlement
        │
        ▼
Settlement = Completed
```

The Treasurer does not need to manually create or attach the report.

## User Guide

### 1. Configure Petty Cash

Before creating settlements, a system administrator should create a **Petty Cash Configuration** for each Center Officer.

Go to:

```text
Petty Cash Configuration → New
```

Enter:

* **Center Officer** – Select the Center Officer who will manage the petty cash.
* **Cost Center** – Select the Cost Center associated with the Center Officer.
* **Petty Cash Account** – Select the account used for petty cash.
* **Petty Cash Limit** – Enter the maximum amount available to the Center Officer.

Save the configuration.

The configuration is automatically used when the Center Officer creates a Petty Cash Settlement.

### 2. Create a Monthly Petty Cash Settlement

The Center Officer creates one settlement for each month.

Go to:

```text
Petty Cash Settlement → New
```

Select:

* **Center Officer**
* **Month**

The following fields are automatically populated from the Center Officer's Petty Cash Configuration:

* Cost Center
* Petty Cash Account
* Petty Cash Limit

The Center Officer must then add each expense separately in the **Expenses** table.

### 3. Add Expenses

Each expense should be entered as a separate row.

Complete the expense information:

| Field           | Description                                         |
| --------------- | --------------------------------------------------- |
| Expense Item    | Description or category of the expense              |
| Expense Date    | Date the expense occurred                           |
| Invoice Number  | Invoice or receipt number, if available             |
| Supplier        | Supplier associated with the expense, if applicable |
| Expense Account | Account to which the expense should be posted       |
| Related Details | Additional information about the expense            |
| Amount          | Amount paid                                         |
| Receipt         | Invoice or receipt attachment                       |

A receipt must be attached to every expense.

The application automatically calculates:

```text
Total Expenses
Remaining Balance
```

The Center Officer cannot submit the settlement if the total expenses exceed the configured Petty Cash Limit.

### 4. Submit the Settlement

After entering all expenses and attaching the required receipts, the Center Officer submits the settlement for review.

The workflow moves the settlement to:

```text
Pending Accountant Review
```

The Center Officer should review the settlement carefully before submitting it because it represents the complete petty cash expenses for that month.

A Center Officer cannot create more than one settlement for the same month.

### 5. Accountant Review

The Accountant reviews the submitted settlement.

The Accountant should verify:

* Expense details
* Expense amounts
* Expense accounts
* Receipts/invoices
* Cost Center
* Petty Cash Account
* Total Expenses
* Petty Cash Limit

If everything is correct, the Accountant approves the settlement.

The workflow moves to:

```text
Pending Finance Review
```

If corrections are required, the Accountant can return the settlement to the Center Officer.

### 6. Finance Review

The Finance user performs the financial review after Accountant approval.

The Finance user should verify:

* Expense amounts
* Expense Accounts
* Receipts/invoices
* Cost Center
* Petty Cash Account
* Petty Cash Limit
* Total Expenses
* Accounting correctness of the settlement

If everything is correct, the Finance user approves the settlement.

The workflow moves to:

```text
Pending Operations Approval
```

If corrections are required, Finance can return the settlement to the Accountant.

### 7. Operations Approval

The Operations user performs the operational review after Finance approval.

The Operations user should verify that:

* The expenses are appropriate.
* Required supporting documents are attached.
* The settlement information is complete.
* The expense accounts are correct.
* The total amount is within the petty cash limit.

If approved, the workflow moves to:

```text
Pending Treasurer Processing
```

If corrections are required, Operations can return the settlement to Finance.

### 8. Treasurer Processing

The Treasurer performs the final payment and accounting step.

The Treasurer should:

1. Open the settlement in **Pending Treasurer Processing**.
2. Verify the expenses and total amount.
3. Select:

   * **Payment Method:** `Whish`
   * **Payment Date:** Date on which the payment is processed.
4. Click **Complete**.

When the Treasurer completes the workflow, the application automatically:

1. Validates the Whish account.
2. Validates the Cost Center and company.
3. Validates each Expense Account and company.
4. Creates a Journal Entry.
5. Adds a debit entry for each expense.
6. Applies the settlement Cost Center to the expense entries.
7. Credits `Whish - OS` with the total expenses.
8. Submits the Journal Entry.
9. Stores the Journal Entry number in the settlement.
10. Changes Payment Status from `Unpaid` to `Paid`.
11. Generates the Petty Cash Settlement PDF.
12. Attaches the PDF to the settlement.

The settlement then reaches:

```text
Completed
```

No manual Journal Entry creation or PDF generation is required from the Treasurer.

### 9. View the Settlement PDF

After the Treasurer completes the settlement:

1. Open the completed **Petty Cash Settlement**.
2. Locate the **Attachments** section.
3. Open the generated PDF.

The PDF contains the settlement information, expense details, totals, payment status, and Journal Entry information.

The report is generated automatically and stored as a private attachment.

### 10. Payment Fields

The settlement contains the following payment-related fields:

| Field          | Description                                                             |
| -------------- | ----------------------------------------------------------------------- |
| Payment Method | Payment method used for the settlement. Currently `Whish`.              |
| Payment Date   | Date used as the Journal Entry posting date.                            |
| Journal Entry  | Automatically populated with the Journal Entry created for the payment. |
| Payment Status | Shows whether the settlement has been paid.                             |

The normal payment status is:

```text
Unpaid
```

After successful Treasurer processing:

```text
Paid
```

### 11. Returning a Settlement for Correction

A settlement can be returned during multiple stages of the approval process.

#### Accountant → Center Officer

```text
Pending Accountant Review
        │
        │ Return to Center Officer
        ▼
Draft
        │
        │ Correct and resubmit
        ▼
Pending Accountant Review
```

#### Finance → Accountant

```text
Pending Finance Review
        │
        │ Return to Accountant
        ▼
Pending Accountant Review
        │
        │ Approve
        ▼
Pending Finance Review
```

#### Operations → Finance

```text
Pending Operations Approval
        │
        │ Return to Finance
        ▼
Pending Finance Review
        │
        │ Approve
        ▼
Pending Operations Approval
```

This staged return process ensures that corrections are reviewed by the appropriate preceding department.

## Monthly Settlement Rules

The application enforces several rules to maintain data integrity:

* Each Center Officer can have only one settlement for a given month.
* At least one expense is required.
* Expense amounts must be greater than zero.
* An Expense Account is required for every expense.
* A receipt is required for every expense.
* Total Expenses cannot exceed the configured Petty Cash Limit.
* Cost Center is automatically loaded from the Center Officer's configuration.
* Petty Cash Account is automatically loaded from the Center Officer's configuration.
* Petty Cash Limit is automatically loaded from the Center Officer's configuration.
* The Whish account must exist, be enabled, and belong to the correct company.
* The Cost Center must belong to the same company as the Whish account.
* Every Expense Account must belong to the same company as the Whish account.
* A settlement cannot be paid twice.
* A settlement cannot create multiple Journal Entries for the same payment.
* A settlement generates its PDF report after successful payment processing.

## Validation

Validation is performed at the application/server level to protect the data even if client-side validation is bypassed.

The settlement validates:

```text
Center Officer + Month
        ↓
Petty Cash Configuration
        ↓
Expenses
        ↓
Expense Accounts
        ↓
Receipts
        ↓
Total Expenses
        ↓
Petty Cash Limit
```

If the total expenses exceed the configured limit, the settlement is rejected:

```text
Total Expenses cannot exceed the Petty Cash Limit.
```

This validation is performed on the server and is not dependent solely on browser-side scripts.

## Installation

The application is intended for **Frappe Framework v16**.

Install the app using the Frappe `bench` CLI:

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app https://github.com/Ibrahim-abdulwahab/petty_cash_management.git --branch version-16

bench --site $SITE_NAME install-app center_expense_management
```

After installation, migrate the site:

```bash
bench --site $SITE_NAME migrate
```

Clear the cache if necessary:

```bash
bench --site $SITE_NAME clear-cache
```

Restart the bench when required:

```bash
bench restart
```

## Configuration

After installing the application:

1. Create or verify the required user roles:

   * Center Officer
   * Accountant
   * Finance
   * Operations
   * Treasurer

2. Create a **Petty Cash Configuration** for each Center Officer.

3. Configure the appropriate:

   * Cost Center
   * Petty Cash Account
   * Petty Cash Limit

4. Ensure the required Expense Accounts exist and belong to the correct company.

5. Ensure the Whish account exists and is enabled:

   ```text
   Whish - OS
   ```

6. Ensure the **Petty Cash Settlement Workflow** is installed and active.

7. Ensure the users responsible for each workflow stage have the appropriate roles and permissions.

## Development

Enable developer mode on the development site:

```bash
bench set-config -g developer_mode 1
```

After making changes to application code or DocTypes, migrate the site:

```bash
bench --site $SITE_NAME migrate
```

Clear the cache:

```bash
bench --site $SITE_NAME clear-cache
```

If application assets have been changed, build the application:

```bash
bench build --app center_expense_management
```

Restart the bench when required:

```bash
bench restart
```

### Python Syntax Check

The main settlement controller can be checked with:

```bash
python3 -m py_compile center_expense_management/doctype/petty_cash_settlement/petty_cash_settlement.py
```

No output indicates that the Python file passed the syntax check.

## GitHub Repository

The project is maintained in the following GitHub repository:

```text
https://github.com/Ibrahim-abdulwahab/petty_cash_management
```

The main development branch is:

```text
version-16
```

The Frappe application contained in the repository is:

```text
center_expense_management
```

The Petty Cash Settlement workflow is stored as an application fixture:

```text
center_expense_management/fixtures/workflow.json
```

This ensures that the workflow configuration, including the Finance Review stage, can be tracked in Git and included when the application is deployed or installed on another Frappe site.

## Contributing

This app uses `pre-commit` for code formatting and linting.

Install and enable pre-commit:

```bash
cd apps/center_expense_management
pre-commit install
```

Pre-commit is configured to use:

* Ruff
* ESLint
* Prettier
* PyUpgrade

Before committing changes, check the repository:

```bash
git status
```

Then:

```bash
git add .
git commit -m "Describe your changes"
git push origin version-16
```

If the remote branch contains changes that are intentionally being replaced by the local branch, a force push can be used carefully:

```bash
git push origin version-16 --force-with-lease
```

`--force-with-lease` is preferred over `--force` because it helps prevent accidentally overwriting changes that were pushed to the remote branch by someone else.

## Project Structure

The main application structure is:

```text
center_expense_management/
│
├── center_expense_management/
│   ├── center_expense_management/
│   │   └── doctype/
│   │       ├── petty_cash_configuration/
│   │       ├── petty_cash_expense/
│   │       └── petty_cash_settlement/
│   │
│   ├── fixtures/
│   │   └── workflow.json
│   │
│   ├── hooks.py
│   └── modules.txt
│
├── README.md
├── license.txt
├── pyproject.toml
└── requirements.txt
```

The main Petty Cash Settlement controller is responsible for:

* Loading petty cash configuration
* Validating the Center Officer and month
* Validating expenses
* Calculating totals
* Enforcing the petty cash limit
* Creating the Whish Journal Entry
* Validating accounting company consistency
* Linking the Journal Entry to the settlement
* Updating the payment status
* Generating the PDF settlement report
* Attaching the PDF report to the settlement

## License

MIT


