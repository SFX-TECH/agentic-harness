# The Quality Gauge

> How to know whether agent-built software is any good, instead of arguing about it.

> **In plain terms:** Everything else in this harness is about *producing* software with coding agents. None of it tells you whether what came out is any good. This page is five cheap measurements that put a number on it, what each one answers, and the real numbers they returned on a shipping product. Old, boring, free tools. What is new is pointing them at agent-written code and publishing the result.

---

## Why this pillar exists

"Is AI-written code any good" is currently an argument, not a measurement. People trade anecdotes. Someone says agents write duplicated slop, someone else says their agents ship fine, and nobody puts a number on the table.

You can just measure it.

**The principle: prefer a measurement that produces a number over another agent that produces an opinion.**

Reviewers are useful and you should have them. But reviewers cost tokens, generate false positives (the best published study of multi-agent code review found roughly a 50% false-positive rate), and produce judgments you then have to judge. A duplication percentage is not an opinion. Neither is a mutation score. Numbers can be tracked over time, compared against public baselines, and handed to a skeptic.

Everything below was run against a production codebase: a Windows repair app, roughly 900 files, 11,078 tests, 147 repair modules, weekly releases, real users. The numbers are the ones it actually returned, including the one that came back badly.

---

## 1. Duplication: "agents copy instead of abstracting"

> **In plain terms:** Does the code repeat itself instead of building reusable pieces? This is the most common criticism of AI-written code, and it takes one command to answer.

**The critique, stated fairly.** The most-cited study of AI-era code quality analyzed 211 million lines and found copy-pasted lines rising from 8.3% to 12.3% between 2020 and 2024, while refactored code fell from 25% of changes to under 10%. The claim is that a model reaches for a nearby example instead of building the right abstraction.

**Measure it.** `jscpd` across your source directories, minimum clone length 12 lines. Runs through `npx`, installs nothing.

**What it returned.** **1.46%.** Seventy-eight clones, 1,331 duplicated lines across 198 files.

Roughly one eighth of the published ecosystem average, and that average includes human-written code. The most concrete criticism of agent-written code turned out to be answerable with one number.

---

## 2. Static security analysis: "agents write insecure code"

> **In plain terms:** Automated scanners read your code looking for known-dangerous patterns. They find a lot of noise. The skill is sorting the four real problems out of five hundred warnings.

**The critique, stated fairly.** This one has the strongest evidence behind it. Controlled testing across 100+ models and 80 tasks found AI introducing a vulnerability roughly **45% of the time**, with security not improving even as functional correctness did. Real-world failures cluster hard in access control: leaked user data, deleted production databases, credentials exposed within days of launch.

**Measure it.** `bandit` for Python, `semgrep` for cross-language rulesets. Both read-only, both fast.

**What it returned, and the part that matters more than the number.** 515 findings. That number would stop most people cold, and it should not. 491 were low severity, and the four flagged as "hardcoded password" were variables named `token` in a parser for Microsoft knowledge-base articles.

**The real result was four.** Four uses of `tempfile.mktemp()`, a function that hands back a predictable filename *without creating the file*, leaving a window where an attacker pre-creates that path as a symbolic link and redirects the write somewhere privileged. The worst instance sat in the undo engine, feeding an elevated PowerShell redirect: a privileged write to an attacker-choosable path, inside the feature the product's entire safety story rests on.

An afternoon of read-only scanning found a privilege-escalation-class bug that fourteen review agents and eleven thousand tests had not.

**The transferable part is the triage, not the tool.** Raw scanner output is mostly noise, and a harness that says "run bandit" has not helped you. Sort by severity *and* confidence. Classify your accepted patterns once, with a written reason, so they stop generating debate: a repair tool runs subprocess on purpose, and those warnings are expected forever. Then hunt specifically for the classes that matter in your domain. Publish the triaged number, never the raw one.

---

## 3. Mutation testing: "your tests are theater"

> **In plain terms:** Break the code on purpose, then see whether your tests notice. If you break something and every test still passes, that test suite was decorating, not checking. This is the sharpest criticism of agent-built software, because it attacks the thing you were relying on for safety.

**The critique, stated fairly.** Agents write tests. Agents write tests for code agents wrote. A test that mirrors the implementation passes forever and proves nothing. Test *count* is not test *quality*, and a large suite can be a comfort blanket.

**Measure it.** Mutation testing injects small bugs and checks whether the suite notices. A surviving mutant is unasserted behavior. Practical note: the standard Python tool `mutmut` has no native Windows support, and `mutatest`'s entry point was broken in our environment. Do not let a tooling gap stop you, because of what comes next.

**The variant worth stealing.** Rather than random operator mutation across a whole module, hand-pick mutations that each break **one invariant you actually care about**, apply them one at a time, and revert. Random mutation asks "do the tests notice arbitrary edits." Targeted mutation asks "do the tests defend the things that would hurt me." For security-critical code the second question is the one worth answering, and a thirty-line script does it in an afternoon.

**What it returned.** Five mutations, each breaking a security invariant that a long adversarial review had already been fought over. **Three caught, two survived.** Line coverage on that module: 84%.

The two survivors were **the same blind spot**, and that is the finding:

- The elevation check failing *open*. The code says "if we cannot determine whether we are running with administrator rights, assume we are, and refuse to load." Flip that to assume-we-are-not, and every test still passed.
- A trust manifest with no hashes being accepted. The code says "never trust a user-writable directory without pinned file hashes." Remove that check, and every test still passed.

The suite proved *"an attack is refused."* It did not prove *"when we cannot tell, we refuse anyway."*

**The rule that came out of it, and this is the most valuable thing on this page.** An agent writing tests naturally covers the branches it just wrote, because each one has a feature story to tell. It under-covers the **default taken when a check itself fails**, because that path has no story. So:

> For every fail-safe default in security-critical code, write the test that forces the *check* to fail, not just the condition the check is looking for.

That rule is not obvious, is in no style guide, and came out of measurement rather than opinion. It is exactly the kind of thing this pillar exists to surface.

---

## 4. Coverage: "you do not know what your tests touch"

> **In plain terms:** Coverage tells you which lines ran during your tests. It does not tell you whether anything was actually checked, which is why it belongs next to mutation testing rather than instead of it.

Coverage is the weakest of the five as a quality signal and still worth having, because it is the cheapest way to find blind spots.

**Measure it.** `pytest-cov`, one flag.

**What it returned.** 84% on the security-critical module. Most useful as context for the mutation result above: **high coverage with surviving mutants is the precise signature of tests that execute code without asserting its behavior.** Neither number means much alone. Together they are diagnostic.

---

## 5. Complexity: "nobody can read this, including you"

> **In plain terms:** A score for how tangled each function is. High scores are not automatically bugs, but they tell you exactly which parts of your own codebase you no longer understand, which is where to send a human.

**The critique, stated fairly.** The honest concern about agent-native development is not that the code is wrong. It is **understanding debt**: the author cannot read their own codebase, so when the agents cannot fix something, nobody can. The bus factor is zero.

**Measure it.** `radon cc` for cyclomatic complexity, whose scale tops out at F for anything above 41.

**What it returned.** The top functions scored 249, 209, and 105.

**How to read that honestly.** A dispatcher over 147 repair modules is going to branch a lot, and high complexity there is not automatically a defect. But 249 independent paths means full-path testing is impossible and no human holds all of it in their head.

The useful conclusion is not "refactor these." It is that complexity ranking hands you a **prioritized map of where your understanding debt actually lives**, which is precisely where to point a human reviewer and precisely where to be most suspicious of a confident agent.

---

## What this pillar is not

**Not a substitute for a human security review.** Scanners find known patterns. A person doing a threat model finds the thing nobody wrote a rule for. If your software runs with privilege, touches user data, or handles money, buy one human review pass before a trust milestone. Every gauge here raises the floor. None raises the ceiling.

**Not proof that agent-built code is fine.** The measurement that most directly tested the defense came back at three out of five. That is a good result against the published evidence, and it is also a real gap that measurement found and opinion would not have.

**Not a gate on day one.** Measure first, threshold later. A gate imposed before you know your own baseline is a number someone will game or skip.

---

## Wiring it in

Sequenced by value per minute of runtime:

| Gauge | Cost | Where it belongs |
|---|---|---|
| Duplication | seconds | every commit, or a weekly trend line |
| Static security | about a minute | pre-commit gate, after a one-time triage of accepted patterns |
| Coverage | one test run | inside the existing test gate, reported not enforced |
| Complexity | seconds | a weekly report, used to route human attention |
| Mutation | minutes to hours | tag time, scoped to changed security-critical modules only |

The rule governing all of them, and it is [Principle 3](PRINCIPLES.md) applied to quality: **a check that runs beats a habit that does not.** Anything depending on a person remembering to invoke it will drift, and you will find out at the worst moment. Put each gauge inside something that already runs.

The corollary, learned the hard way: **automation that was designed but never registered is not automation.** Confirm your hooks actually fire and your scheduled jobs actually exist. A documented intention and a running job look identical in a README and nothing alike in reality.

---

## Publish your numbers

The debate about agent-written code is conducted almost entirely in anecdotes, and the loudest anecdotes involve people who shipped unreviewed prototypes and got breached. That is a real failure mode. It is not the only one available.

If you build this way, measure your own code and publish the numbers with the method attached. One measured duplication percentage does more than any amount of arguing, and a number that comes back badly has handed you something specific and fixable instead of a vague worry.

The point of a harness is not to prove agents write perfect code. It is to make the quality of what they write **visible, measurable, and improvable**, which is what engineering has always been.
