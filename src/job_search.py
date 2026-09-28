import json
import os
import requests


API_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1"


def load_criteria():
    with open("config/criteria.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_jobs():
    response = requests.get(
        API_URL,
        params={
            "app_id": os.environ["ADZUNA_APP_ID"],
            "app_key": os.environ["ADZUNA_APP_KEY"],
            "results_per_page": 50,
            "where": "London",
            "what": "internship placement",
            "content-type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json().get("results", [])


def is_relevant(job, criteria):
    title = str(job.get("title", "")).lower()
    description = str(job.get("description", "")).lower()

    text = f"{title} {description}"

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

    has_target_field = any(term in text for term in target_fields)
    has_unwanted_field = any(term in text for term in unwanted_fields)
    has_internship = any(term in text for term in internship_terms)
    has_excluded_role = any(term in text for term in excluded_roles)

    return (
        has_target_field
        and has_internship
        and not has_unwanted_field
        and not has_excluded_role
    )


def process_jobs():
    criteria = load_criteria()
    jobs = get_jobs()

    results = []

    for job in jobs:
        if not is_relevant(job, criteria):
            continue

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
