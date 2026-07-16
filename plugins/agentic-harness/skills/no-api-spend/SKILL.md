---
name: no-api-spend
description: A hard cost guardrail. The agent must never write or run code that calls a paid model or API (Anthropic, OpenAI, Google, embeddings, vision, TTS, any metered endpoint) without first stating the planned call volume, the estimated cost, and getting an explicit approval. Applies to scripts, subagents, batch jobs, and third-party packages that call out on your key. Use in every project where an API key is present in the environment.
---

An agent that can write code can write code that spends money. This skill makes that impossible to do silently.

## The rule

Before any code you write or run makes a metered API call, stop and get approval with this exact shape:

> Stopping. Skill no-api-spend blocks this. Planned: `<model or API>` on `<N>` items at roughly `<tokens or units>` each, estimated cost about $`<X>`. Approve, or pick a non-API path.

No approval, no call. "The user probably wants it" is not approval. A prior approval covers that run only, not the next one.

## Where the money leaks (check all of these)

1. **Scripts you author.** Never instantiate a paid SDK in a throwaway script without the quote-and-approve step, even for "just a quick test." Loops multiply: a quick test over a directory is a batch job.
2. **Batch and vision work is the dangerous edge.** Per-item costs that look tiny multiply by item count, and image/vision tokens dwarf text. Estimate the whole batch before item one.
3. **Subagents and tools.** Work you delegate inherits this rule. A subagent prompt that says "summarize each file with the API" is a spend decision you just made.
4. **Third-party packages.** Some libraries call hosted models by default with whatever key is in the environment. Before adding a dependency that touches AI, find out what it calls and with whose key.
5. **Retries and watchers.** Anything that runs on a loop or a schedule needs a cap (max calls, max cost) in the code itself, not in your intentions.

## Cheaper paths to offer first

When you hit the block, propose the non-API alternative in the same breath: a local model if one is available, a heuristic or regex for the simple version of the task, a sample run (10 items, not 10,000) to validate before the full batch, or doing the reasoning yourself in-session where the cost is already accounted for.

## The estimate discipline

An estimate must be a number, not a shrug: items times average input/output units times the current price. If you do not know the price, finding it is part of the approval, not something to skip. After an approved run, report actual usage against the estimate so the next estimate is better.
