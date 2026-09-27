import json
import re
import requests
from datetime import datetime, timezone


API_URL = "https://www.arbeitnow.co.uk/api/job-board-api"


def load_criteria():
    with open("config/criteria.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_jobs():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict):
        return data.get("data", [])

    return data


def text_matches(text, keywords):
    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


def is_london(job):
    location = str(job.get("location", "")).lower()

    return (
        "london" in location
        or "greater london" in location
    )


def is_internship_or_placement(job, criteria):
    title = str(job.get("title", "")).lower()
    description = str(job.get("description", "")).lower()

    combined = f"{title} {description}"

    include = criteria["role_type"]["include"]
    exclude = criteria["role_type"]["exclude"]

    has_internship_term = any(
        term.lower() in combined
        for term in include
    )

    has_excluded_term = any(
        term.lower() in combined
        for term in exclude
    )

    return has_internship_term and not has_excluded_term


def is_relevant_field(job, criteria):
    title = str(job.get("title", "")).lower()
    description = str(job.get("description", "")).lower()

    combined = f"{title} {description}"

    matched_fields = text_matches(
        combined,
        criteria["target_fields"]
    )

    return matched_fields


def process_jobs():
    criteria = load_criteria()
    jobs = get_jobs()

    results = []

    for job in jobs:

        if not is_london(job):
            continue

        if not is_internship_or_placement(job, criteria):
            continue

        matched_fields = is_relevant_field(job, criteria)

        if not matched_fields:
            continue

        results.append({
            "company": job.get("company_name", ""),
            "role": job.get("title", ""),
            "location": job.get("location", ""),
            "posted_date": job.get("created_at", ""),
            "deadline": "",
            "category": ", ".join(matched_fields),
            "match": "Potential match",
            "application_url": job.get("url", ""),
            "source": "Arbeitnow",
            "status": "🆕 New",
            "notes": ""
        })

    return results


if __name__ == "__main__":
    jobs = process_jobs()

    print(f"Found {len(jobs)} potential matches.")

    for job in jobs[:20]:
        print(
            f"{job['company']} | "
            f"{job['role']} | "
            f"{job['location']}"
        )
