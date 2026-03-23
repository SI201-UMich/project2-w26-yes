# Project 2 — coding plan (4 tasks)

This plan splits work in `project2_starter.py` around dependencies: search parsing → per-listing parsing → combine + CSV → analytics + tests. See `instructions.md` for full specs and point values.

---

## Task 1 — Search results: `load_listing_results`

**Goal:** Return a list of `(listing_title, listing_id)` from `html_files/search_results.html` (18 listings; first tuple must match the rubric).

**Steps**

1. Open `html_files/search_results.html` with `encoding="utf-8-sig"` if needed.
2. Parse with BeautifulSoup; locate each listing link whose `href` contains `/rooms/` (or the pattern your file uses).
3. Extract the numeric **listing ID** from the URL (e.g. `.../rooms/1944564` → `"1944564"`).
4. Extract the **listing title** that pairs with each link (structure may differ from screenshots—inspect the actual HTML).
5. Return a **list of tuples** in a stable order (typically document order on the page).
6. Manually verify count **18** and first tuple `("Loft in Mission District", "1944564")` before moving on.

**Files:** `project2_starter.py` — function `load_listing_results` only (until Task 3 needs the rest).

---

## Task 2 — Listing pages: `get_listing_details`

**Goal:** For a given `listing_id`, read `html_files/listing_<listing_id>.html` and return the nested dict specified in `instructions.md` (policy, host type/name, inferred room type, location rating).

**Steps**

1. Build the path to `listing_<id>.html` next to the script (reuse `os.path` patterns used in tests).
2. **Policy:** Find text in the **host** area; normalize to a license string, `"Pending"`, or `"Exempt"` as appropriate.
3. **Host type:** `"Superhost"` if that label appears; else `"regular"`.
4. **Host name:** Support multiple hosts (e.g. `"Seth And Alexa"`).
5. **Room type:** From listing **subtitle** — substring `"Private"` → `"Private Room"`; `"Shared"` → `"Shared Room"`; otherwise `"Entire Room"`.
6. **Location rating:** Parse the location rating as `float`; if missing, use `0.0`.
7. Return `{ "<listing_id>": { ... } }` exactly as specified.

**Files:** `html_files/listing_*.html` (spot-check IDs from instructions/tests: `467507`, `1550913`, `1944564`, etc.).

---

## Task 3 — Full dataset + CSV: `create_listing_database` and `output_csv`

**Goal:** One row per listing in the required column order; CSV sorted by location rating descending with the exact header row.

**Steps**

1. **`create_listing_database(html_path)`:** Call `load_listing_results(html_path)`, then for each `(listing_title, listing_id)` call `get_listing_details(listing_id)` and flatten to:
   `(listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)`.
2. Confirm tuple length **7** and spot-check last row against `test_create_listing_database` in `instructions.md`.
3. **`output_csv(data, filename)`:** Sort `data` by `location_rating` **descending** (index 6).
4. Write CSV with header exactly:
   `Listing Title`, `Listing ID`, `Policy Number`, `Host Type`, `Host Name`, `Room Type`, `Location Rating`.
5. Run `main()` once to produce `airbnb_dataset.csv` for submission.

**Depends on:** Tasks 1 and 2.

---

## Task 4 — Analytics, validation, unit tests (and optional bonus)

**Goal:** Implement remaining functions, all six `TestCases`, and confirm the full script runs.

**Steps**

1. **`avg_location_rating_by_room_type(data)`:** Group by `room_type` (field index 5); average `location_rating` (index 6); **exclude** rows where rating is `0.0`.
2. **`validate_policy_numbers(data)`:** For non-Pending, non-Exempt policies, test against valid patterns:
   - `20##-00####STR`
   - `STR-000####`  
   Collect `listing_id`s that **fail** (return a `list[str]`).
3. **Tests:** Implement each method in `TestCases` per `instructions.md` / comments in `project2_starter.py`:
   - counts, first/last tuples, spot-checks for `get_listing_details`;
   - `test_output_csv`: write temp file, read back, assert first **data** row, `os.remove` the temp file;
   - averages and invalid policy list as specified.
4. Run: `python project2_starter.py` (or your entrypoint) — `main()` plus `unittest.main()` should pass.
5. **Optional bonus:** `google_scholar_searcher(query)` using `requests` + BeautifulSoup for first-page titles only (no tests required).

**Deliverables checklist:** working code, generated `airbnb_dataset.csv`, reflection files per `grading.md` (not part of these four coding tasks).

---

## Suggested order

Work **1 → 2 → 3 → 4**. Task 4 should be last because tests assume Tasks 1–3 behave correctly (`setUp` builds `self.listings` and `self.detailed_data` from `load_listing_results` and `create_listing_database`).
