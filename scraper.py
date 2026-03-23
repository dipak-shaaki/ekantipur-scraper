from playwright.sync_api import sync_playwright
import json


def scrape_entertainment_news(page):
    """Extract top 5 articles from the entertainment section."""

    print("Navigating to entertainment page...")
    page.goto("https://ekantipur.com/entertainment")

    # Wait for articles to load
    page.wait_for_selector(".category-inner-wrapper")

    articles = []
    cards = page.query_selector_all("div.category")

    count = 0
    for card in cards:
        if count >= 5:
            break

        # Title — inside h2 > a
        title_el = card.query_selector(".category-description h2 a")
        if not title_el:
            # This is a date-separator div, skip it
            continue

        title = title_el.text_content().strip()

        # Image — try data-src first (lazy), fallback to src (already loaded)
        img_el = card.query_selector(".category-image img")
        if img_el:
            image_url = img_el.get_attribute("data-src") or img_el.get_attribute("src")
        else:
            image_url = None

        # Author — null if not found
        author_el = card.query_selector(".author-name a")
        author = author_el.text_content().strip() if author_el else None

        articles.append({
            "title": title,
            "image_url": image_url,
            "category": "मनोरञ्जन",
            "author": author
        })

        count += 1
        print(f"  Article {count}: {title[:50]}...")

    return articles


def scrape_cartoon(page):
    """Extract today's cartoon from the homepage carousel."""

    print("Navigating to homepage for cartoon...")
    page.goto("https://ekantipur.com")
    page.wait_for_load_state("networkidle")

    # Wait for the cartoon slider to appear
    page.wait_for_selector(".cartoon-slider")

    # The active slide is today's cartoon
    active_slide = page.query_selector(".cartoon-slider .swiper-slide-active")

    if not active_slide:
        print("  WARNING: Could not find active cartoon slide")
        return {"title": None, "image_url": None, "author": None}

    # Image URL is in the href of the anchor tag (full size image)
    link_el = active_slide.query_selector("a.loading-img")
    image_url = link_el.get_attribute("href") if link_el else None

    # Title and author come from the img alt text
    # alt = "कान्तिपुर दैनिकमा आज प्रकाशित अविनको कार्टुन"
    img_el = active_slide.query_selector("img")
    alt_text = img_el.get_attribute("alt") if img_el else None

    # Use the alt text as the title
    title = alt_text.strip() if alt_text else None

    # Extract author from alt text: "अविनको कार्टुन" → "अविन"
    author = None
    if alt_text and "को कार्टुन" in alt_text:
        parts = alt_text.split("को कार्टुन")
        if parts:
            author = parts[0].split()[-1]

    print(f"  Cartoon title: {title}")
    print(f"  Cartoon author: {author}")

    return {
        "title": title,
        "image_url": image_url,
        "author": author
    }


# ── Main ──────────────────────────────────────────────────────────────────────
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("=== Starting scraper ===")

    # Task 1
    entertainment = scrape_entertainment_news(page)
    print(f"✓ Got {len(entertainment)} entertainment articles\n")

    # Task 2
    cartoon = scrape_cartoon(page)
    print(f"✓ Got cartoon data\n")

    # Build output
    output = {
        "entertainment_news": entertainment,
        "cartoon_of_the_day": cartoon
    }

    # Save — ensure_ascii=False keeps Nepali text readable
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("=== Done! Saved to output.json ===")
    browser.close()