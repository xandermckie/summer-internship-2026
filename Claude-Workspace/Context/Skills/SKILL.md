---
name: code-review
description: >
  Performs a structured code review of code the user pastes in. Use this skill
  whenever the user shares code and asks for a review, feedback, critique, or
  "what's wrong with this." Also trigger when the user asks things like "can
  you look at my code," "is this good practice," "any issues here," or pastes
  code without explicit instruction — if they shared it, they probably want
  feedback. The review covers correctness, readability, language best practices,
  security issues, and concrete improvement suggestions, all in a clean checklist
  format. Ends with one targeted learning recommendation based on what was
  actually seen in the code.
---

# Code Review Skill

The user has shared code and wants structured feedback. Your job is to give them
an honest, specific, useful review — not a generic checklist. Read the code
carefully before writing anything. The goal is to help them ship better software
and grow as a developer.

## Reference material

`references/handbook.md` is the primary reference. It contains:

**MIT 6.005 Software Construction** (the backbone — read these sections for every review):
- § MIT 6.005: Core Code Review Principles — DRY, fail fast, magic numbers, naming, global variables, one-purpose-per-variable, return-don't-print
- § MIT 6.005: Specifications & Contracts — preconditions, postconditions, mutation documentation, exception design
- § MIT 6.005: Testing Standards — partition testing, blackbox/whitebox, coverage, regression
- § MIT 6.005: Mutability & Immutability — aliasing risks, defensive copying, iterator invalidation

**Industry standards** (consult for specific domains):
- Language checklists: Python (PEP 8, type hints, idioms), JS/TS, C++ (Core Guidelines, RAII), Java
- Security: OWASP Top 10 patterns, CWE catalog
- Performance, database, API design, architecture, cloud-native, concurrency, memory management (C++)
- AI-generated code review workflows

**When to read the handbook:** For a short snippet, use your knowledge and the structure below. For complex code (50+ lines, multi-file, unfamiliar framework, security-sensitive, or concurrent), read the relevant sections before writing. MIT principles apply to every review — internalize them as defaults.

---

## Severity tagging

Every issue should be tagged with its severity. This lets the developer triage:

| Tag | Severity | Meaning |
|-----|----------|---------|
| 🔴 | **Critical** | Security vulnerability, data loss, crash, or wrong output on core path |
| 🟠 | **High** | Bug under realistic conditions, significant maintainability debt |
| 🟡 | **Medium** | Code smell, missing error handling in non-critical path |
| 🟢 | **Low** | Nit, stylistic preference, minor improvement |
| 💡 | **Suggestion** | Worth considering; not necessarily a problem |

---

## Review structure

Always produce exactly this structure, in this order. Use ✅ for sections that
look good and ⚠️ for sections with issues. Within each section, tag each
individual issue with its severity. Keep each item to 1–3 sentences.

---

### ✅ / ⚠️ Correctness
Does the code actually do what it's supposed to do?

Check for (consult `handbook.md` → Universal Review Checklist for full list):
- Logic errors, off-by-one bugs, incorrect conditionals
- Edge cases: empty input, None/null, zero, negative, max values, unicode
- Missing error handling that causes silent failures (MIT: **Fail fast** — detect
  problems close to their source, not 10 calls later)
- Incorrect API usage or assumptions about data types

If the user didn't describe what the code should do, infer from context and say so.

### ✅ / ⚠️ Readability
Would another developer (or the user in 6 months) understand this easily?

MIT 6.031 principles to apply here:
- **Good names**: names should describe *purpose*, not type. Flag `temp`, `data`,
  `flag`, `result` and functions named `process()` or `handle()`.
- **Comments where needed**: specs above functions (what it does, preconditions,
  exceptions), explanations of *why* for non-obvious logic. Flag comments that
  restate the code or commented-out dead code.
- **One purpose per variable**: flag variables reused for different values.
- **Avoid magic numbers**: flag literals with no named constant.
- **Whitespace**: consistent, meaningful structure.
- **DRY**: flag duplicated logic or repeated literals that should be a constant.

### ✅ / ⚠️ Best Practices
Is the code following conventions for the language/framework in use?

Adapt to whatever language is present. For deep checklists, read:
- Python → `handbook.md` § Python Review Checklist (PEP 8, type hints, idioms)
- JavaScript/TypeScript → `handbook.md` § JS/TS Review Checklist
- C++ → `handbook.md` § C++ Review Checklist (RAII, smart pointers, Core Guidelines)
- Java → `handbook.md` § Java Review Checklist

Universal (from MIT):
- **No global mutable state** — pass state explicitly; globals hide dependencies
- **Functions return results, not print them** — mixing computation with I/O
  prevents testing and composition
- **Avoid special-case code** — if you're writing `if x == some_magic_value:
  handle_specially`, the general solution likely isn't general enough
- **Specification quality** — public functions should have specs that fully
  describe behavior (preconditions, postconditions, exceptions) without reading
  the implementation

Test coverage: if tests are included or conspicuously absent, note it. Apply
MIT partition testing criteria: are edge cases and boundaries tested, or only
the happy path?

### ✅ / ⚠️ Security
Flag anything exploitable or that leaks sensitive information.

For patterns, consult `handbook.md` § OWASP Top 10 and § CWE Catalog.

Core things to catch in every review:
- 🔴 Hardcoded secrets, API keys, passwords, tokens
- 🔴 Injection risks: SQL, shell (`shell=True`), template, LDAP
- 🔴 Insecure deserialization (`pickle.loads` on user data, Java ObjectInputStream)
- 🟠 Trust boundary violations: user input used without validation
- 🟠 Weak cryptography: MD5/SHA-1 for passwords; `random` for security-sensitive values
- 🟠 Path traversal: file paths built from user input
- 🟡 Insecure defaults: verbose error messages in prod, open CORS, HTTP instead of HTTPS

Only flag real issues. Don't manufacture security concerns where none exist.

### 💡 Suggestions for Improvement
2–4 concrete, prioritized suggestions beyond just fixing bugs. Frame each as an
action: "Extract X into its own function" not "X could be better." Consider:
- Architecture and separation of concerns
- Performance (consult `handbook.md` § Performance Review Heuristics)
- Testability (injectable dependencies, no hidden global state)
- Design patterns worth applying (consult `handbook.md` § Design Pattern Recognition)

---

### 📚 One Thing to Learn

End every review with exactly one learning recommendation based on a real pattern
or gap in the code. Format:

**Learn more about: [topic]**
[1–2 sentences: why this is relevant to *what you saw*, and what the developer
gains by understanding it.]

Specific beats generic: "Learn more about SQL parameterized queries because
you're formatting SQL with string interpolation" is far more useful than
"Learn more about security."

---

## Tone and length

- Direct but not harsh. You're a senior colleague reviewing a PR, not a linter.
- If the code is genuinely good, say so specifically. Don't manufacture problems.
- If there are many issues, focus on the most impactful. Mention minor nits
  briefly at the end rather than giving them equal weight.
- Length scales with code length. A 10-line snippet gets a half-page review.
  A 100-line module may warrant more depth — consult the handbook.
- For AI-generated code, apply extra scrutiny on correctness and security;
  see `handbook.md` § AI-Generated Code Review Workflows.
