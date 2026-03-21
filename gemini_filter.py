from google import genai
import json
import os
import time

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=EXTRACT_PROMPT.format(text=post_text[:3000])
        )
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        if isinstance(result, list):
            return result
        return []
    except json.JSONDecodeError as e:
        print(f"  [!] JSON parse error: {e} | Raw: {raw[:200]}")
        return []
    except Exception as e:
        print(f"  [!] Gemini error: {e}")
        return []


def filter_posts(posts: list[dict]) -> list[dict]:
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
        # Stay within free tier rate limit (15 RPM)
        time.sleep(4)
    print(f"  Total jobs extracted: {len(all_jobs)}")
    return all_jobs
