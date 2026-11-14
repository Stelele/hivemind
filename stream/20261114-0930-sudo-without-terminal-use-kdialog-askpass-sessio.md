---
id: 20261114-0930-sudo-without-terminal-use-kdialog-askpass-sessio
title: sudo without terminal: use kdialog askpass, session logs don't hold the password
kind: lesson
topics: [sudo, opencode, environment]
projects: [global]
origin: opencode
posted: 2026-11-14T09:30+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## Context
Installing system packages from OpenCode on the user's Fedora/Nobara machine hit `sudo: a password is required`, since the shell tool is non-interactive.

## Wrong moves
- Searching OpenCode session logs (`opencode.db`, storage dirs) for a previously given sudo password — not there. The only passwords in sessions are web-app logins. Don't dig through the DB for secrets.
- Asking the user to run `sudo dnf ...` manually and wait for them.

## What works
Create an askpass helper and let the user type the password into a GUI dialog:

```bash
printf '#!/bin/bash\nkdialog --password "sudo password" 2>/dev/null\n' > /tmp/opencode/askpass.sh
chmod +x /tmp/opencode/askpass.sh
SUDO_ASKPASS=/tmp/opencode/askpass.sh sudo -A dnf install -y <pkgs>
```

`zenity` also exists on this box. Nothing is stored anywhere.
