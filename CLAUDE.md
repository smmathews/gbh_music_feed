# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web scraper and podcast feed generator for GBH/WCRB radio shows. Scrapes episode metadata from radio station websites, generates RSS/ATOM feed files, and uploads them to an S3 bucket. Runs on a Raspberry Pi via cron every 4 hours.

Three feeds are generated:
- **Jazz on 89.7** (`jazz_feed.py`) — scrapes GBH site using `get_gbh_downloads`
- **WCRB In Concert** (`in_concert_feed.py`) — scrapes CRB site using `get_crb_downloads`
- **WCRB BSO** (`bso_feed.py`) — scrapes CRB site using `get_crb_downloads`

Two combined feeds are also generated (`combined_feed.py`):
- **GBH Music: All Shows** (`all_gbh_music`) — jazz + in concert + BSO
- **WCRB Classical: All Shows** (`all_classical`) — in concert + BSO

## Commands

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run individual feed generators
python3 jazz_feed.py
python3 in_concert_feed.py
python3 bso_feed.py

# Run all feeds and upload to S3
./runAndUpload.sh

# Run all tests (these hit live websites)
python3 -m unittest discover

# Run individual tests
python3 -m unittest test_latest_shows_scraper
python3 -m unittest test_jazz_feed
python3 -m unittest test_in_concert_feed
```

## Architecture

- `latest_shows_scraper.py` — Core scraping module. Two scraping paths:
  - `get_gbh_downloads`/`get_gbh_links`/`get_gbh_show_info` for GBH-hosted shows (jazz)
  - `get_crb_downloads` for WCRB/classicalwcrb.org shows (in concert, BSO)
- `feed_utils.py` — Shared helpers (`write_feed`, `add_entries`) used by all feed modules.
- `*_feed.py` — Each feed module creates a `FeedGenerator`, calls the appropriate scraper, builds feed entries, and writes RSS/ATOM XML files to `feeds/`.
- `feeds/` — Output directory for generated XML files, synced to S3 bucket `gbh-feed`.

Feed generators can be called as functions (with optional file path args) or run as standalone scripts.

## Key Details

- GBH scraper looks for download URLs matching `.*cdn.*mp3` in `data-stream-url` attributes, with a fallback from `<button>` to `<ps-stream-url>` elements.
- CRB scraper finds `<ps-promo>` elements with `data-content-type="episodic-radio-episode"` and extracts `audio/mpeg` stream URLs, plus each promo's `PromoA-timestamp`/`PromoA-description` for the entry date and description.
- Tests are integration tests that make real HTTP requests to the radio station websites — they will fail if the sites are down or change structure. `test_scraper_offline.py` covers parsing with canned HTML and runs offline.
