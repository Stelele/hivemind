---
id: 20261115-2142-kitty-protocol-terminals-konsole-send-ctrl-shift
title: Kitty-protocol terminals (Konsole) send Ctrl+Shift+` as a distinct <C-S-`> key — map BOTH it and <C-^>
kind: lesson
topics: [neovim, terminal, keymaps, konsole]
projects: [dotfiles]
origin: opencode session: nvim VSCode-style terminal keymaps
posted: 2026-11-15T21:42+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
CORRECTS 20261115-1651-ctrl-shift-reaches-nvim-as-c-map-that-not-c-s — that advice
is only true for legacy-encoding terminals.

Konsole 26.08 (and ghostty, wezterm) implement the kitty keyboard protocol. Once
nvim enables it, ctrl+shift+grave arrives as CSI-u (ESC[96;6u / ESC[96:96;6u)
which nvim decodes as a distinct <C-S-`> key. Two verified facts from a pty
harness with vim.on_key + behavior probes:
1. nvim decodes CSI-u key sequences EVEN IF the kitty protocol handshake never
   completed, so mapping <C-S-`> works regardless of what the multiplexer
   (herdr) passes through.
2. legacy ctrl+shift+` is 0x1e = <C-^>; legacy ctrl+` is 0x00 which nvim decodes
   as <C-Space> in legacy mode but <C-`> in kitty mode (CSI 96;5u).
Therefore: map <C-^> AND <C-S-`> to the same action to cover every terminal.
Reference: ~/.config/nvim/lua/config/keymaps.lua, dotfiles commit 5438b60.
