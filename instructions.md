# SI 201: Project 2 — Airbnb “Scraping”

This document combines the official assignment text from `project2_instructions_w26.pdf` with details that are specific to **this repository** (starter code, data files, and Canvas submission notes in `grading.md`).

---

## Introduction

Starting in the 1990s, the San Francisco Bay Area has had an affordable housing shortage. The introduction of Airbnb caused serious concerns by taking potential rental units off the housing market. As of 2015, lawmakers have attempted to regulate this by requiring potential listers to receive a business license from the local government before offering short-term rentals. This allows the government to manage the number of short-term rental units in the city. However, the government will only investigate Airbnb and property listings after receiving a complaint.

In this project, you will simulate the work of an independent investigator: extracting public information, analyzing patterns, and validating compliance. You will extract structured data from Airbnb web pages using the **BeautifulSoup** Python library. Web pages are written in HTML, which is designed to display information in a browser rather than support data analysis. Your task is to use **web scraping**—extracting unstructured HTML and converting it into organized data—to analyze Airbnb listings.

In practice, web scraping often involves downloading pages automatically. However, many websites, including Airbnb, forbid automated scraping in their terms of service (see **Appendix**). To avoid violating Airbnb’s terms of service, this assignment provides **legally obtained, static HTML files** in the `html_files/` folder. **Use only those static files—do not send requests to the live Airbnb website.**

---

##                                                                                                                                                                                                                                                                                                                                  Repository layout (this project)


| Path                             | Role                                                                                            |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| `project2_starter.py`            | Implement required functions and `TestCases` here.                                              |
| `html_files/search_results.html` | Search results page used by `load_listing_results` / `create_listing_database`.                 |
| `html_files/listing_<id>.html`   | One saved listing page per ID referenced from search results (18 listings in the search index). |
| `grading.md`                     | Due date, GitHub Classroom workflow, and rubric (from Canvas).                                  |


The starter file imports `BeautifulSoup`, `re`, `os`, `csv`, `unittest`, and `requests` (for the bonus). `main()` writes `airbnb_dataset.csv` via `output_csv`; `unittest.main()` runs your tests when you execute the script.

---

## Collaboration and academic integrity

- You may work **individually** or in a **group of up to three** students.
- **All members** of a group must submit the **same GitHub URL** of the group’s repository on Canvas.
- If you collaborate, follow the **“Collaborating with GitHub”** document (Canvas: **Files → Useful Docs → Collab_with_Github.pdf**) before you start.
- You may use generative AI similarly to homework. You **must report** that you used it and **how** you used it. You are responsible for all GenAI-assisted code. The starter header includes fields for this disclosure and for alignment with your GenAI contract.

---

## Deliverables

Your Project 2 GitHub repository must include:

1. **All committed code** for Project 2.
2. **The output CSV** produced by your solution (e.g. `airbnb_dataset.csv` or the filename you use).
3. **One reflection file per team member**: `reflective_<first_name>.txt` or `reflective_<first_name>.pdf`.

Submission steps and commit expectations (fork, clone, ≥4 commits, push, submit repo link on Canvas) are summarized in `grading.md`.

---

## Tasks — functions

Implement every function below. Read **Debugging tips and tricks** (appendix) before you start.

### `load_listing_results(html_path) -> list[tuple]`

- **Input:** `html_path` — path to `search_results.html` (under `html_files/` in this repo).
- **Return:** A list of tuples `(listing_title, listing_id)`.
- **Listing ID:** The numeric ID in the listing URL (e.g. `https://www.airbnb.com/rooms/1944564` → `"1944564"`).

**Example output:**

```python
[
    ('Loft in Mission District', '1944564'),
    ('Home in Mission District', '49043049'),
    # ...
]
```

---

### `get_listing_details(listing_id) -> dict`

- **Input:** `listing_id` (string).
- **Return:** A nested dictionary:
  - **Outer key:** the `listing_id` (string).
  - **Inner dict** keys:


| Key               | Type    | Rules                                                                                                                                                                                                                            |
| ----------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `policy_number`   | `str`   | One of: a license/policy number string, `"Pending"`, or `"Exempt"`. Found in the **host** section; raw text may vary—normalize into these three categories when appropriate.                                                     |
| `host_type`       | `str`   | `"Superhost"` if “Superhost” appears; otherwise `"regular"`.                                                                                                                                                                     |
| `host_name`       | `str`   | Host name(s). If multiple hosts, include both (e.g. `"Seth And Alexa"`).                                                                                                                                                         |
| `room_type`       | `str`   | Must be `"Private Room"`, `"Shared Room"`, or `"Entire Room"`. **Not** given explicitly; infer from the listing **subtitle**: contains `"Private"` → Private Room; contains `"Shared"` → Shared Room; **neither** → Entire Room. |
| `location_rating` | `float` | Location rating from the ratings section. If there is no rating / you cannot find it, use `**0.0`**.                                                                                                                             |


**Example output:**

```python
{
    "1944564": {
        "policy_number": "2022-004088STR",
        "host_type": "Superhost",
        "host_name": "Brian",
        "room_type": "Entire Room",
        "location_rating": 4.9
    },
    # ...
}
```

**Data files:** For a given `listing_id`, read `html_files/listing_<listing_id>.html` (see repository file list below).

---

### `create_listing_database(html_path) -> list[tuple]`

- **Input:** `html_path` — path to `search_results.html`.
- **Behavior:** Use `load_listing_results()` for `(listing_title, listing_id)`, then `get_listing_details()` for the rest. Combine into one tuple **per listing** in this **order**:

`(listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)`

**Example output:**

```python
[
    ('Loft in Mission District', '1944564', '2022-004088STR', 'Superhost', 'Brian', 'Entire Room', 4.9),
    ('Home in Mission District', '49043049', 'Pending', 'Superhost', 'Cherry', 'Entire Room', 4.9),
    # ...
]
```

---

### `output_csv(data, filename) -> None`

- **Input:** `data` — list of tuples from `create_listing_database()`; `filename` — output CSV path/name.
- **Behavior:**
  - **Sort** rows in **descending** order by `location_rating`.
  - Write a CSV whose **header row** is exactly:
    `Listing Title`, `Listing ID`, `Policy Number`, `Host Type`, `Host Name`, `Room Type`, `Location Rating`
  - Each following row is one tuple, columns aligned with the header.

---

### `avg_location_rating_by_room_type(data) -> dict`

- **Input:** `data` — list of tuples from `create_listing_database()`.
- **Behavior:** For each `room_type`, compute the **average** `location_rating`.
- **Exclude** listings where `location_rating == 0.0` (treated as “no rating”) before averaging.

**Example output:**

```python
{
    'Private Room': 4.9,
    # ...
}
```

---

### `validate_policy_numbers(data) -> list[str]`

- **Input:** `data` — output of `create_listing_database()`.
- **Behavior:** For each row, check whether `policy_number` matches the **valid license format**. **Ignore** listings that are **Pending** or **Exempt**.
- **Return:** A list of `**listing_id`** strings whose policy numbers **do not** match the valid format.

**Valid formats** (`#` = any digit `0`–`9`):

- `20##-00####STR`
- `STR-000####`

---

## Test cases

After implementing the functions, implement the tests in `TestCases` (in `project2_starter.py`). Each test is worth **10 points** (6 tests → **60** points total).


| Test                                    | Requirements                                                                                                                                                                                                                                                                |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_load_listing_results`             | Extracted listing count is **18**. First tuple is `("Loft in Mission District", "1944564")`.                                                                                                                                                                                |
| `test_get_listing_details`              | Call `get_listing_details` for each ID in `["467507", "1550913", "1944564", "4614763", "6092596"]`. Spot-check against `listing_<id>.html`: **467507** → policy `"STR-0005349"`; **1944564** → host type `"Superhost"`, room type `"Entire Room"`, location rating **4.9**. |
| `test_create_listing_database`          | Every tuple has **7** fields. Last tuple is `("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)`.                                                                                                                    |
| `test_output_csv`                       | Write `detailed_data` to a CSV, read it back; first **data** row (after header) is `["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]`. (Starter uses a temp path like `test.csv`—remove the file after the test.)    |
| `test_avg_location_rating_by_room_type` | Average for `"Private Room"` is **4.9**.                                                                                                                                                                                                                                    |
| `test_validate_policy_numbers`          | Result list contains **exactly** `"16204265"` for this dataset.                                                                                                                                                                                                             |


---

## Reflective questions

Each student submits a **separate** file: `reflective_<first_name>.txt` or `reflective_<first_name>.pdf`. Paragraph-length, thoughtful answers are sufficient; there are no single “right” answers.

Context: you used scraping-style parsing on Airbnb HTML to study compliance with San Francisco rental rules—hosts, the platform, and third parties all play a role in accountability.

1. **Accountability:** Do you think the current system provides adequate accountability for short-term rentals in San Francisco? Explain why or why not. If inadequate, suggest a change in behavior or policy to improve accountability. You may refer to the **SWE Code of Ethics** as you think it through.
2. **Legality of scraping:** Web scraping’s legality in the U.S. is still debated. Skim the **Legal issues** (or equivalent) section of **[Web scraping](https://en.wikipedia.org/wiki/Web_scraping)** on Wikipedia and material on legal issues related to the **[Computer Fraud and Abuse Act](https://en.wikipedia.org/wiki/Computer_Fraud_and_Abuse_Act)**. Describe **at least one factor** you think is important when discussing the legality of web scraping and why.
3. **Ethics:** Scraping public data is not always socially beneficial. Consider cases such as the **[Facebook–Cambridge Analytica scandal](https://en.wikipedia.org/wiki/Facebook%E2%80%93Cambridge_Analytica_data_scandal)** or **[Clearview AI](https://en.wikipedia.org/wiki/Clearview_AI)**. Many argue that using personal data without meaningful consent—even when public—is unethical. Propose **at least two guidelines** you would use when deciding whether a web-scraping project is ethical.

**Grading:** **30** points total (**10** per question), graded per submission.

---

## Bonus: `google_scholar_searcher(query)`

> **Note:** The course PDF names this bonus in the narrative; the starter defines `**google_scholar_searcher(query)`**. Implement that name.

- Use `**requests**` to fetch the Google Scholar results page for `query`.
- Use **BeautifulSoup** to collect **titles on the first page only** (no pagination).
- **No test cases** are required for bonus credit.
- Results may differ over time from any example list in the PDF.

Example query `"airbnb"` returns a list of title strings (illustrative only):

```python
[
    'Progress on Airbnb: a literature review',
    'Digital discrimination: The case of Airbnb. com',
    # ...
]
```

---

## Grading summary


| Item                               | Points  |
| ---------------------------------- | ------- |
| `load_listing_results`             | 20      |
| `get_listing_details`              | 40      |
| `create_listing_database`          | 15      |
| `output_csv`                       | 10      |
| `avg_location_rating_by_room_type` | 10      |
| `validate_policy_numbers`          | 15      |
| Test cases (6 × 10)                | 60      |
| Reflection (3 × 10)                | 30      |
| **Course total**                   | **200** |
| Bonus: `google_scholar_searcher`   | **20**  |


Graders check correct **return shapes**, correct **use of prior functions** where required (e.g. `create_listing_database` building on `load_listing_results` / `get_listing_details`), and working tests. See `grading.md` for Canvas due date and submission workflow.

---

## Appendix

### Debugging tips and tricks

You can open HTML in VS Code; it is often easier to use the browser **Inspect** tools (Chrome/Firefox: right-click → Inspect; Safari: enable developer features first). The PDF notes that you might locate elements via tags/classes—**your** HTML may use different classes than any screenshot; always inspect **these** static files.

Static copies may look incomplete or oddly laid out because **CSS and JavaScript** from the live site are not bundled. For a fully rendered comparison, the assignment originally points to live Airbnb search/listing pages—**this course run still requires you to parse only the provided files**, not to scrape Airbnb live.

### Encoding (`utf-8-sig`)

If you get **encoding errors** when reading or writing files, open text files with:

```python
open("filename", "r", encoding="utf-8-sig")
```

Some Airbnb pages include characters that need this handling.

### Web scraping and accountability

Investigative work sometimes uses scraping of **public** pages to hold institutions accountable (the PDF cites investigative reporting examples).

### Airbnb terms of service

Airbnb’s Terms of Service prohibit automated access, e.g. *“Do not use bots, crawlers, scrapers, or other automated means to access or collect data…”* Enforceability is unsettled and U.S. cases differ. **This assignment uses manually obtained static HTML** so your work does not rely on automated collection against the live site.

---

## Static HTML files in `html_files/`

These files are in this repository for parsing:

- `search_results.html`
- `listing_11442567.html`, `listing_1550913.html`, `listing_16204265.html`, `listing_1944564.html`, `listing_23672181.html`, `listing_28803800.html`, `listing_31057117.html`, `listing_4614763.html`, `listing_467507.html`, `listing_47705504.html`, `listing_49043049.html`, `listing_49591060.html`, `listing_50010586.html`, `listing_6092596.html`, `listing_6107359.html`, `listing_11225011.html`, `listing_755957132088408739.html`, `listing_824047084487341932.html`

---

*Synthesized from `project2_instructions_w26.pdf`, `project2_starter.py`, and `grading.md`.*