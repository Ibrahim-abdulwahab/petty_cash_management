# Center Expense Management

A Frappe application for managing **center petty cash expenses and monthly petty cash settlements**.

The application allows center officers to record expenses, automatically calculate petty cash balances, and submit monthly settlements through a controlled approval workflow.

## Features

* Petty Cash Configuration for each Center Officer
* Monthly Petty Cash Settlement
* Expense tracking with:

  * Expense item
  * Expense date
  * Invoice number
  * Supplier
  * Expense account
  * Related details
  * Amount
  * Invoice/receipt attachment
* Automatic calculation of:

  * Petty Cash Limit
  * Total Expenses
  * Remaining Balance
* Validation of expense amounts and required information
* Prevention of duplicate monthly settlements for the same Center Officer
* Receipt requirement for expenses
* Monthly settlement approval workflow
* Journal Entry requirement before completing a settlement

## DocTypes

### Petty Cash Configuration

Stores the petty cash configuration for each Center Officer, including:

* Center Officer
* Cost Center
* Petty Cash Account
* Petty Cash Limit

### Petty Cash Expense

Child table used to record individual expenses within a settlement.

### Petty Cash Settlement

The main document used to submit and process a Center Officer's monthly petty cash settlement.

## Workflow

The Petty Cash Settlement follows this workflow:

```text
Center Officer
      │
      ▼
Pending Accountant Review
      │
      ▼
Pending Operations Approval
      │
      ▼
Pending Treasurer Processing
      │
      ▼
Completed
```

### Roles

| Stage                | Role           |
| -------------------- | -------------- |
| Draft / Submission   | Center Officer |
| Accountant Review    | Accountant     |
| Operations Approval  | Operations     |
| Treasurer Processing | Treasurer      |

The Accountant and Operations users can return a settlement to the Center Officer for correction.

Before completion, the Treasurer must select the related Journal Entry.

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

The configuration is used automatically when the Center Officer creates a Petty Cash Settlement.

### 2. Create a Monthly Petty Cash Settlement

The Center Officer creates one settlement for each month.

Go to:

```text
Petty Cash Settlement → New
```

Select:

* **Center Officer**
* **Month**

The following fields are populated automatically from the Center Officer's Petty Cash Configuration:

* Cost Center
* Petty Cash Account
* Petty Cash Limit

The Center Officer must then add each expense separately in the **Expenses** table.

### 3. Add Expenses

Each expense should be entered as a separate row.

Complete the required information:

| Field           | Description                                         |
| --------------- | --------------------------------------------------- |
| Expense Item    | Description/category of the expense                 |
| Expense Date    | Date the expense occurred                           |
| Invoice Number  | Invoice or receipt number, if available             |
| Supplier        | Supplier associated with the expense, if applicable |
| Expense Account | Account to which the expense should be posted       |
| Related Details | Additional information about the expense            |
| Amount          | Amount paid                                         |
| Receipt         | Invoice or receipt attachment                       |

A receipt/invoice must be attached to each expense.

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

If everything is correct, the Accountant approves the settlement.

The workflow moves to:

```text
Pending Operations Approval
```

If corrections are required, the Accountant can return the settlement to the Center Officer.

### 6. Operations Approval

The Operations user performs the final operational review.

The Operations user should verify that:

* The expenses are appropriate.
* Required supporting documents are attached.
* The settlement information is complete.
* The total amount is within the petty cash limit.

If approved, the workflow moves to:

```text
Pending Treasurer Processing
```

If corrections are required, Operations can return the settlement to the Center Officer.

### 7. Treasurer Processing

The Treasurer is responsible for the final accounting/payment step.

Before completing the settlement, the Treasurer must create or identify the appropriate **Journal Entry** in ERPNext.

The Journal Entry should record the settlement's expenses against the configured Petty Cash Account.

After the Journal Entry has been created:

1. Open the Petty Cash Settlement.
2. Select the related Journal Entry in the **Journal Entry** field.
3. Verify that the Journal Entry corresponds to the settlement.
4. Complete the workflow.

The Journal Entry is required before the settlement can be completed.

The workflow then moves to:

```text
Completed
```

### 8. Returning a Settlement for Correction

A settlement can be returned to the Center Officer during the review stages.

If the Accountant or Operations user returns a settlement:

```text
Accountant / Operations
          │
          ▼
Center Officer
```

The Center Officer can correct the settlement and submit it again for review.

### 9. Monthly Settlement Rules

The application enforces several rules to maintain data integrity:

* Each Center Officer can have only one settlement for a given month.
* At least one expense must be entered.
* Expense amounts must be greater than zero.
* An Expense Account is required for each expense.
* A receipt is required for each expense.
* Total Expenses cannot exceed the configured Petty Cash Limit.
* Cost Center, Petty Cash Account, and Petty Cash Limit are loaded from the Center Officer's configuration.

## Installation

You can install this app using the Frappe `bench` CLI:

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app https://github.com/Ibrahim-abdulwahab/petty_cash_management.git --branch version-16

bench --site $SITE_NAME install-app center_expense_management
```

The application is currently intended for **Frappe Framework v16**.

## Configuration

After installing the application:

1. Create the required user roles:

   * Center Officer
   * Accountant
   * Operations
   * Treasurer
2. Create a **Petty Cash Configuration** for each Center Officer.
3. Configure the appropriate Cost Center and Petty Cash Account.
4. Set the Center Officer's Petty Cash Limit.
5. Ensure the Petty Cash Settlement workflow is installed and active.

## Development

Enable developer mode on the development site:

```bash
bench set-config -g developer_mode 1
```

After making changes to application assets:

```bash
bench --site $SITE_NAME clear-cache
bench build --app center_expense_management
```

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
git push
```

## License

MIT

