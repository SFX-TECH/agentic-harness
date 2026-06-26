#!/usr/bin/env bash
# agentic-harness SessionStart hook.
# Surfaces the project's durable state at the start of a session so work never begins on stale ground:
# which memory-bank files exist, and the git freshness (branch, uncommitted count, ahead/behind upstream).
# Read-only. SessionStart hooks cannot block; if anything here fails, the session simply starts without this context.
set -u

PROJECT="${CLAUDE_PROJECT_DIR:-$PWD}"
out=""

# Memory bank presence
bank="$PROJECT/.claude/memory-bank"
if [ -d "$bank" ]; then
  files=""
  for f in decisions.md active-context.md progress.md; do
    [ -f "$bank/$f" ] && files="$files $f"
  done
  if [ -n "$files" ]; then
    out="${out}Memory bank present:${files}. Read active-context.md for the current state before non-trivial work."$'\n'
  else
    out="${out}Memory bank directory exists but is empty."$'\n'
  fi
else
  out="${out}No memory bank found. Run /harness-init to scaffold durable context for this project."$'\n'
fi

# Git freshness (guarded: harmless if git is absent or this is not a repo)
if command -v git >/dev/null 2>&1 && git -C "$PROJECT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git -C "$PROJECT" branch --show-current 2>/dev/null)"
  dirty="$(git -C "$PROJECT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  out="${out}Git: branch ${branch:-detached}, ${dirty} uncommitted file(s)."
  if git -C "$PROJECT" rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    ahead="$(git -C "$PROJECT" rev-list --count '@{u}..HEAD' 2>/dev/null)"
    behind="$(git -C "$PROJECT" rev-list --count 'HEAD..@{u}' 2>/dev/null)"
    out="${out} ${ahead:-0} ahead, ${behind:-0} behind upstream."
    if [ "${behind:-0}" != "0" ]; then
      out="${out} Pull or verify against the remote before relying on local state."
    fi
  fi
fi

printf '%s\n' "$out"
