---
name: harness-init
description: Scaffold the agentic harness into the current project, a CLAUDE.md session bootstrap plus a memory bank (decisions, active context, progress). Run once per project to give every future Claude Code session durable context.
disable-model-invocation: true
argument-hint: "[--force]"
---

Initialize the agentic harness in the current project. The user invoked this deliberately; scaffold the files, do not improvise extra structure.

The template files live in this skill's own directory at `${CLAUDE_SKILL_DIR}/templates/`. Use absolute paths from that variable so it works regardless of the current working directory.

## Steps

1. Check whether `${CLAUDE_PROJECT_DIR}/CLAUDE.md` already exists. If it does and the user did not pass `--force` (check $ARGUMENTS), stop and report what is already there, so nothing is overwritten by accident.

2. Copy the bootstrap: read `${CLAUDE_SKILL_DIR}/templates/CLAUDE.md` and write it to `${CLAUDE_PROJECT_DIR}/CLAUDE.md`.

3. Create the memory bank directory `${CLAUDE_PROJECT_DIR}/.claude/memory-bank/` and copy every file from `${CLAUDE_SKILL_DIR}/templates/memory-bank/` into it: decisions.md, active-context.md, progress.md.

4. Report the files created, then tell the user the next step in one line: open CLAUDE.md and fill in the real stack, locked decisions, and current state, then keep the memory bank updated as a habit.

Read the template files before writing them so you copy their real contents verbatim. Do not paraphrase or summarize the templates; they are the harness, copied for the user to fill in.
