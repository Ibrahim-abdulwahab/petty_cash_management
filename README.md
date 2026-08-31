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

