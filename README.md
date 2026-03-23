## Ekantipur Scraper

This project is a small Playwright-based web scraper for `ekantipur.com`. It currently extracts:

1. The top articles from the `Entertainment` section (`/entertainment`)
2. The `Cartoon of the day` from the homepage carousel (`/`)

The scraper writes the collected data to `output.json` in the project root.

## What it extracts

For each entertainment article card inside `div.category`, the scraper attempts to extract:

- `title` (text inside `.category-description h2 a`)
- `image_url` (from `.category-image img`, preferring `data-src` and falling back to `src`)
- `author` (from `.author-name a`, or `null`/`None` if missing)
- `category` (currently hard-coded to `मनोरञ्जन`)

For the cartoon of the day (homepage):

- `title` and `author` are derived from the active slide's `img alt` text
- `image_url` is extracted from the active slide link (`a.loading-img` -> `href`)

## How it works

The logic lives in `scraper.py`:

- `scrape_entertainment_news(page)`
  - Navigates to `https://ekantipur.com/entertainment`
  - Waits for `.category-inner-wrapper` to appear
  - Iterates through `page.query_selector_all("div.category")`
  - Skips nodes that do not contain a title link (`.category-description h2 a`)
  - Collects the first 5 cards

- `scrape_cartoon(page)`
  - Navigates to `https://ekantipur.com`
  - Waits for `.cartoon-slider` and selects `.swiper-slide-active`
  - Extracts image/title/author from elements within the active slide

`main.py` is just a minimal placeholder; running `scraper.py` performs the actual scraping and produces `output.json`.

## Output format

`output.json` has this structure:

- `entertainment_news`: an array of article objects
- `cartoon_of_the_day`: a single object with `title`, `image_url`, and `author`

Nepali/unicode text is preserved via `json.dump(..., ensure_ascii=False, ...)`.

## Requirements

- Python >= 3.13 (see `.python-version`)
- Playwright (declared in `pyproject.toml`)

## Run

1. Install dependencies (example):
   - `pip install -e .`
2. Run the scraper:
   - `python scraper.py`
3. Review:
   - `output.json`

