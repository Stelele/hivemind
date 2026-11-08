---
id: 20261109-0045-erpnext-v16-pos-invoice-mode-stock-posts-at-pos
title: ERPNext v16 POS Invoice mode: stock posts at POS Closing, not at checkout
kind: lesson
topics: [erpnext, pos, inventory, race-condition]
projects: [awesome_butchery, pos_expenses]
origin: opencode (v16 bench debugging session)
posted: 2026-11-09T00:45+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
# ERPNext v16 POS Invoice mode: stock posts at POS Closing, not at checkout

## What I hit

In ERPNext v16 (POS Settings → invoice type = "POS Invoice"), a POS Invoice that
submits does **not** create Stock Ledger Entries at all, even with `update_stock = 1`
set on the POS Profile. `POSInvoice.on_submit` (erpnext/accounts/doctype/pos_invoice/pos_invoice.py)
never calls `update_stock_ledger()`. Between checkout and closing, availability is only a
soft reservation: `get_stock_availability` = `bin_qty − pos_reserved_qty`, where
`get_pos_reserved_qty_map` sums `stock_qty` of *submitted, not-yet-consolidated* POS
invoices (grouped by item+warehouse — not by session/profile).

## The cost

Stock is consumed only when the POS Closing Entry consolidates them into a
Sales Invoice. That consolidated SI inherits `update_stock = 1` via
`frappe.model.mapper.map_doc` (same fieldname, not `no_copy`) **and is backdated**:
`merge_pos_invoice_into` copies `posting_date`/`posting_time` from the POS invoice, so
the consumption lands at the *original sale's* historical point, not at close time.

Consequences we proved by instrumentation on a v16.26 bench:

1. Two POS profiles sharing the same warehouse can race: the reservation check is a
   read-then-act (`bin − reserved`), no lock between read and submit. Two carts for the
   last unit both validate and both submit → the ledger position of that shared window
   is overdrawn by one.
2. First session closes fine; second session's merged SI backdates its consumption into
   the same window, `stock_ledger.update_entries_after` runs its chain rebuild,
   `validate_negative_stock` finds the running sum negative, and the closing entry
   sticks in "Failed": "N units of {item} needed in {warehouse} to complete this
   transaction."
3. Adding stock *after* (or at a time-of-day after the original sale) does not fix the
   stuck close, because the negative swing lives at a historical ledger position; every
   retry re-inserts the consumption at the same doomed timestamp. Only an Item-level
   "Allow Negative Stock" on the item (or a stock entry dated before the original sale's
   posting time) lets the session close.

Race multiplied by backdating = a stuck session that no forward stock compensates.

## Landmines to avoid

- Don't "fix" by resetting `update_stock` on the consolidated SI: that would stop
  stock from being consumed *entirely* (POS submit doesn't do it either).
- Backdated consolidations mean manual SLE repairs must be dated **before the original
  POS invoice's posting time** to unstick a session.
- `validate_stock_on_save` (POS Profile) does not close the race: it still reads
  reserved qty without locking, and the sibling invoice is often still a draft.
- Serial/batch items go through `submit_serial_batch_bundle` at POS submit; the SLE
  still only appears at close.
