---
id: 20261115-1651-ctrl-shift-reaches-nvim-as-c-map-that-not-c-s
title: Ctrl+Shift+` reaches nvim as <C-^>; map that, not <C-S-`>
kind: lesson
topics: [neovim, terminal, keymaps]
projects: [dotfiles]
origin: opencode session: nvim VSCode-style terminal keymaps
posted: 2026-11-15T16:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Terminals send control+shift+backtick as 0x1E (ctrl+^) because shift turns ` into ~
and ctrl subtracts 0x40 — there is no distinct <C-S-`> key in legacy encoding.
Only terminals with the kitty keyboard protocol (ghostty) can deliver it separately.
When a user wants a ctrl+shift+<key> binding in nvim, compute the legacy fallback
(ctrl + shifted_key) and map that. Same for <C-S-2>/<C-S-3> variants.
Reference: ~/.config/nvim/lua/config/keymaps.lua, dotfiles commit 240127b.
