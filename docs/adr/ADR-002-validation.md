# ADR-002: Use Custom Validation Instead of Pandera

**Date:** 2026-07-10  
**Status:** Accepted  
**Author:** Vishal  

---
## Context

CleanSweep needs to validate every row from 5 different supplier files
before loading it into the conformed layer.

Validation rules include:
- Price must be a positive number
- Quantity must be a positive integer
- Order date must be in YYYY-MM-DD format
- Product name must be a non-empty string

The team evaluated two approaches:
1. **Pandera** — a third-party DataFrame validation library
2. **Custom validator** — hand-written validation functions in Python

## Options Considered

### Option 1: Pandera
- ✅ Declarative schema definitions (clean, readable)
- ✅ Industry-standard library used in production
- ❌ Extra dependency to install and learn
- ❌ Error messages are harder to customise
- ❌ Less flexible for supplier-specific rules

### Option 2: Custom Validator ✅ CHOSEN
- ✅ Full control over validation logic per supplier
- ✅ Custom error messages stored in quarantine table
- ✅ Easy to understand — plain Python functions
- ✅ No extra dependencies beyond pandas
- ❌ More code to write and maintain

## Decision

We chose a **custom validator** (`src/validation/validator.py`).

For a learning project, writing validation logic from scratch builds
understanding of how data quality checks work. Each rule is a simple
Python function (`is_valid_price`, `is_valid_date`) that is easy to
read, test, and explain at a showcase.

The quarantine design (saving bad rows with a reason) would be harder
to implement cleanly with Pandera's schema-based approach.

## Consequences

**Positive:**
- Full control over what happens to bad rows (quarantine with reason)
- Every rule is transparent and readable in plain Python
- Easy to add new rules for new suppliers

**Negative:**
- Must maintain validation rules manually as suppliers change
- No built-in statistical validation (e.g. value distributions)
- In production, Pandera or Great Expectations would be preferred

## Conclusion

Custom validation was the right choice for a learning prototype.
For production at scale, migrating to Pandera would be straightforward
since the validation logic is already modular.
