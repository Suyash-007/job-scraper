from duckduckgo_search import DDGS
import time
import random

SEARCH_QUERIES = [
    "hiring founder's office bangalore linkedin",
    "hiring founder's office delhi linkedin",
    "hiring chief of staff india startup linkedin",
    "hiring growth manager india startup linkedin",
    "founder office intern india linkedin",
    "hiring EIR india startup linkedin",
    "hiring strategy ops india startup linkedin",
    "hiring category manager india startup linkedin",
]


def scrape_all() -> list[dict]:
    all_posts = []
    seen_urls = set()

    with DDGS() as ddgs:
        for i, query in enumerate(SEARCH_QUERIES):
            print(f"  Searching ({i+1}/{len(SEARCH_QUERIES)}): {query}")

            try:
                results = list(ddgs.text(query, max_results=20))
            except Exception as e:
                print(f"  [!] Search failed: {e}")
                results = []

            for r in results:
                url = r.get("href", "")
                snippet = r.get("body", "").strip()

                # Accept both LinkedIn posts and LinkedIn job pages
                if "linkedin.com" not in url:
                    continue
                if len(snippet) < 40:
                    continue
                if url in seen_urls:
                    continue

                seen_urls.add(url)
                all_posts.append({"url": url, "content": snippet})
                print(f"    Found: {url[:80]}")

            if i < len(SEARCH_QUERIES) - 1:
                time.sleep(random.uniform(2, 4))

    print(f"  Total unique posts found: {len(all_posts)}")
    return all_posts
```

And update `requirements.txt` — swap `duckduckgo-search` for `ddgs`:
```
ddgs
google-genai
gspread
google-auth
