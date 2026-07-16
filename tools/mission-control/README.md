# Mission Control

> **In plain terms:** If you run more than a couple of coding-agent sessions at once, you end up tabbing between terminals just to see who is working and who has stalled. Mission Control is one local web page that shows every Claude Code session on your machine, live: which project each belongs to, whether it is working right now, what it last said, and the role you gave it. One glance instead of ten windows.

A zero-dependency Python script (3.10+, stdlib only). It reads the session transcripts Claude Code already writes under `~/.claude/projects` (each session continuously appends a `.jsonl` file), so "active right now" simply means the file was written seconds ago. Read-only on the transcripts; the only thing it ever writes is its own config file.

## Run

```
python mission_control.py
```

Open http://localhost:3131. It refreshes every 4 seconds.

## What you get

- **Board view.** Each project is a card, sorted by most recent activity; live projects get an accent edge. Each session shows a status dot (pulsing = actively writing, amber = idle, gray = asleep), a role label, the short session id, timing, and a two-line snippet of the last thing that session said.
- **Office view.** The ambient version: each session is a small figure at a desk. The monitor glows and the figure types when the session is working. Hover a desk for the snippet. Same data, different mood.
- **Click-to-label roles.** Click any session name and assign it a role from that project's vocabulary (configurable), or a custom one. Labels persist in `mission_control.config.json`, which is auto-created next to the script and re-read live, so edits apply without a restart.

## Config

`mission_control.config.json`:

- `names`: project folder slug to display name (`"D--my-repo": "My App"`).
- `labels`: first 8 characters of a session id to a role label. Session ids persist across `claude --resume`, so labels are more durable than you might expect.
- `roles`: per-project role vocabulary for the click-to-label menu, plus a `_default` list.
- `hide`: project slugs to keep off the board.

## Honest limitations

- "Working" means the transcript is being written right now. A session that is paused waiting for your input shows as idle, which is technically true but worth knowing.
- It observes sessions; it does not manage them. Launching, resuming, and stopping stay in your terminals.

To auto-start it, register the run command with your OS startup mechanism (a `shell:startup` shortcut or a service wrapper on Windows).
