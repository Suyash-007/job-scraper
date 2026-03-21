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
    "Location",
    "Experience",
    "Job Type",
    "CTC",
    "Source URL",
]


def get_sheet():
    """
    Authenticates with Google Sheets using a service account key
    stored as the GOOGLE_CREDENTIALS env variable (JSON string).
    """
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(creds)

    sheet_id = os.environ["SHEET_ID"]
    return client.open_by_key(sheet_id).sheet1


def ensure_headers(sheet):
    """
    Adds the header row if the sheet is empty.
    """
    first_row = sheet.row_values(1)
    if not first_row:
        sheet.append_row(SHEET_HEADERS, value_input_option="RAW")
        print("  Headers added to sheet.")


def get_existing_urls(sheet) -> set:
    """
    Returns a set of all Source URLs already in the sheet,
    used for de-duplication.
    """
    try:
        records = sheet.get_all_records()
        return {str(r.get("Source URL", "")).strip() for r in records}
    except Exception:
        return set()


def append_jobs(jobs: list[dict]) -> int:
    """
    Appends only new (not already in sheet) jobs.
    Returns count of rows added.
    """
    sheet = get_sheet()
    ensure_headers(sheet)
    existing_urls = get_existing_urls(sheet)

    today = date.today().strftime("%d %b %Y")
    new_rows = []

    for job in jobs:
        url = str(job.get("source_url", "")).strip()

        # Skip if this post URL is already in the sheet
        if url and url in existing_urls:
            continue

        new_rows.append([
            today,
            job.get("role", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("experience", ""),
            job.get("job_type", ""),
            job.get("ctc", ""),
            url,
        ])

        # Mark as seen so we don't add duplicates within the same run
        if url:
            existing_urls.add(url)

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="RAW")
        print(f"  Added {len(new_rows)} new jobs to Google Sheet.")
    else:
        print("  No new jobs to add (all already in sheet).")

    return len(new_rows)
