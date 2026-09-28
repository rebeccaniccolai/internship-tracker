import json
import requests


API_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1"


def load_criteria():
    with open("config/criteria.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_jobs():
    response = requests.get(
        API_URL,
        params={
            "app_id": __import__("os").environ["ADZUNA_APP_ID"],
            "app_key": __import__("os").environ["ADZUNA_APP_KEY"],
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
    text = (
        str(job.get("title", "")) + " " +
        str(job.get("description", ""))
    ).lower()

    fields = criteria["target_fields"]

    include_terms = criteria["role_type"]["include"]
    exclude_terms = criteria["role_type"]["exclude"]

    has_field = any(term.lower() in text for term in fields)
    has_internship = any(term.lower() in text for term in include_terms)
    has_exclusion = any(term.lower() in text for term in exclude_terms)

    return has_field and has_internship and not has_exclusion


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
