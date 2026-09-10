frappe.ui.form.on('Petty Cash Settlement', {
    center_officer: function(frm) {
        load_petty_cash_configuration(frm);
    },

    petty_cash_limit: function(frm) {
        calculate_totals(frm);
    },

    refresh: function(frm) {
        calculate_totals(frm);
    },

    expenses_add: function(frm) {
        calculate_totals(frm);
    },

    expenses_remove: function(frm) {
        calculate_totals(frm);
    },

    before_workflow_action: function(frm) {
        // Receipt required when Center Officer submits
        if (frm.selected_workflow_action === 'Submit for Accountant Review') {
            (frm.doc.expenses || []).forEach(function(row) {
                if (!row.receipt) {
                    frappe.throw(
                        __('Expense row {0}: Invoice/Receipt attachment is required before submission.', [row.idx])
                    );
                }
            });

            // One settlement per Center Officer per month
            if (frm.doc.center_officer && frm.doc.month) {
                let selected_date = frappe.datetime.str_to_obj(frm.doc.month);

                let month_start = frappe.datetime.obj_to_str(
                    new Date(
                        selected_date.getFullYear(),
                        selected_date.getMonth(),
                        1
                    )
                );

                let next_month = new Date(
                    selected_date.getFullYear(),
                    selected_date.getMonth() + 1,
                    1
                );

                let month_end = frappe.datetime.obj_to_str(next_month);

                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Petty Cash Settlement',
                        filters: [
                            ['center_officer', '=', frm.doc.center_officer],
                            ['month', '>=', month_start],
                            ['month', '<', month_end],
                            ['name', '!=', frm.doc.name]
                        ],
                        fields: ['name'],
                        limit_page_length: 1
                    },
                    async: false,
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            frappe.throw(
                                __('This Center Officer already has a Petty Cash Settlement for {0}. Only one settlement is allowed per month.', [
                                    frappe.datetime.str_to_user(frm.doc.month).substring(0, 7)
                                ])
                            );
                        }
                    }
                });
            }
        }
    },

    validate: function(frm) {
        let limit = flt(frm.doc.petty_cash_limit);
        let total = flt(frm.doc.total_expenses);

        // Check that every expense has a positive amount
        (frm.doc.expenses || []).forEach(function(row) {
            if (flt(row.amount) <= 0) {
                frappe.throw(
                    __('Expense row {0}: Amount must be greater than 0.', [row.idx])
                );
            }
        });

        // Check that total expenses do not exceed the petty cash limit
        if (total > limit) {
            frappe.throw(
                __('Total Expenses cannot exceed the Petty Cash Limit.')
            );
        }
    }
});

frappe.ui.form.on('Petty Cash Expense', {
    amount: function(frm) {
        calculate_totals(frm);
    }
});

function load_petty_cash_configuration(frm) {
    if (!frm.doc.center_officer) {
        return;
    }

    frappe.db.get_list('Petty Cash Configuration', {
        filters: {
            center_officer: frm.doc.center_officer
        },
        fields: [
            'cost_center',
            'petty_cash_account',
            'petty_cash_limit'
        ],
        limit: 1
    }).then(function(records) {
        if (records.length === 0) {
            frappe.msgprint(
                __('No Petty Cash Configuration was found for this Center Officer.')
            );
            return;
        }

        let config = records[0];

        frm.set_value('cost_center', config.cost_center);
        frm.set_value('petty_cash_account', config.petty_cash_account);
        frm.set_value('petty_cash_limit', config.petty_cash_limit);

        calculate_totals(frm);
    });
}

function calculate_totals(frm) {
    let total = 0;

    (frm.doc.expenses || []).forEach(function(row) {
        total += flt(row.amount);
    });

    frm.set_value('total_expenses', total);

    let limit = flt(frm.doc.petty_cash_limit);
    frm.set_value('remaining_balance', limit - total);
}
