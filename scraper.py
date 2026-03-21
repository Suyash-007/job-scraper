import requests
import time
import random
import os

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

SEARCH_QUERIES = [
    "site:linkedin.com/posts hiring founders office bangalore",
    "site:linkedin.com/posts hiring founders office delhi",
    "site:linkedin.com/posts hiring chief of staff india startup",
    "site:linkedin.com/posts hiring growth manager india startup",
    "site:linkedin.com/posts founder office intern india",
    "site:linkedin.com/posts hiring EIR india startup",
    "site:linkedin.com/posts hiring strategy ops india startup",
    "site:linkedin.com/posts hiring category manager india startup",
]


def search_posts(query: str) -> list[dict]:
    response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        },
        json={"q": query, "num": 20, "gl": "in", "hl": "en"},
        timeout=15
    )
    response.raise_for_status()
    data = response.json()

    posts = []
    for result in data.get("organic", []):
        url = result.get("link", "")
        snippet = result.get("snippet", "").strip()
        if "linkedin.com" not in url:
            continue
        if len(snippet) < 40:
            continue
        posts.append({"url": url, "content": snippet})
        print(f"    Found: {url[:80]}")
    return posts


def scrape_all() -> list[dict]:
    all_posts = []
    seen_urls = set()

    for i, query in enumerate(SEARCH_QUERIES):
        print(f"  Searching ({i+1}/{len(SEARCH_QUERIES)}): {query}")
        try:
            posts = search_posts(query)
        except Exception as e:
            print(f"  [!] Search failed: {e}")
            posts = []

        for post in posts:
            if post["url"] not in seen_urls:
                seen_urls.add(post["url"])
                all_posts.append(post)

        if i < len(SEARCH_QUERIES) - 1:
            time.sleep(random.uniform(1, 2))

    print(f"  Total unique posts found: {len(all_posts)}")
    return all_posts
