# Code Review Handbook
## A Reviewer's Reference — MIT 6.005 + Industry Standards

**Core framework (MIT 6.005 Software Construction):**
Every piece of code should be evaluated against three goals:
- **Safe from bugs** — correct today and correct in the unknown future
- **Easy to understand** — communicating clearly with future programmers, including future you
- **Ready for change** — designed to accommodate change without rewriting

These three goals are the backbone of this handbook. Every section maps back to them.

---

## Table of Contents

1. [Severity Rubric](#severity-rubric)
2. [MIT 6.005: Core Code Review Principles](#mit-6005-core-code-review-principles)
3. [MIT 6.005: Specifications & Contracts](#mit-6005-specifications--contracts)
4. [MIT 6.005: Testing Standards](#mit-6005-testing-standards)
5. [MIT 6.005: Mutability & Immutability](#mit-6005-mutability--immutability)
6. [Universal Review Checklist](#universal-review-checklist)
7. [Python Review Checklist](#python-review-checklist)
8. [JavaScript / TypeScript Review Checklist](#javascript--typescript-review-checklist)
9. [C++ Review Checklist](#c-review-checklist)
10. [Java Review Checklist](#java-review-checklist)
11. [Security: OWASP Top 10 Patterns](#security-owasp-top-10-patterns)
12. [Security: CWE Pattern Catalog](#security-cwe-pattern-catalog)
13. [Performance Review Heuristics](#performance-review-heuristics)
14. [Design Pattern Recognition](#design-pattern-recognition)
15. [Anti-Pattern Catalog](#anti-pattern-catalog)
16. [Concurrency & Threading Review](#concurrency--threading-review)
17. [Memory Management Review (C/C++)](#memory-management-review-cc)
18. [API Design Standards](#api-design-standards)
19. [Database Review Standards](#database-review-standards)
20. [Architecture Review Guidance](#architecture-review-guidance)
21. [Cloud-Native & Microservices Standards](#cloud-native--microservices-standards)
22. [AI-Generated Code Review Workflows](#ai-generated-code-review-workflows)
23. [Senior/Staff-Level Engineering Expectations](#seniorstaff-level-engineering-expectations)

---

## Severity Rubric

| Severity | Label | Meaning | Must fix before merge? |
|----------|-------|---------|------------------------|
| 🔴 | **Critical** | Security vulnerability, data loss, crash, correctness failure in core path | Yes |
| 🟠 | **High** | Performance issue under realistic load, hidden bug, significant maintainability debt | Usually |
| 🟡 | **Medium** | Code smell, style violation, missing error handling in non-critical path | Recommended |
| 🟢 | **Low** | Nit, stylistic preference, minor improvement | Optional |
| 💡 | **Suggestion** | Worth considering, not necessarily a problem | Developer's call |

**Calibration:** A typical non-trivial PR has 0–2 Critical/High, 3–8 Medium, and several Low/Suggestion. If everything is Critical, you're over-indexing. If nothing is above Low, look harder.

---

## MIT 6.005: Core Code Review Principles

*Source: MIT 6.005 Software Construction, Reading 4 (Robert Miller, Max Goldman)*
*License: CC BY-SA 4.0 — https://web.mit.edu/6.005/www/fa16/classes/04-code-review/*

These nine principles come directly from MIT's Software Construction course. Each one maps to safety, clarity, or changeability.

### 1. Don't Repeat Yourself (DRY)

Duplicated code is a bug risk. When logic exists in two places, a fix in one may not reach the other.

> "Copy-and-paste is an enormously tempting programming tool, and you should feel a frisson of danger run down your spine every time you use it." — MIT 6.005

**What to look for:** same logic in multiple methods, same constant written multiple times, copy-paste tests.

**Maps to:** *Safe from bugs* (one fix point), *Ready for change* (one change point)

### 2. Comments Where Needed

Comments explain **why**, not **what**. The code already shows what it does.

**Useful:** specs above methods, preconditions, source attribution, non-obvious decisions
**Useless — flag these:**
```java
while (n != 1) { // test whether n is 1
    ++i;          // increment i
}
```
**Maps to:** *Easy to understand*, *Safe from bugs* (documented assumptions)

### 3. Fail Fast

Code should reveal bugs as early as possible. Static errors beat runtime errors beat silent wrong answers.

> "Static checking fails faster than dynamic checking, and dynamic checking fails faster than producing a wrong answer that may corrupt subsequent computation." — MIT 6.005

```java
// BAD: wrong arg order silently produces wrong answer
dayOfYear(9, 2, 2019)

// GOOD: wrong arg order is a compile error
dayOfYear(Month.FEBRUARY, 9, 2019)

// BAD: returns -1 and hides the problem
if (month < 1 || month > 12) return -1;

// GOOD: throws immediately, exposing the bug
if (month < 1 || month > 12) throw new IllegalArgumentException("month out of range: " + month);
```

**Maps to:** *Safe from bugs* (earlier detection = easier fix)

### 4. Avoid Magic Numbers

Every constant that isn't 0, 1, or 2 is a magic number. Name it.

> "Don't hardcode constants that you've computed by hand." — MIT 6.005

```java
// BAD
if (response_code == 429) time.sleep(60);

// GOOD
final int HTTP_TOO_MANY_REQUESTS = 429;
final int RATE_LIMIT_BACKOFF_SECONDS = 60;
if (response_code == HTTP_TOO_MANY_REQUESTS) time.sleep(RATE_LIMIT_BACKOFF_SECONDS);
```

Also flag **hand-computed constants**: `59` is worse than `31 + 28`, which is worse than `DAYS_IN_JANUARY + DAYS_IN_FEBRUARY`.

**Maps to:** *Easy to understand*, *Ready for change*

### 5. One Purpose For Each Variable

Don't reuse a variable for two different meanings — including method parameters.

```java
// BAD: dayOfMonth is repurposed mid-function
public static int dayOfYear(int month, int dayOfMonth, int year) {
    if (month == 2) dayOfMonth += 31; // now means something different
    return dayOfMonth;
}

// GOOD:
public static int dayOfYear(int month, int dayOfMonth, int year) {
    int dayOfYear = dayOfMonth;
    if (month == 2) dayOfYear += 31;
    return dayOfYear;
}
```

> "Method parameters should generally be left unmodified." — MIT 6.005

**Maps to:** *Easy to understand*, *Safe from bugs*

### 6. Use Good Names

Long and self-descriptive beats short and cryptic.

- **Bad:** `tmp`, `temp`, `data`, `x`, `val`, `flag`, `n`
- **Good:** `secondsPerDay`, `isLeapYear`, `remainingRetryCount`

> "Every local variable is temporary, and every variable is data, so those names are generally meaningless." — MIT 6.005

| Language | Functions | Variables | Classes | Constants |
|----------|-----------|-----------|---------|-----------|
| Python | `snake_case` | `snake_case` | `PascalCase` | `UPPER_CASE` |
| Java | `camelCase` | `camelCase` | `PascalCase` | `UPPER_CASE` |
| JS/TS | `camelCase` | `camelCase` | `PascalCase` | `UPPER_CASE` |

Methods: **verb phrases** (`getDate`, `isValid`). Variables/classes: **noun phrases** (`userList`, `ConnectionPool`).

### 7. Use Whitespace to Help the Reader

Consistent indentation, spaces around operators, blank lines between logical sections. Never tab characters (they render differently across tools).

### 8. Don't Use Global Variables

Global variables are mutable state accessible from anywhere. They make code hard to test and reason about.

In Java: `public static` non-final fields are global. In Python: module-level mutable variables used across functions.

**Exception:** Constants (`UPPER_CASE`, `static final`) are fine.

> "Change global variables into parameters and return values, or put them inside objects." — MIT 6.005

**Maps to:** *Safe from bugs* (hard to localize bugs), *Easy to understand* (must trace entire program)

### 9. Methods Should Return Results, Not Print Them

Functions that print output can't be composed, tested, or reused in other contexts.

```java
// BAD: output is lost; untestable
public static void countLongWords(List<String> words) {
    int n = 0;
    for (String word : words) if (word.length() > 5) ++n;
    System.out.println(n);
}

// GOOD:
public static int countLongWords(List<String> words) { ... return n; }
```

> "Only the highest-level parts of a program should interact with the console." — MIT 6.005

**Exception:** Logging is fine. Debug prints must be removed before merge.

---

## MIT 6.005: Specifications & Contracts

*Source: MIT 6.005, Readings 6 & 7 — https://web.mit.edu/6.005/www/fa16/classes/06-specifications/*

A specification is the contract between caller and implementer. Good specs make bugs impossible by clarifying what each party is responsible for.

> "Specifications are the linchpin of teamwork. It's impossible to delegate responsibility for implementing a method without a specification." — MIT 6.005

### Structure of a Complete Spec

```
requires:  (precondition)  what the caller must ensure before calling
effects:   (postcondition) what the function guarantees, including mutations and return value
```

```python
def find_first(lst: list, value: Any) -> int:
    """
    Find the first occurrence of value in lst.
    Requires: lst is not None
    Effects:  Returns index of first element equal to value,
              or -1 if not found. Does not modify lst.
    """
```

### Review Questions for Every Public Function

1. **Is a spec present?** No spec = no contract.
2. **Can another engineer use this function correctly from the spec alone**, without reading the implementation?
3. **Are preconditions documented?**
4. **Is every mutation documented?** Undocumented mutation is a hidden contract violation.
5. **Is the spec appropriately strong?** Too weak: almost any implementation satisfies it. Too strong: over-specifies implementation details, reducing freedom.
6. **Are exceptions documented** with the conditions that trigger each?

### Exception Design

- **Checked exceptions:** for expected failures callers must handle (file not found, network timeout)
- **Unchecked exceptions:** for programmer errors — violated preconditions (NullPointer, out-of-bounds)

```java
// BAD: swallowing exception
try { ... } catch (Exception e) { }

// BAD: exception as control flow
try { return items.get(index); }
catch (IndexOutOfBoundsException e) { return defaultValue; }
// GOOD:
return index < items.size() ? items.get(index) : defaultValue;

// BAD: losing original traceback
catch (Exception e) { throw new Exception("something went wrong"); }
// GOOD:
catch (DatabaseError e) { throw new ServiceUnavailableError("DB down") from e; }
```

---

## MIT 6.005: Testing Standards

*Source: MIT 6.005, Reading 3 — https://web.mit.edu/6.005/www/fa16/classes/03-testing/*

### Test-First Programming

Write tests **before** code:
1. Write a specification
2. Write tests that exercise the spec
3. Write the implementation to pass the tests

Writing tests first forces clarity about the spec and finds spec bugs early, before implementation anchors your thinking.

### Systematic Partition Testing

Don't test randomly. Partition the input space into subdomains of similar behavior and test each partition.

**Steps:**
1. Identify all input variables and their meaningful ranges
2. Divide each into subdomains
3. Always include boundaries
4. Choose one representative per partition cell, document which partition each test covers

**Boundary checklist — always include:**
- 0, 1, -1
- Empty collection, single-element collection
- First and last element
- Maximum and minimum numeric values
- `null`/`None`

**Example: `max(a: int, b: int) -> int`**
Partitions: `a < b`, `a = b`, `a > b`, `a = 0`, `a = MIN_INT`, `b = MAX_INT`

### Blackbox vs. Whitebox Testing

- **Blackbox:** tests from spec only. Survive refactoring.
- **Whitebox:** tests from implementation. Catch branch-specific bugs.

Flag: whitebox tests that assert implementation details not in the spec — they break on refactoring.

### Coverage Goals

| Type | Meaning | Target |
|------|---------|--------|
| Statement | Every line executed by some test | 100% reachable |
| Branch | Both branches of every if/while covered | Strongly desired |
| Path | Every combination of branches | Infeasible |

### Unit vs. Integration Tests

- **Unit tests:** one module, isolated. Bug localization is easy.
- **Integration tests:** multiple modules. Important but harder to debug.

**Flag:** unit tests that secretly call real DBs, real HTTP — those are integration tests in disguise. Use mocks/stubs.

### Regression Testing

Every bug fix should add a test that would have caught the bug. Run all tests on every commit.

**Flag:** bug fixes with no accompanying regression test.

---

## MIT 6.005: Mutability & Immutability

*Source: MIT 6.005, Reading 9 — https://web.mit.edu/6.005/www/fa16/classes/09-immutability/*

> "Immutable types are safer from bugs, easier to understand, and more ready for change." — MIT 6.005

### Aliasing Makes Mutation Dangerous

Two references to the same mutable object mean mutation through one affects the other — often surprising the other's owner.

```python
# BAD: sumAbsolute mutates the caller's list
def sum_absolute(lst):
    for i in range(len(lst)):
        lst[i] = abs(lst[i])  # modifies caller's data!
    return sum(lst)

my_data = [-5, -3, -2]
print(sum_absolute(my_data))  # 10
print(sum(my_data))            # also 10 — caller expected -10!
```

**MIT's rule:** if a function mutates its input, the spec must say so explicitly.

### Returning Mutable Objects From Caches

```java
// BAD: returning reference to cached mutable object
private static Date cachedAnswer = null;
public static Date startOfSpring() {
    if (cachedAnswer == null) cachedAnswer = compute();
    return cachedAnswer; // caller can mutate your cache!
}

// GOOD: defensive copy
return new Date(cachedAnswer.getTime());

// BEST: use an immutable type
public static LocalDate startOfSpring() { ... } // LocalDate is immutable, no copy needed
```

### Mutability Review Checklist

- [ ] Does any method mutate inputs the spec doesn't document as being mutated?
- [ ] Is a mutable object returned from a function that caches it? (aliasing risk)
- [ ] Are mutable objects passed to functions that might mutate them without documentation?
- [ ] Could this data structure be immutable? Would that simplify reasoning about it?
- [ ] Java: is `java.util.Date` used? (Replace with `java.time.LocalDate` / `Instant`)
- [ ] Python: mutable default arguments? (`def f(x, lst=[])` is a classic bug)
- [ ] Are internal collections returned directly? (representation exposure — callers can mutate internal state)

### Mutation and Iterator Invalidation

```java
// BAD: modifying list while iterating — skips elements or throws ConcurrentModificationException
for (String s : list) {
    if (shouldRemove(s)) list.remove(s);
}

// GOOD:
list.removeIf(s -> shouldRemove(s)); // Java 8+

// Or: iterator's own remove()
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    if (shouldRemove(iter.next())) iter.remove();
}
```

```python
# BAD: skips elements
for item in items:
    if bad(item): items.remove(item)

# GOOD:
items = [item for item in items if not bad(item)]
```

---

## Universal Review Checklist

### Correctness
- [ ] Does the code do what the PR/ticket describes?
- [ ] Edge cases handled: empty, null/None, 0, -1, max/min, unicode?
- [ ] Fail fast on bad input rather than propagating incorrect values?
- [ ] Off-by-one errors in loops or array indexing?
- [ ] Conditionals correct (`&&` vs `||`, `<=` vs `<`)?

### Readability (MIT 6.005)
- [ ] Names communicate intent? No `tmp`, `data`, `flag`, `x`?
- [ ] One purpose per variable? Parameters unmodified?
- [ ] Comments explain **why**, not **what**? No redundant comments?
- [ ] No magic numbers — named constants instead?
- [ ] Methods return results, not print them?
- [ ] No global mutable variables?
- [ ] Dead code, debug artifacts removed?

### Specifications
- [ ] Public functions have specs?
- [ ] Preconditions, postconditions, mutations documented?
- [ ] Exceptions documented with triggering conditions?

### Maintainability
- [ ] DRY — no duplicated logic?
- [ ] Testable by design (injectable deps, no hidden state)?
- [ ] Tests present and meaningful?

### Security
- [ ] User input validated?
- [ ] No hardcoded secrets?
- [ ] No injection risks?
- [ ] Auth/authz checks present?
- [ ] No sensitive data in logs?

---

## Python Review Checklist

### PEP 8 & Style (https://peps.python.org/pep-0008/)
- [ ] 4-space indentation, no tabs
- [ ] Lines ≤ 88 chars (Black) or ≤ 79 (strict PEP 8)
- [ ] `snake_case` functions/variables, `PascalCase` classes, `UPPER_CASE` constants
- [ ] Imports grouped: stdlib → third-party → local
- [ ] No wildcard imports

### Type Hints (https://typing.python.org/en/latest/reference/best_practices.html)
- [ ] Public functions have type hints on params and return
- [ ] `X | None` (3.10+) or `Optional[X]` for nullable values
- [ ] `list[int]` not `List[int]` in 3.9+

### Pythonic Idioms
- [ ] `with` for resources (files, DB connections)
- [ ] `enumerate()` not `range(len(...))`
- [ ] f-strings not `%` or `.format()`
- [ ] `dataclasses` for structured data
- [ ] `if __name__ == "__main__":` guard

### Mutable Default Argument (MIT 6.005 pattern)
```python
# BAD: default list shared across all calls
def add_item(item, lst=[]):
    lst.append(item)
    return lst

# GOOD:
def add_item(item, lst=None):
    if lst is None: lst = []
    lst.append(item)
    return lst
```

### Error Handling
- [ ] No bare `except:` or silent `except Exception: pass`
- [ ] Context managers for cleanup
- [ ] Exceptions carry context (`raise ValueError(f"Expected X, got {val}") from e`)

### Common Anti-Patterns
```python
# BAD: 'is' for value comparison
if x is 5: ...       # works by accident for small ints, breaks otherwise
# GOOD:
if x == 5: ...

# BAD: type() instead of isinstance()
if type(x) == int: ...
# GOOD:
if isinstance(x, int): ...

# BAD: mutating list while iterating (MIT 6.005)
for item in items:
    if bad(item): items.remove(item)
# GOOD:
items = [item for item in items if not bad(item)]
```

---

## JavaScript / TypeScript Review Checklist

### Style
- [ ] `const` by default; `let` only when reassignment needed; `var` never
- [ ] Strict equality (`===`) not loose (`==`)
- [ ] No `console.log` in production code

### TypeScript
- [ ] No `any` — use `unknown` and narrow
- [ ] No `!` assertions without explanation
- [ ] `strict: true` in tsconfig

### Async/Await
- [ ] `await` on every Promise-returning call
- [ ] Promise rejections caught
- [ ] `Promise.all()` for independent parallel calls

```typescript
// BAD: missing await
const data = fetchUser(id);
console.log(data.name); // undefined — data is a Promise

// BAD: no HTTP error check
const res = await fetch(url);
const data = await res.json(); // wrong error on 4xx/5xx

// GOOD:
const res = await fetch(url);
if (!res.ok) throw new Error(`HTTP ${res.status}`);
const data = await res.json();
```

### Security
- [ ] No `dangerouslySetInnerHTML` with unsanitized input
- [ ] No `innerHTML` — use `textContent`
- [ ] No `eval()` or `new Function()` with user input

---

## C++ Review Checklist

### Modern C++ (https://isocpp.github.io/CppCoreGuidelines/)
- [ ] `nullptr` not `NULL` or `0`
- [ ] Range-based `for` over index loops
- [ ] `std::array`/`std::vector` over raw arrays
- [ ] `std::string` over `char*`

### RAII & Memory
- [ ] No raw `new`/`delete` — use `std::make_unique<>` / `std::make_shared<>`
- [ ] `std::lock_guard`/`std::scoped_lock` instead of manual lock/unlock
- [ ] Rule of Five (or Rule of Zero with smart pointers)

### Type Safety
- [ ] `enum class` not plain `enum`
- [ ] `static_cast<>` not C-style casts
- [ ] `const` correctness on member functions and params
- [ ] `[[nodiscard]]` on error-code-returning functions

---

## Java Review Checklist

### Modern Java (8+)
- [ ] Streams/lambdas instead of verbose for-loop patterns
- [ ] `Optional<T>` instead of returning `null`
- [ ] Records instead of boilerplate POJOs (Java 16+)
- [ ] Try-with-resources for all `AutoCloseable`
- [ ] `@Override` on all overriding methods

### Immutability (MIT 6.005)
- [ ] No `java.util.Date` — use `java.time.*` (all immutable)
- [ ] Expose `Collections.unmodifiableList()` not raw internal lists
- [ ] Defensive copy mutable inputs before storing in fields

---

## Security: OWASP Top 10 Patterns

*Source: https://owasp.org/www-project-top-ten/ (2021)*

### A01: Broken Access Control
```python
# BAD: user controls user_id
record = db.query(f"SELECT * FROM orders WHERE user_id = {request.user_id}")
# GOOD:
record = db.query("SELECT * FROM orders WHERE user_id = ?", (current_user.id,))
```

### A02: Cryptographic Failures
```python
# BAD: MD5 for passwords
hashlib.md5(password.encode()).hexdigest()
# GOOD:
bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### A03: Injection
```python
# SQL
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")  # BAD
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))  # GOOD

# OS Command
subprocess.run(f"ls {user_input}", shell=True)  # BAD
subprocess.run(["ls", user_input])              # GOOD

# Template
Template(user_input).render()  # BAD
env.get_template("fixed.html").render(data=user_input)  # GOOD
```

### A04: Insecure Design
- No rate limiting on sensitive endpoints
- Excessive data in API responses
- Business logic steps that can be skipped

### A05: Security Misconfiguration
- `DEBUG=True` in production
- Stack traces exposed to users
- `Access-Control-Allow-Origin: *` with credentials

### A07: Auth Failures
```python
# BAD: not verifying JWT signature
jwt.decode(token, options={"verify_signature": False})
# GOOD:
jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### A08: Deserialization
```python
import pickle
pickle.loads(request.data)  # BAD — arbitrary code execution
json.loads(request.data)    # GOOD
```

### A09: Logging Failures
```python
logger.info(f"Login: {username}, password: {password}")  # BAD
logger.info(f"Request from {user_input}")  # BAD — log injection
logger.info("Login: %s", username)  # GOOD
```

### A10: SSRF
```python
requests.get(request.args.get("url"))  # BAD
# GOOD: validate against allowlist
if urllib.parse.urlparse(url).hostname not in ALLOWED_HOSTS:
    raise ValueError("URL not allowed")
```

---

## Security: CWE Pattern Catalog

| CWE | Name | Signal |
|-----|------|--------|
| CWE-20 | Improper Input Validation | User input used without validation |
| CWE-22 | Path Traversal | File paths built from user input |
| CWE-78 | OS Command Injection | `shell=True` + user input |
| CWE-79 | XSS | `innerHTML` with user data |
| CWE-89 | SQL Injection | String-formatted queries |
| CWE-94 | Code Injection | `eval`, `pickle.loads` on user data |
| CWE-190 | Integer Overflow | Arithmetic on user-controlled values |
| CWE-200 | Sensitive Data Exposure | PII in logs/error messages |
| CWE-285 | Improper Authorization | Missing authz checks |
| CWE-327 | Weak Cryptography | MD5/SHA1 for passwords |
| CWE-330 | Weak Randomness | `random` for security values |
| CWE-352 | CSRF | State-changing endpoints without CSRF token |
| CWE-400 | Resource Exhaustion | No rate limiting, unbounded loops |
| CWE-502 | Deserialization | `pickle`, Java ObjectInputStream on untrusted data |
| CWE-601 | Open Redirect | Redirect target from user input |
| CWE-918 | SSRF | Fetching user-supplied URLs |

---

## Performance Review Heuristics

### Algorithm & Data Structures
- O(n²) vs O(n log n) vs O(n) — is complexity appropriate for expected scale?
- Lookups in set/dict (O(1)) vs list (O(n))
- String concatenation in a loop

```python
# BAD: O(n²)
result = ""
for item in items: result += str(item)

# GOOD: O(n)
result = "".join(str(item) for item in items)
```

### Database (N+1 is the most common)
```python
# BAD: N+1 queries
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")

# GOOD: one query
users_with_orders = db.query("SELECT u.*, o.* FROM users u LEFT JOIN orders o ON o.user_id = u.id")
```
Also: missing indexes, `SELECT *`, unbounded queries, missing `LIMIT`.

### Memory
- Large objects held longer than necessary
- Generators vs full list construction
- Unbounded `lru_cache`
- Reading entire large files into memory

### Concurrency
- I/O-bound → async/await or threading
- CPU-bound → multiprocessing (Python GIL)
- Independent calls → `asyncio.gather()` not sequential awaits

---

## Design Pattern Recognition

| Pattern | Good Signal | Caution |
|---------|------------|---------|
| **Strategy** | Behavior injected, swappable | — |
| **Repository** | DB access behind interface | — |
| **Dependency Injection** | Deps passed in | — |
| **Observer/Events** | Decoupled producer/consumer | — |
| **Singleton** | Global mutable state | Hard to test; prefer DI |
| **God Object** | One class does everything | Decompose it |

---

## Anti-Pattern Catalog

### Arrow Code (use early returns — MIT 6.005: fail fast)
```python
# BAD
def process(data):
    if data is not None:
        if data.is_valid():
            if data.user is not None:
                do_thing(data)

# GOOD
def process(data):
    if data is None: return
    if not data.is_valid(): return
    if data.user is None: return
    do_thing(data)
```

### Magic Numbers → Named Constants
```python
# BAD
if response_code == 429: time.sleep(60)
# GOOD
if response_code == HTTP_TOO_MANY_REQUESTS: time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
```

### Boolean Trap
```python
widget.repaint(True)         # BAD — what does True mean?
widget.repaint(immediate=True)  # GOOD
```

### Long Parameter Lists (5+ params → group into dataclass)
### Primitive Obsession (raw strings/ints for typed concepts)
### Cargo Cult Code (copied without understanding — inconsistent style, comments that don't match code)

---

## Concurrency & Threading Review

### Race Conditions
```python
# BAD: read-modify-write unprotected
counter += 1
# GOOD:
with lock: counter += 1
```

### Deadlocks
Multiple locks in inconsistent order across threads. Always acquire in the same canonical order.

### Python GIL
- Threads → I/O-bound work
- `multiprocessing` → CPU-bound work
- `asyncio` → high-concurrency I/O

### Async Anti-Patterns
```python
# BAD: blocking in async context
async def fetch():
    time.sleep(5)  # freezes the event loop
# GOOD:
async def fetch():
    await asyncio.sleep(5)

# BAD: sequential independent awaits
a = await call_a()
b = await call_b()
# GOOD:
a, b = await asyncio.gather(call_a(), call_b())
```

### MIT 6.005 Thread-Safety Strategies
1. **Confinement** — don't share mutable data across threads
2. **Immutability** — nothing to race over
3. **Threadsafe data types** — `queue.Queue`, `threading.Lock`, `concurrent.futures`

---

## Memory Management Review (C/C++)

| Bug | Description |
|-----|-------------|
| Buffer overflow | Writing past end of buffer — use `std::vector`, bounds checks |
| Use-after-free | Accessing freed memory — smart pointers, AddressSanitizer |
| Double free | Freed twice — smart pointers prevent this |
| Memory leak | No free — RAII, Valgrind |
| Dangling pointer | Pointer to out-of-scope stack var — never return `&local` |

```cpp
// BAD: raw owning pointer, easy to miss delete on error path
Foo* f = new Foo();
delete f;

// GOOD: automatic cleanup
auto f = std::make_unique<Foo>();

// Smart pointer guide:
// unique_ptr: sole owner, zero overhead (default choice)
// shared_ptr: multiple owners, reference-counted
// weak_ptr: non-owning observer, breaks cycles
```

---

## API Design Standards

### REST
- [ ] HTTP verbs: GET (idempotent), POST (create), PUT/PATCH (update), DELETE
- [ ] Status codes: 200/201/204/400/401/403/404/409/422/500
- [ ] List endpoints paginated
- [ ] Sensitive data not in URL params
- [ ] Rate limiting headers present

### Internal APIs
- [ ] One thing per function
- [ ] Consistent return types
- [ ] Breaking changes versioned
- [ ] Error conditions communicated consistently (exceptions vs error codes)

---

## Database Review Standards

- [ ] All queries parameterized — no string formatting
- [ ] Queries scoped to authenticated user's data
- [ ] `LIMIT` on unbounded queries
- [ ] Multi-step mutations in transactions
- [ ] Indexes on WHERE/JOIN/ORDER BY columns
- [ ] NOT NULL constraints where appropriate
- [ ] ORM N+1 fixed (Django `select_related`, SQLAlchemy eager loading)
- [ ] Large-table indexes use `CONCURRENTLY` (Postgres)

---

## Architecture Review Guidance

### Dependency Direction
```
Presentation → Application → Domain → Infrastructure
```
Domain should not import Infrastructure. Business logic should not directly call `requests.get()`.

### Separation of Concerns
- [ ] HTTP parsing separate from business logic
- [ ] Business logic separate from DB queries
- [ ] Config in environment variables
- [ ] Auth in middleware, not scattered through handlers

### Testability (MIT 6.005: ready for change)
- [ ] External deps injected or behind interfaces
- [ ] Time and randomness injected (no `datetime.now()` in business logic)
- [ ] No global mutable state

---

## Cloud-Native & Microservices Standards

### 12-Factor App (https://12factor.net/)
- [ ] Config in environment variables
- [ ] Stateless processes
- [ ] Logs to stdout/stderr

### Service Communication
- [ ] Timeouts on all outbound calls
- [ ] Retries with exponential backoff and jitter
- [ ] Circuit breaker for unreliable downstreams

### Observability
- [ ] Structured JSON logging with correlation IDs
- [ ] RED metrics (rate, errors, duration)
- [ ] Health check endpoints

### Containers
- [ ] Not running as root
- [ ] Secrets in vault/Kubernetes Secrets
- [ ] Resource limits set
- [ ] Images pinned to digest, not `latest`

---

## AI-Generated Code Review Workflows

AI code has specific failure modes beyond human errors:

1. **Plausible but wrong** — subtle logic errors in edge cases not in the prompt
2. **Outdated APIs** — deprecated functions from before training cutoff
3. **Missing error handling** — generates happy path only
4. **Hallucinated libraries** — packages/functions that don't exist
5. **Injection vulnerabilities** — SQL injection, hardcoded credentials appear frequently
6. **Incorrect concurrency** — race conditions not obvious on reading
7. **Context blindness** — correct in isolation, wrong for the surrounding codebase

### AI Code Review Checklist
- [ ] Run the code. Don't just read it. AI code often fails on first run.
- [ ] Verify every import against current docs
- [ ] Test all edge cases explicitly (AI typically only tested the happy path)
- [ ] Extra scrutiny on security issues
- [ ] Verify fit with codebase conventions (naming, error handling, logging style)
- [ ] Look for "looks right but isn't" in algorithms, date handling, math

---

## Senior/Staff-Level Engineering Expectations

### Senior Engineer
- Error handling comprehensive, not bolted on
- Code testable by design (injectable deps, no hidden state)
- Changes backward compatible or clearly documented as breaking
- Documentation accurate and current

### Staff Engineer
- Architectural decisions justified and documented
- Abstractions appropriate — not too early, not too late
- Solution is the simplest thing that solves the problem
- Operational concerns addressed: monitoring, rollback, migration

### Key Questions at Any Level
- What happens when this fails? (graceful degradation)
- What happens at 10x load?
- How will we know if this breaks in production?
- How would we roll this back?
- What's the migration path for existing data/users?
