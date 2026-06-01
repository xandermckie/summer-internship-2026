# Week 2 Code Review Summary

**Review Date:** June 1, 2026  
**Reviewed By:** Claude Code Review

---

## Files Reviewed

Only **1 Python file** found in the repository:

### 1. `notes/weather.py`

**What it does:**  
Fetches weather data from the wttr.in API for a list of cities and displays current temperature and conditions.

**Key Features:**
- Validates city name input (non-empty string, alphanumeric + spaces only)
- Calls wttr.in API with 5-second timeout
- Handles multiple error types (timeouts, HTTP errors, invalid response data)
- Batch processing via `get_weather_for_cities()`

---

## Code Quality Assessment

| Category | Status | Notes |
|----------|--------|-------|
| **Correctness** | ✅ Good | Solid error handling and API integration. Edge cases handled well. |
| **Readability** | ✅ Good | Clear variable names, good comments, well-separated functions. |
| **Best Practices** | ⚠️ Needs Fix | Module-level function call executes on import — should use `if __name__ == "__main__":` |
| **Security** | ✅ Good | Proper input validation; no hardcoded secrets or injection vulnerabilities. |

---

## Issues Flagged

### 🔴 Critical (Fix before Week 3)

1. **Auto-executing entry point** — The line `get_weather_for_cities(...)` at module level will run whenever the file is imported, which breaks library usage.
   - **Fix:** Wrap in `if __name__ == "__main__":`
   - **Priority:** High — this prevents reuse and causes unexpected behavior

### 🟡 Medium Priority

2. **Returns don't propagate data** — Functions print directly instead of returning values, making them hard to test and integrate with other code.
   - **Fix:** Have `get_weather()` return the weather dict; let the caller handle printing
   - **Priority:** Medium — improves testability and reusability

3. **Manual URL sanitization** — Current validation is good, but `urllib.parse.quote()` is the standard approach for URL encoding.
   - **Fix:** Use `urllib.parse.quote(city)` instead of `.replace(" ", "").isalnum()`
   - **Priority:** Medium — more robust and idiomatic Python

4. **Using `print()` instead of logging** — For any production code, use Python's `logging` module instead of print statements.
   - **Fix:** Switch to `logging.info()` and `logging.error()`
   - **Priority:** Low — good-to-have for real applications

---

## What to Fix Before Week 3

**Priority 1 (Do First):**
- Add `if __name__ == "__main__":` guard around the entry point call

**Priority 2 (Do Next):**
- Refactor `get_weather()` to return data instead of printing
- Update caller code to handle output

**Priority 3 (Nice to Have):**
- Replace manual string validation with `urllib.parse.quote()`
- Migrate from `print()` to `logging` module

---

## Learning Recommendation

**Learn more about: `if __name__ == "__main__":` and module design**

This is a fundamental Python pattern for writing code that can be both run as a script *and* imported as a library without unwanted side effects. It's essential for building reusable code.

---

## Summary

**Overall:** Good foundational code with solid error handling. The main blocker is the auto-executing entry point — fix that first, then refactor to return data instead of printing. After those changes, this will be a clean, reusable weather module.

**Next Steps:** 
1. Add `if __name__ == "__main__":` guard
2. Refactor functions to return values
3. Consider adding unit tests for the validation logic
