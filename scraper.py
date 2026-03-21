import requests
from bs4 import BeautifulSoup
import time
import random

# Add or edit these to target the roles you care about
SEARCH_QUERIES = [
    "hiring founder's office bangalore",
    "hiring founder's office delhi",
    "hiring chief of staff india startup",
    "hiring growth manager india startup",
    "founder office intern india",
    "hiring EIR india startup",
    "hiring strategy ops india startup",
    "hiring category manager india startup",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
}


def search_linkedin_posts(query: str) -> list[dict]:
    """
    Uses Google to find LinkedIn posts matching the query.
    Returns list of {url, snippet} dicts.
    """
    google_query = f'site:linkedin.com/posts {query}'
    url = f"https://www.google.com/search?q={requests.utils.quote(google_query)}&num=20&hl=en"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [!] Google search failed for '{query}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    posts = []

    for result in soup.select("div.g"):
        link_el = result.select_one("a")
        snippet_el = result.select_one("div.VwiC3b")

        if not link_el:
            continue

        href = link_el.get("href", "")
        if "linkedin.com/posts" not in href:
            continue

        snippet = snippet_el.get_text(separator=" ", strip=True) if snippet_el else ""
        if len(snippet) < 40:
            continue

        posts.append({"url": href, "content": snippet})

    return posts


def scrape_all() -> list[dict]:
    """
    Runs all search queries and returns a de-duplicated list of posts.
    """
    all_posts = []
    seen_urls = set()

    for i, query in enumerate(SEARCH_QUERIES):
        print(f"  Searching ({i+1}/{len(SEARCH_QUERIES)}): {query}")
        posts = search_linkedin_posts(query)

        for post in posts:
            if post["url"] not in seen_urls:
                seen_urls.add(post["url"])
                all_posts.append(post)

        # Polite delay between requests so Google doesn't block us
        if i < len(SEARCH_QUERIES) - 1:
            time.sleep(random.uniform(3, 6))

    print(f"  Total unique posts found: {len(all_posts)}")
    return all_posts
