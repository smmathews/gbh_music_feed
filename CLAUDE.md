# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web scraper and podcast feed generator for GBH/WCRB radio shows. Scrapes episode metadata from radio station websites, generates RSS/ATOM feed files, and uploads them to an S3 bucket. Runs on a Raspberry Pi via cron every 4 hours.

Three feeds are generated:
- **Jazz on 89.7** (`jazz_feed.py`) — scrapes GBH site using `GetGBHDownloads`
- **WCRB In Concert** (`in_concert_feed.py`) — scrapes CRB site using `GetCRBDownloads`
- **WCRB BSO** (`bso_feed.py`) — scrapes CRB site using `GetCRBDownloads`

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

# Run tests (these hit live websites)
python3 -m unittest latest_shows_scraper.test
python3 -m unittest jazz_feed.test
python3 -m unittest in_concert_feed.test
```

## Architecture

- `latest_shows_scraper.py` — Core scraping module. Two scraping paths:
  - `GetGBHDownloads`/`GetGBHLinks`/`GetGBHShowInfo` for GBH-hosted shows (jazz)
  - `GetCRBDownloads` for WCRB/classicalwcrb.org shows (in concert, BSO)
- `*_feed.py` — Each feed module creates a `FeedGenerator`, calls the appropriate scraper, builds feed entries, and writes RSS/ATOM XML files to `feeds/`.
- `feeds/` — Output directory for generated XML files, synced to S3 bucket `gbh-feed`.

Feed generators can be called as functions (with optional file path args) or run as standalone scripts. The scraper uses `__import__('latest_shows_scraper')` for module loading.

## Key Details

- GBH scraper looks for download URLs matching `.*cdn.*mp3` in `data-stream-url` attributes, with a fallback from `<button>` to `<ps-stream-url>` elements.
- CRB scraper finds `<ps-promo>` elements with `data-content-type="episodic-radio-episode"` and extracts `audio/mpeg` stream URLs.
- Tests are integration tests that make real HTTP requests to the radio station websites — they will fail if the sites are down or change structure.
