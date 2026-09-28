import os

import requests


def send_telegram_message(message):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    response.raise_for_status()


def format_job_message(job):
    return (
        "🆕 New internship match\n\n"
        f"🏢 {job['company']}\n"
        f"💼 {job['role']}\n"
        f"📍 {job['location']}\n"
        f"🔗 {job['application_url']}"
    )


def send_new_jobs(jobs):
    for job in jobs:
        message = format_job_message(job)
        send_telegram_message(message)
