from google import genai
import json
import os
import time

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EXTRACT_PROMPT = """
You are a job listing extractor. Below are LinkedIn post snippets.

For each post, extract any job openings that match ALL of these criteria:
- Role type: Founder's Office, Chief of Staff (CoS), EIR, Growth, Operations, Strategy, Program Management, or Category Management
- Company type: Indian startup or growth-stage company
- Location: Anywhere in India or Remote

For each job found, return a JSON object with exactly these fields:
- role: job title as mentioned
- company: company name (use "Stealth startup" if unnamed)
- company_location: city where company is based, if mentioned
- location: job location (city or "Remote")
- experience: e.g. "2-4 yrs", "Freshers", "3-6 yrs", or "" if not mentioned
- job_type: "Full time" or "Intern"
- ctc: salary/CTC if mentioned, otherwise ""
- role_details: 1 sentence summary of what the role involves
- posted_by: name of the person who made the LinkedIn post, if identifiable from the URL or content
- source_url: the URL of the post

Return a single JSON array of all jobs found.
If no relevant jobs found, return: []
Return ONLY valid JSON. No explanation, no markdown, no code blocks.

Posts:
{posts}
"""


def filter_posts(posts: list[dict]) -> list[dict]:
    if not posts:
        return []

    all_jobs = []
    batch_size = 5
    batches = [posts[i:i+batch_size] for i in range(0, len(posts), batch_size)]

    print(f"  Processing {len(posts)} posts in {len(batches)} batches of {batch_size}...")

    for b_idx, batch in enumerate(batches):
        print(f"  Batch {b_idx+1}/{len(batches)}...")

        posts_text = ""
        for i, post in enumerate(batch):
            url = post.get("url", "")
            content = post.get("content", "")[:600]
            title = post.get("title", "")
            posts_text += f"\n[{i+1}] URL: {url}\nTitle: {title}\nContent: {content}\n"

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=EXTRACT_PROMPT.format(posts=posts_text)
            )
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)
            if isinstance(result, list):
                all_jobs.extend(result)
                print(f"    Found {len(result)} jobs in this batch")
        except json.JSONDecodeError as e:
            print(f"  [!] JSON parse error in batch {b_idx+1}: {e}")
        except Exception as e:
            print(f"  [!] Gemini error in batch {b_idx+1}: {e}")

        # Pause between batches to respect rate limits
        if b_idx < len(batches) - 1:
            time.sleep(5)

    print(f"  Total jobs extracted: {len(all_jobs)}")
    return all_jobs
