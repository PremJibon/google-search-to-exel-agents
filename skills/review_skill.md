# Review Skill (`skills/review_skill.md`)

## 1. Purpose
The **Review Skill** acts as an internal quality assurance auditor before data is presented to the user or rendered into Excel/CSV. It guarantees that the leads adhere to strict accuracy, normalization, and zero-hallucination standards.

---

## 2. Review Checklist & Rules

### Rule 1: Zero Fabrication Audit
- Inspect every row in the dataset.
- Check for placeholder text (e.g., "N/A", "Unknown", "123-456-7890", "example.com").
- If a data point was not explicitly returned by the underlying provider response, ensure it is set to an empty string `""` rather than synthetic data.

### Rule 2: Phone Number Integrity
- Ensure phone numbers contain valid digit counts (minimum 7 digits, maximum 15 digits).
- Check that unwanted punctuation, spaces, or stray alphabetic characters are eliminated.
- If "Require Phone" was toggled ON, ensure that 100% of rows in the export set contain non-empty phone fields.

### Rule 3: URL and Maps Link Verification
- Ensure websites start with a valid scheme (`http://` or `https://`).
- Ensure Maps URLs point to verified OpenStreetMap node/way/relation links or Google Maps URLs.
- Strip tracking query parameters (`utm_source`, `ref`, etc.).

### Rule 4: Deduplication Verification
- Calculate uniqueness across:
  - Phone number
  - Normalized business name + geographical coordinate within 150 meters
- Ensure zero duplicate rows exist in the final set.

### Rule 5: CSV/Excel Injection Security
- Check text fields for risky leading characters (`=`, `+`, `-`, `@`, `|`) that could trigger spreadsheet formula execution.
- If found, prepend a single quote `'` to sanitize the cell content.

---

## 3. Review Outcome Structure
The Review Skill produces a diagnostic summary:
```json
{
  "total_reviewed": 50,
  "valid_leads": 48,
  "removed_duplicates": 2,
  "missing_phones_detected": 14,
  "sanitized_formula_cells": 0,
  "passed_review": true
}
```
