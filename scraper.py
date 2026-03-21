from duckduckgo_search import DDGS
import time
import random

SEARCH_QUERIES = [
    "site:linkedin.com/posts hiring founder's office bangalore",
    "site:linkedin.com/posts hiring founder's office delhi",
    "site:linkedin.com/posts hiring chief of staff india startup",
    "site:linkedin.com/posts hiring growth manager india startup",
    "site:linkedin.com/posts founder office intern india",
    "site:linkedin.com/posts hiring EIR india startup",
    "site:linkedin.com/posts hiring strategy ops india startup",
    "site:linkedin.com/posts hiring category manager india startup",
]


def scrape_all() -> list[dict]:
    """
    Uses DuckDuckGo to find LinkedIn posts matching job queries.
    Returns a de-duplicated list of {url, content} dicts.
    """
    all_posts = []
    seen_urls = set()

    with DDGS() as ddgs:
        for i, query in enumerate(SEARCH_QUERIES):
            print(f"  Searching ({i+1}/{len(SEARCH_QUERIES)}): {query}")

            try:
                results = list(ddgs.text(query, max_results=15))
            except Exception as e:
                print(f"  [!] Search failed for '{query}': {e}")
                results = []

            for r in results:
                url = r.get("href", "")
                snippet = r.get("body", "").strip()

                if "linkedin.com/posts" not in url:
                    continue
                if len(snippet) < 40:
                    continue
                if url in seen_urls:
                    continue

                seen_urls.add(url)
                all_posts.append({"url": url, "content": snippet})

            # Polite delay between searches
            if i < len(SEARCH_QUERIES) - 1:
                time.sleep(random.uniform(2, 4))

    print(f"  Total unique posts found: {len(all_posts)}")
    return all_posts
