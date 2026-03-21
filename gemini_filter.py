import google.generativeai as genai
import json
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

EXTRACT_PROMPT = """
You are a job listing extractor. Read the LinkedIn post text below and extract any job openings mentioned.

Only extract roles that match ALL of these criteria:
- Role type: Founder's Office, Chief of Staff (CoS), EIR, Growth, Operations, Strategy, Program Management, or Category Management
- Company type: Indian startup or growth-stage company
- Location: Anywhere in India (any city) or Remote

For each job found, return a JSON object with exactly these fields:
- role: job title as mentioned
- company: company name (use "Stealth startup" if unnamed)
- location: city name or "Remote"
- experience: e.g. "2-4 yrs", "Freshers", "3-6 yrs"
- job_type: "Full time" or "Intern"
- ctc: CTC or salary if mentioned, otherwise ""

Return a JSON array of these objects.
If no relevant jobs are found in the post, return exactly: []
Return ONLY valid JSON. No explanation, no markdown, no code blocks.

Post text:
{text}
"""


def extract_jobs_from_post(post_text: str) -> list[dict]:
    """
    Sends post text to Gemini and returns a list of structured job dicts.
    """
    try:
        response = model.generate_content(
            EXTRACT_PROMPT.format(text=post_text[:3000])
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini adds them anyway
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)
        if isinstance(result, list):
            return result
        return []

    except json.JSONDecodeError as e:
        print(f"  [!] JSON parse error: {e} | Raw response: {raw[:200]}")
        return []
    except Exception as e:
        print(f"  [!] Gemini error: {e}")
        return []


def filter_posts(posts: list[dict]) -> list[dict]:
    """
    Iterates over all scraped posts, runs Gemini on each,
    and returns a flat list of all extracted jobs.
    """
    all_jobs = []

    for i, post in enumerate(posts):
        content = post.get("content", "").strip()
        if len(content) < 50:
            continue

        print(f"  Extracting jobs from post {i+1}/{len(posts)}...")
        jobs = extract_jobs_from_post(content)

        for job in jobs:
            job["source_url"] = post.get("url", "")
            all_jobs.append(job)

    print(f"  Total jobs extracted: {len(all_jobs)}")
    return all_jobs
