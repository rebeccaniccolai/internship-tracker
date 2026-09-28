import os
from datetime import datetime, timedelta, timezone

import requests
from sheets_writer import add_jobs

API_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

SEARCHES = [
    "journalism intern",
    "publishing intern",
    "editorial intern",
    "film intern",
    "television intern",
    "media intern",
    "communications intern",
    "PR intern",
    "publicity intern",
    "marketing intern",
    "content intern",
    "magazine intern",
    "broadcasting intern",
    "entertainment intern",
    "arts intern",
    "culture intern",
    "journalism placement",
    "publishing placement",
    "editorial placement",
    "film placement",
    "media placement",
    "communications placement",
    "PR placement",
    "marketing placement",
    "content placement",
]


def search_jobs(query):
    response = requests.get(
        API_URL,
        params={
            "app_id": os.environ["ADZUNA_APP_ID"],
            "app_key": os.environ["ADZUNA_APP_KEY"],
            "results_per_page": 50,
            "where": "London",
            "what": query,
            "content-type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json().get("results", [])


def normalise_text(text):
    return " ".join(str(text).lower().split())


def is_relevant(job):
    title = normalise_text(job.get("title", ""))
    description = normalise_text(job.get("description", ""))

    # ---------------------------------------------------------
    # 1. Ignore very old listings
    # ---------------------------------------------------------

    created = job.get("created", "")

    try:
        posted_date = datetime.fromisoformat(
            created.replace("Z", "+00:00")
        )

        cutoff = datetime.now(timezone.utc) - timedelta(days=180)

        if posted_date < cutoff:
            return False

    except Exception:
        pass

    # ---------------------------------------------------------
    # 2. Roles we definitely do NOT want
    # ---------------------------------------------------------

    excluded_title_terms = [
        "runner",
        "production runner",
        "camera runner",
        "floor runner",

        "graduate scheme",
        "graduate programme",
        "graduate program",

        "sales executive",
        "sales associate",
        "business development",
        "account executive",
        "account manager",

        "financial analyst",
        "investment analyst",
        "investment banking",
        "asset management",
        "wealth management",
        "private equity",
        "venture capital",
        "trading",

        "software engineer",
        "software developer",
        "data scientist",
        "data analyst",
        "cyber security",
        "cybersecurity",

        "actuarial",
        "accountant",
        "accounting",
        "procurement",
        "supply chain",
        "logistics",

        "digital marketing executive",
        "marketing executive",

        "placement programme",
        "placement program",
    ]

    if any(term in title for term in excluded_title_terms):
        return False

    # ---------------------------------------------------------
    # 3. Exclude obvious long-term roles
    # ---------------------------------------------------------

    long_term_terms = [
        "12 month",
        "12-month",
        "one year",
        "1 year",
        "18 month",
        "18-month",
        "two year",
        "2 year",
        "24 month",
        "24-month",
    ]

    if any(term in title for term in long_term_terms):
        return False

    # ---------------------------------------------------------
    # 4. Exclude obvious finance / technical roles
    #
    # Only look at the TITLE here.
    # This avoids accidentally rejecting a communications
    # internship simply because the company works in finance.
    # ---------------------------------------------------------

    excluded_title_fields = [
        "finance",
        "financial",
        "banking",
        "investment",
        "insurance",
        "actuarial",
        "accounting",
        "audit",
        "wealth",
        "asset management",
        "private equity",
        "venture capital",
        "trading",
        "developer",
        "engineering",
        "data scientist",
        "data science",
        "cyber",
        "procurement",
        "logistics",
        "supply chain",
        "property management",
        "construction",
        "mechanical",
        "electrical",
    ]

    if any(term in title for term in excluded_title_fields):
        return False

    # ---------------------------------------------------------
    # 5. Must actually be an internship / placement
    # ---------------------------------------------------------

    internship_terms = [
        "intern",
        "internship",
        "placement",
        "student placement",
        "summer placement",
        "summer internship",
    ]

    has_internship = any(
        term in title for term in internship_terms
    )

    if not has_internship:
        return False

    # ---------------------------------------------------------
    # 6. Target fields
    #
    # Strongest preference is for these appearing in the TITLE.
    # Some broader terms are allowed in the description too.
    # ---------------------------------------------------------

    strong_title_fields = [
        "journalism",
        "journalist",
        "publishing",
        "editorial",
        "editor",
        "film",
        "cinema",
        "television",
        "tv",
        "media",
        "communications",
        "public relations",
        "pr ",
        "publicity",
        "content",
        "magazine",
        "broadcasting",
        "entertainment",
        "arts",
        "culture",
        "creative",
        "social media",
        "marketing",
    ]

    broad_description_fields = [
        "journalism",
        "publishing",
        "editorial",
        "film",
        "cinema",
        "television",
        "media",
        "communications",
        "public relations",
        "publicity",
        "content",
        "magazine",
        "broadcasting",
        "entertainment",
        "arts",
        "culture",
        "creative",
        "social media",
        "marketing",
    ]

    title_match = any(
        term in title for term in strong_title_fields
    )

    description_match = any(
        term in description for term in broad_description_fields
    )

    # The role needs to be directly relevant in the title,
    # OR have a clearly relevant description.
    if not title_match and not description_match:
        return False

    # ---------------------------------------------------------
    # 7. Remove clearly sales-heavy roles
    # ---------------------------------------------------------

    sales_terms = [
        "sales",
        "business development",
        "lead generation",
        "cold calling",
        "sales pipeline",
    ]

    if any(term in title for term in sales_terms):
        return False

    # ---------------------------------------------------------
    # 8. Remove obvious training / course / consultancy
    # "placement" listings
    # ---------------------------------------------------------

    fake_placement_terms = [
        "training programme",
        "training program",
        "course",
        "bootcamp",
        "career programme",
        "career program",
        "no experience needed",
        "work experience programme",
        "work experience program",
    ]

    if any(term in title for term in fake_placement_terms):
        return False

    # ---------------------------------------------------------
    # 9. Return genuine potential match
    # ---------------------------------------------------------

    return True


def process_jobs():
    jobs_by_key = {}

    for query in SEARCHES:
        for job in search_jobs(query):

            if not is_relevant(job):
                continue

            company = (
                job.get("company", {})
                .get("display_name", "")
                .strip()
            )

            role = job.get("title", "").strip()

            url = job.get("redirect_url", "").strip()

            # Deduplicate using company + role + URL.
            # This catches cases where Adzuna gives the same
            # vacancy different IDs.
            unique_key = (
                company.lower(),
                role.lower(),
                url.lower(),
            )

            if unique_key not in jobs_by_key:
                jobs_by_key[unique_key] = job

    results = []

    for job in jobs_by_key.values():

        results.append({
            "company": (
                job.get("company", {})
                .get("display_name", "")
            ),
            "role": job.get("title", ""),
            "location": (
                job.get("location", {})
                .get("display_name", "")
            ),
            "posted_date": job.get("created", ""),
            "deadline": "",
            "category": "Potential match",
            "match": "Potential match",
            "application_url": job.get("redirect_url", ""),
            "source": "Adzuna",
            "status": "🆕 New",
            "date_added": "",
            "notes": "",
        })

    return results


if __name__ == "__main__":
    jobs = process_jobs()

    print(f"Found {len(jobs)} potential matches.")

    rows_added = add_jobs(jobs)

    print(f"Added {rows_added} new jobs to Google Sheets.")
        )
