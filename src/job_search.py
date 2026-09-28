import os
from datetime import datetime, timedelta, timezone

import requests


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


def is_relevant(job):
    title = str(job.get("title", "")).lower()
    description = str(job.get("description", "")).lower()
    text = f"{title} {description}"

    # Ignore old listings.
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

    target_fields = [
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
        "marketing",
        "content",
        "magazine",
        "broadcasting",
        "entertainment",
        "arts",
        "culture",
    ]

    unwanted_fields = [
        "software",
        "developer",
        "engineering",
        "engineer",
        "actuarial",
        "accounting",
        "accountant",
        "finance",
        "financial analyst",
        "human resources",
        " hr ",
        "logistics",
        "warehouse",
        "supply chain",
        "procurement",
        "hospitality",
        "property management",
        "construction",
        "mechanical",
        "electrical",
        "data scientist",
        "data science",
        "cyber security",
        "cybersecurity",
        "investment",
        "investment management",
        "financial resources",
        "wealth management",
        "asset management",
        "banking",
        "trading",
        "private equity",
        "venture capital",
        "insurance",
        "12 month",
        "12-month",
        "one year",
        "1 year",
        "18 month",
        "18-month",
        "two year",
        "2 year",
        "bali based",
        "bali-based",
    ]

    internship_terms = [
        "intern",
        "internship",
        "placement",
        "student placement",
        "summer placement",
        "summer internship",
    ]

    excluded_roles = [
        "runner",
        "production runner",
        "camera runner",
        "floor runner",
        "graduate scheme",
        "graduate programme",
        "graduate program",
    ]

    has_target_field = any(
        term in text for term in target_fields
    )

    has_unwanted_field = any(
        term in text for term in unwanted_fields
    )

    has_internship = any(
        term in text for term in internship_terms
    )

    has_excluded_role = any(
        term in title for term in excluded_roles
    )

    return (
        has_target_field
        and has_internship
        and not has_unwanted_field
        and not has_excluded_role
    )


def process_jobs():
    jobs_by_id = {}

    for query in SEARCHES:
        for job in search_jobs(query):
            job_id = job.get("id")

            if job_id and job_id not in jobs_by_id:
                if is_relevant(job):
                    jobs_by_id[job_id] = job

    results = []

    for job in jobs_by_id.values():
        results.append({
            "company": job.get("company", {}).get("display_name", ""),
            "role": job.get("title", ""),
            "location": job.get("location", {}).get("display_name", ""),
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

    for job in jobs:
        print(
            f"{job['company']} | "
            f"{job['role']} | "
            f"{job['location']}"
        )
