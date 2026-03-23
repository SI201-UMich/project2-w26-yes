# Your name: Ayush Madhav Kumar
# Your student id: 37761271
# Your email: ayushmk@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): no one
# If you worked with generative AI also add a statement for how you used it.
#no did not
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?  
# yes it did 

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import csv
import os
import re
import unittest
import requests

_POLICY_RE = (
    re.compile(r"^20\d{2}-00\d{4}STR$"),
    re.compile(r"^STR-000\d{4}$"),
)


def load_listing_results(html_path) -> list[tuple]:
    with open(html_path, encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    results: list[tuple] = []
    for card in soup.find_all(attrs={"data-testid": "card-container"}):
        title_el = card.find(attrs={"data-testid": "listing-card-title"})
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        listing_id = None
        for a in card.find_all("a", href=True):
            m = re.search(r"/rooms/(?:plus/)?(\d+)", a["href"])
            if m:
                listing_id = m.group(1)
                break
        if listing_id:
            results.append((title, listing_id))
    return results


def get_listing_details(listing_id) -> dict:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")
    with open(path, encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    text = soup.get_text(" ", strip=True)

    policy_m = re.search(r"Policy number:\s*(\S+)", text, re.I)
    if policy_m:
        policy_raw = policy_m.group(1).strip().strip("\ufeff")
        pl = policy_raw.lower()
        if pl == "pending":
            policy_number = "Pending"
        elif pl == "exempt":
            policy_number = "Exempt"
        else:
            policy_number = policy_raw
    else:
        policy_number = "Pending"

    host_type = "Superhost" if "Superhost" in text else "regular"

    host_name = ""
    for h2 in soup.find_all("h2"):
        ht = h2.get_text(" ", strip=True)
        hm = re.search(r"hosted by\s+(.+)$", ht, re.I)
        if hm:
            host_name = re.sub(r"\s+", " ", hm.group(1).strip())
            break

    subtitle = ""
    for h2 in soup.find_all("h2"):
        ht = h2.get_text(" ", strip=True)
        if re.search(r"hosted\s+by", ht, re.I) and re.search(
            r"\b(?:Entire|Private|Shared|loft|home|suite|guesthouse|apartment|rental|condo|guest)\b",
            ht,
            re.I,
        ):
            subtitle = ht
            break
    if not subtitle:
        h1 = soup.find("h1")
        subtitle = h1.get_text(" ", strip=True) if h1 else ""

    if "Private" in subtitle:
        room_type = "Private Room"
    elif "Shared" in subtitle:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    location_rating = 0.0
    for loc in soup.find_all(string=re.compile(r"^Location$")):
        sib = loc.parent.find_next_sibling()
        if sib:
            st = sib.get_text(strip=True)
            rm = re.match(r"^(\d+\.\d+)$", st)
            if rm:
                location_rating = float(rm.group(1))
                break
        parent = loc.parent
        if parent:
            combined = parent.get_text(" ", strip=True)
            rm2 = re.search(r"Location\s+(\d+\.\d+)", combined)
            if rm2:
                location_rating = float(rm2.group(1))
                break

    lid = str(listing_id)
    return {
        lid: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating,
        }
    }


def create_listing_database(html_path) -> list[tuple]:
    rows: list[tuple] = []
    for listing_title, listing_id in load_listing_results(html_path):
        details = get_listing_details(listing_id)[str(listing_id)]
        rows.append(
            (
                listing_title,
                listing_id,
                details["policy_number"],
                details["host_type"],
                details["host_name"],
                details["room_type"],
                details["location_rating"],
            )
        )
    return rows


def output_csv(data, filename) -> None:
    sorted_rows = sorted(data, key=lambda row: row[6], reverse=True)
    header = [
        "Listing Title",
        "Listing ID",
        "Policy Number",
        "Host Type",
        "Host Name",
        "Room Type",
        "Location Rating",
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(sorted_rows)


def avg_location_rating_by_room_type(data) -> dict:
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row in data:
        room_type = row[5]
        rating = row[6]
        if rating == 0.0:
            continue
        sums[room_type] = sums.get(room_type, 0.0) + rating
        counts[room_type] = counts.get(room_type, 0) + 1
    return {rt: sums[rt] / counts[rt] for rt in sums}


def validate_policy_numbers(data) -> list[str]:
    invalid: list[str] = []
    for row in data:
        listing_id = row[1]
        policy = row[2]
        if policy in ("Pending", "Exempt"):
            continue
        if any(p.match(policy) for p in _POLICY_RE):
            continue
        invalid.append(str(listing_id))
    return invalid


def google_scholar_searcher(query):
    base = "https://scholar.google.com"
    search_url = f"{base}/scholar?q={quote_plus(query)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Referer": f"{base}/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    def collect_titles(html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        out: list[str] = []
        selectors = (
            "#gs_res_ccl_mid h3.gs_rt a",
            "h3.gs_rt a",
            "#gs_res_ccl_mid .gs_rt a",
            "div.gs_ri h3 a",
            ".gs_rt a",
        )
        for sel in selectors:
            for a in soup.select(sel):
                t = a.get_text(" ", strip=True)
                if t and t not in seen:
                    seen.add(t)
                    out.append(t)
            if out:
                break
        if not out:
            for h3 in soup.select("h3.gs_rt"):
                a = h3.find("a", href=True)
                if a:
                    t = a.get_text(" ", strip=True)
                    if t and t not in seen:
                        seen.add(t)
                        out.append(t)
        return out

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.get(base, timeout=15)
        resp = session.get(search_url, timeout=25)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    if "sorry" in resp.text.lower() and "captcha" in resp.text.lower():
        return []

    titles = collect_titles(resp.text)
    return titles


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")
        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]
        results = [get_listing_details(lid) for lid in html_list]

        d467 = results[0]["467507"]
        self.assertEqual(d467["policy_number"], "STR-0005349")

        d194 = results[2]["1944564"]
        self.assertEqual(d194["host_type"], "Superhost")
        self.assertEqual(d194["room_type"], "Entire Room")
        self.assertEqual(d194["location_rating"], 4.9)

        self.assertIn("policy_number", results[3]["4614763"])
        self.assertIn("room_type", results[4]["6092596"])

    def test_create_listing_database(self):
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)
        self.assertEqual(
            self.detailed_data[-1],
            (
                "Guest suite in Mission District",
                "467507",
                "STR-0005349",
                "Superhost",
                "Jennifer",
                "Entire Room",
                4.8,
            ),
        )

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        try:
            output_csv(self.detailed_data, out_path)
            with open(out_path, newline="", encoding="utf-8-sig") as f:
                rows = list(csv.reader(f))
            self.assertEqual(
                rows[1],
                [
                    "Guesthouse in San Francisco",
                    "49591060",
                    "STR-0000253",
                    "Superhost",
                    "Ingrid",
                    "Entire Room",
                    "5.0",
                ],
            )
        finally:
            if os.path.isfile(out_path):
                os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        averages = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(averages["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])


def main():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_files", "search_results.html")
    detailed_data = create_listing_database(html_path)
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
