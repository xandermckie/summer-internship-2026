# MIT 6.031 Software Construction — Review Principles

Source: MIT 6.031 "Software Construction" (Spring 2022)
https://web.mit.edu/6.031/www/sp22/

The MIT Software Construction course organizes all code quality around three goals.
Every review question ultimately traces back to one of these:

| Goal | Question to ask |
|------|----------------|
| **Safe from bugs** | Correct today and correct in the unknown future? |
| **Easy to understand** | Clear to future programmers, including future you? |
| **Ready for change** | Designed to accommodate change without rewriting? |

---

## MIT Code Review Rules (Reading 4)

These are the concrete, objective rules MIT teaches for code review.
They're language-agnostic and apply to every review.

### 1. Don't Repeat Yourself (DRY)

Duplicated code is a safety risk. A bug in duplicated code must be fixed in every
copy — and it usually isn't. Copy-paste creates invisible coupling between
disconnected parts of the codebase.

**Flag when you see:**
- The same logic in two or more places
- Repeated literals (same number, same string) without a named constant
- Copy-pasted functions that differ only in a parameter

**The fix:** Extract the common logic. Even a two-line helper is worth it if it
removes duplication.

```python
# BAD: 12 branches each adding a hardcoded cumulative day count
if month == 2:
    day_of_month += 31
elif month == 3:
    day_of_month += 59
# ... 10 more branches

# GOOD: data-driven, DRY
MONTH_LENGTHS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
for m in range(1, month):
    day_of_month += MONTH_LENGTHS[m]
```

### 2. Comments Where Needed

Good comments make code safer and more maintainable. But over-commenting is noise.

**Comments that add value:**
- Specifications above functions: what it does, preconditions, postconditions,
  exceptions. A reader should be able to use the function from the spec alone.
- Explanations of *why*, not *what* ("This loop is O(n²) but n is always < 20")
- Citations for non-obvious algorithms ("Knuth vol. 2 §4.5.2")
- Flags for known issues ("TODO: handle leap years")

**Comments that are noise (flag these):**
- Restating what the code already says (`i += 1  # increment i`)
- Commented-out code left in
- Outdated comments that no longer match the code

```python
# BAD: comment restates the code
x = x + 1  # add 1 to x

# GOOD: comment explains why
# Offset by 1 because the API uses 1-based indexing
x = x + 1
```

### 3. Fail Fast

Code should detect problems as close to the source as possible — not silently
continue with bad state that causes a confusing failure 10 calls later.

**Principle:** If a function has a precondition (valid inputs), check it at the
start and raise an informative error immediately.

```python
# BAD: accepts garbage, fails mysteriously later
def compute_ratio(a, b):
    return a / b  # ZeroDivisionError with no context

# GOOD: fail fast with clear message
def compute_ratio(a, b):
    if b == 0:
        raise ValueError(f"Denominator cannot be zero (a={a})")
    return a / b
```

**Flag when you see:**
- Functions that proceed silently on invalid input
- Silent returns (`return None`, `return []`) where the caller won't know something went wrong
- Error conditions checked much later than where they occur

### 4. Avoid Magic Numbers

A number with no name is a mystery. The reader has no way to know what it means,
whether it's intentional, or whether it needs to change if requirements change.

```python
# BAD: what is 86400? what is 7?
if elapsed > 86400 * 7:
    expire_session()

# GOOD: self-documenting
SECONDS_PER_DAY = 86400
SESSION_TIMEOUT_DAYS = 7

if elapsed > SECONDS_PER_DAY * SESSION_TIMEOUT_DAYS:
    expire_session()
```

**Flag:** Any literal number (or string) embedded in logic that isn't 0, 1, or an
obviously universal constant.

### 5. One Purpose for Each Variable

A variable that gets reused for different purposes at different points in a
function is hard to track. Its type might even change (in dynamic languages).

```python
# BAD: 'temp' used for three different things
temp = get_user_input()
temp = temp.strip().lower()
temp = db.lookup(temp)
return temp

# GOOD: each variable has one job
raw_input = get_user_input()
normalized = raw_input.strip().lower()
user = db.lookup(normalized)
return user
```

**Flag:** Variables named `temp`, `data`, `result`, `val` that are reused for
unrelated values. Variables whose types change mid-function.

### 6. Use Good Names

Names are the primary documentation for what code does. A well-named codebase
barely needs comments.

**Good names:**
- Describe the *purpose*, not the type or implementation (`user_count`, not `int1`)
- Are consistent with domain vocabulary and existing codebase conventions
- Are pronounceable and memorable
- Avoid abbreviations unless they're universal (`url`, `id`, `num`)

**Name red flags:**
- Single-letter variables outside of conventional uses (`i`, `j` for loop indices; `x`, `y` for coordinates)
- Generic names: `data`, `info`, `manager`, `handler`, `util`
- Boolean names that don't read as a question: `flag`, `status` → use `is_valid`, `has_permission`
- Functions named with vague verbs: `process()`, `handle()`, `do_thing()`

```python
# BAD
def calc(a, b, f):
    return a * (1 - b) if f else a

# GOOD
def calculate_discounted_price(price, discount_rate, apply_discount):
    return price * (1 - discount_rate) if apply_discount else price
```

### 7. Use Whitespace to Help the Reader

Consistent, meaningful whitespace is free documentation. It groups related things
together and separates unrelated things.

- Blank lines between logical sections of a function
- Spaces around operators and after commas
- Consistent indentation (automated by formatters — flag if a project has no formatter)
- Align related assignments only if it aids readability (not as a rule)

**Flag:** Dense, unspaced code; inconsistent indentation; mixed tabs and spaces.

### 8. Don't Use Global Variables

Global mutable state is one of the primary sources of bugs in large programs.
Any function anywhere can modify it; its value at any point depends on the entire
execution history.

```python
# BAD: global mutable state
current_user = None

def login(user):
    global current_user
    current_user = user

def get_profile():
    return current_user.profile  # depends on hidden state

# GOOD: pass state explicitly
def get_profile(user):
    return user.profile
```

**Exceptions:** Constants (truly immutable) and well-encapsulated singletons
(database connection pool, application config loaded once at startup) are
acceptable. Flag *mutable* globals.

### 9. Functions Should Return Results, Not Print Them

A function that `print()`s its output can't be composed, tested, or reused. It
mixes computation with I/O.

```python
# BAD: untestable, non-composable
def double(x):
    print(x * 2)  # output goes to stdout, can't be used by caller

# GOOD: pure function, easy to test and compose
def double(x):
    return x * 2
```

**Flag:** Functions that `print()` or write to files/logs as their primary output
instead of returning values. (Logging for observability is fine — *replacing* the
return value with a print is not.)

### 10. Avoid Special-Case Code

Special cases add branches, which add complexity. If you find yourself writing
`if month == 2: handle_february_specially`, that's often a sign the general
solution isn't general enough.

```python
# BAD: special case for one value
def days_in_month(month, year):
    if month == 2:
        return 29 if is_leap_year(year) else 28  # special case
    elif month in (4, 6, 9, 11):
        return 30
    else:
        return 31

# BETTER: table-driven, no special cases in calling code
DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def days_in_month(month, year):
    days = DAYS[month]
    if month == 2 and is_leap_year(year):
        days += 1
    return days
```

---

## MIT Testing Principles (Reading 3)

When reviewing tests (or noting their absence), apply these MIT criteria.

### Test-First Programming

Tests should be written *before* the implementation. If tests are added after,
they're often shaped by the implementation rather than the specification, and edge
cases get missed.

**Review question:** Do the tests reflect the *spec* (what the function should do),
or the *implementation* (what the current code happens to do)?

### Partition Testing (Input Space Partitioning)

Good tests cover the *boundary* between correct and incorrect behavior, not just
the happy path. MIT teaches choosing test cases by partitioning the input space:

1. Identify the *dimensions* of the input (each parameter, plus combinations)
2. For each dimension, identify the *partitions*: ranges of values that should
   produce similar behavior
3. Pick at least one test case from each partition, with emphasis on boundaries

**Classic partitions to check for:**
- Empty / single element / many elements
- Zero / negative / positive / max value
- Null / None / missing
- First / middle / last element of a collection
- Sorted / unsorted / reverse-sorted
- Valid / invalid / boundary-of-valid input

```python
# For a function abs(x: int) -> int:
# Partitions: x < 0, x = 0, x > 0
# Good tests: abs(-5), abs(0), abs(5)
# Also: abs(INT_MIN) — boundary often breaks naive implementations
```

**Flag when you see:**
- Tests that only cover the happy path
- No test for empty/null input
- No test for boundary values
- Only one or two test cases for a function with complex input space

### Black Box vs. Glass Box Testing

- **Black box**: Test cases derived from the *specification* alone, without
  looking at the implementation. Finds cases the implementer forgot.
- **Glass box**: Test cases derived from the *implementation* structure (e.g.,
  covering each `if` branch). Finds cases the spec doesn't exercise.

Both are needed. A test suite that only has happy-path tests is neither.

### Code Coverage

A well-tested function has tests that exercise:
- Every branch (`if`/`else`, `try`/`except`)
- Every loop (zero iterations, one iteration, many iterations)
- Every `return` or `raise` path

**Flag:** Code with no tests, or tests that demonstrably miss branches.

### Automated Regression Testing

Tests should be automated — runnable with one command, producing a clear
pass/fail. They should be run on every change (CI).

**Flag:**
- Manual-only tests ("run this script and check the output by eye")
- Tests with no assertions
- Tests that require external setup not documented or automated

---

## MIT Specification Principles (Reading 6)

### What a Good Spec Looks Like

A function specification (docstring / doc comment) should answer:
1. **Preconditions**: What must be true about the inputs for the function to work?
2. **Postconditions**: What does the function guarantee about the output?
3. **Exceptions**: What exceptions can it raise, and under what conditions?
4. **Side effects**: Does it mutate any of its inputs?

```python
def binary_search(arr: list[int], target: int) -> int:
    """
    Find the index of target in arr using binary search.

    Preconditions:
        arr is sorted in ascending order.
        arr contains no duplicate values.

    Returns:
        The index i such that arr[i] == target.

    Raises:
        ValueError: if target is not present in arr.
    """
```

**Review question (from MIT):** Can another engineer determine the *complete
expected behavior* of this function from its specification alone, without reading
the implementation?

### Specification Strength

- A **strong** spec constrains behavior tightly — it leaves little room for
  different implementations. Good for public APIs.
- A **weak** spec allows multiple valid implementations. Good for internal
  helpers that may be optimized later.

**Flag:** Specs that are *too weak* (the caller can't rely on anything meaningful)
or *too strong* (the spec describes implementation details that should be free to change).

### Representation Exposure

If a class returns a reference to its internal mutable data structure, external
code can modify it without going through the class's API. This breaks encapsulation.

```python
# BAD: exposes internal list
class Playlist:
    def __init__(self):
        self._songs = []
    
    def get_songs(self):
        return self._songs  # caller can mutate this!

# GOOD: return a copy
def get_songs(self):
    return list(self._songs)

# BETTER: return an immutable view
def get_songs(self):
    return tuple(self._songs)
```

**Flag:** Methods that return direct references to internal mutable fields,
especially collections.

---

## MIT Immutability Principles

MIT dedicates significant attention to mutability because a large fraction of
real-world bugs come from unexpected state mutation.

### Prefer Immutability

An immutable object's value never changes after construction. This eliminates an
entire class of bugs — you can reason about it locally without tracking all the
places it might be modified.

```python
# Mutable: dangerous in concurrent code, harder to reason about
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def translate(self, dx, dy):
        self.x += dx  # mutates self
        self.y += dy

# Immutable: safe to share, easy to reason about
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float
    
    def translate(self, dx, dy) -> "Point":
        return Point(self.x + dx, self.y + dy)  # returns new value
```

**Flag:**
- Objects passed into functions and mutated inside them (unexpected aliasing)
- Functions with "output parameters" (mutable containers passed in for results)
- Shared mutable state accessed from multiple call sites

### Aliasing Bugs

When two variables point to the same mutable object, mutating one affects the other.
This is a common, subtle source of bugs.

```python
a = [1, 2, 3]
b = a           # b is an alias for a, not a copy
b.append(4)
print(a)        # [1, 2, 3, 4] — a was also modified!

# Fix: copy explicitly
b = list(a)     # or a[:]
b.append(4)
print(a)        # [1, 2, 3] — a is unchanged
```

**Flag:** Assignments of mutable objects without copying, especially when the
original is expected to remain unchanged.
