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

    existing_rows = worksheet.get_all_values()[1:]

    existing_jobs = set()

    for row in existing_rows:
        if len(row) >= 2:
            company = row[0].strip().lower()
            role = row[1].strip().lower()

            existing_jobs.add(
                (company, role)
            )

    new_jobs = []

    for job in jobs:
        company = job["company"].strip().lower()
        role = job["role"].strip().lower()

        unique_key = (company, role)

        if unique_key in existing_jobs:
            continue

        row = [
            job["company"],
            job["role"],
            job["location"],
            job["posted_date"],
            job["deadline"],
            job["category"],
            job["match"],
            job["application_url"],
            job["source"],
            job["status"],
            job["date_added"],
            job["notes"],
        ]

        worksheet.append_row(row)

        existing_jobs.add(unique_key)
        new_jobs.append(job)

    return new_jobs
