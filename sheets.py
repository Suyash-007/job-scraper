import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import date

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_HEADERS = [
    "Date Added",
    "Role",
    "Company",
    "Company Location",
    "Job Location",
    "Experience",
    "Job Type",
    "CTC",
    "Role Details",
    "Posted By",
    "Source URL",
]


def get_sheet():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet_id = os.environ["SHEET_ID"]
    return client.open_by_key(sheet_id).sheet1


def ensure_headers(sheet):
    first_row = sheet.row_values(1)
    if not first_row:
        sheet.append_row(SHEET_HEADERS, value_input_option="RAW")
        print("  Headers added to sheet.")


def get_existing_urls(sheet) -> set:
    try:
        records = sheet.get_all_records()
        return {str(r.get("Source URL", "")).strip() for r in records}
    except Exception:
        return set()


def append_jobs(jobs: list[dict]) -> int:
    sheet = get_sheet()
    ensure_headers(sheet)
    existing_urls = get_existing_urls(sheet)

    today = date.today().strftime("%d %b %Y")
    new_rows = []

    for job in jobs:
        url = str(job.get("source_url", "")).strip()
        if url and url in existing_urls:
            continue

        new_rows.append([
            today,
            job.get("role", ""),
            job.get("company", ""),
            job.get("company_location", ""),
            job.get("location", ""),
            job.get("experience", ""),
            job.get("job_type", ""),
            job.get("ctc", ""),
            job.get("role_details", ""),
            job.get("posted_by", ""),
            url,
        ])

        if url:
            existing_urls.add(url)

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="RAW")
        print(f"  Added {len(new_rows)} new jobs to Google Sheet.")
    else:
        print("  No new jobs to add (all already in sheet).")

    return len(new_rows)
