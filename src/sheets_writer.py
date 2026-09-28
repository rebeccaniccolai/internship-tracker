import os
import json

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet():
    credentials_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open("Internship Tracker")
    return spreadsheet.worksheet("Internships")


def add_jobs(jobs):
    worksheet = get_sheet()

    existing_urls = set(
        worksheet.col_values(8)[1:]
    )

    new_jobs = []

    for job in jobs:
        application_url = job["application_url"]

        if not application_url:
            continue

        if application_url in existing_urls:
            continue

        row = [
            job["company"],
            job["role"],
            job["location"],
            job["posted_date"],
            job["deadline"],
            job["category"],
            job["match"],
            application_url,
            job["source"],
            job["status"],
            job["date_added"],
            job["notes"],
        ]

        worksheet.append_row(row)

        existing_urls.add(application_url)
        new_jobs.append(job)

    return new_jobs
