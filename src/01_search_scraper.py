import asyncio
import re
import os
from playwright.async_api import async_playwright

# Primary keywords for search
KEYWORDS = ["wlw", "le", "la", "陈乐", "les", "百合", "lesbian"]

# Keywords that require deeper scrolling (more results)
DEPTH_KEYWORDS = ["le", "wlw", "百合"]

# Output file for storing collected URLs
OUTPUT_FILE = "urls.txt"


async def search_incremental():
    """
    Incrementally search Douyin for video URLs using keyword queries.

    - Avoids duplicates by checking against an existing URL list
    - Intercepts network responses to extract video IDs
    - Saves only new video URLs
    """

    # Load existing URLs for deduplication
    existing_urls = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_urls = {line.strip() for line in f if line.strip()}

    print(f"[INFO] Loaded {len(existing_urls)} existing URLs. Duplicates will be skipped.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/110.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        new_urls = set()

        async def handle_response(response):
            """
            Intercept Douyin search-related network responses
            and extract aweme_id values as video URLs.
            """
            if "search/item" in response.url or "aweme/v1" in response.url:
                try:
                    text = await response.text()
                    ids = re.findall(r'"aweme_id":"(\d+)"', text)

                    for vid in ids:
                        url = f"https://www.douyin.com/video/{vid}"
                        if url not in existing_urls and url not in new_urls:
                            print(f"[NEW] Found new video: {url}")
                            new_urls.add(url)

                except Exception:
                    pass

        page.on("response", handle_response)

        # Step 1: Manual login
        print("[INFO] Opening Douyin homepage...")
        await page.goto("https://www.douyin.com/")

        print("\n[IMPORTANT] Please scan the QR code to log in.")
        print("After logging in successfully, return here and press ENTER.")
        await asyncio.to_thread(input)

        # Step 2: Incremental keyword search
        for kw in KEYWORDS:
            scroll_times = 25 if kw in DEPTH_KEYWORDS else 10
            print(f"[SEARCH] Keyword: '{kw}' | Scrolls: {scroll_times}")

            await page.goto(f"https://www.douyin.com/search/{kw}")

            for i in range(1, scroll_times + 1):
                print(f"   [SCROLL] {kw}: {i}/{scroll_times}")
                await page.evaluate("window.scrollBy(0, 3000)")
                await asyncio.sleep(2.5)

        # Step 3: Save new URLs
        if new_urls:
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                for url in new_urls:
                    f.write(url + "\n")

            total = len(existing_urls) + len(new_urls)
            print(f"\n[SUCCESS] Added {len(new_urls)} new URLs. Total: {total}")
        else:
            print("\n[INFO] No new videos found outside the existing dataset.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(search_incremental())
