from scraper import scrape_all
from gemini_filter import filter_posts
from sheets import append_jobs


def main():
    print("=" * 50)
    print("Job Scraper Starting")
    print("=" * 50)

    print("\n[1/3] Scraping LinkedIn posts via Google...")
    posts = scrape_all()

    if not posts:
        print("No posts found. Exiting.")
        return

    print("\n[2/3] Extracting job listings with Gemini...")
    jobs = filter_posts(posts)

    if not jobs:
        print("No relevant jobs extracted. Exiting.")
        return

    print("\n[3/3] Writing to Google Sheets...")
    count = append_jobs(jobs)

    print("\n" + "=" * 50)
    print(f"Done! {count} new jobs added to your sheet.")
    print("=" * 50)


if __name__ == "__main__":
    main()
