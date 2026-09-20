from datetime import datetime, timezone

from feedgen.feed import FeedGenerator
import latest_shows_scraper
from feed_utils import add_entries, write_feed


def generate_combined_feed(title, link, description, sources, rss_file=None, atom_file=None):
    """Combine the entries of multiple show feeds into a single feed.

    sources: list of (show_link, scraper) pairs, where scraper(show_link)
    returns a list of download dicts (as produced by latest_shows_scraper).
    Entries are de-duplicated by href and sorted newest-first.
    """
    fg = FeedGenerator()
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    fg.title(title)
    fg.language('en')
    fg.description(description)
    info = latest_shows_scraper.get_og_info(link)
    if info["image"]:
        fg.logo(info["image"])

    epoch_min = datetime.min.replace(tzinfo=timezone.utc)
    entries = {}
    for show_link, scraper in sources:
        for download in scraper(show_link):
            entries.setdefault(download["href"], download)
    merged = sorted(entries.values(),
                    key=lambda d: d.get("published") or epoch_min,
                    reverse=True)
    add_entries(fg, merged)
    return write_feed(fg, rss_file=rss_file, atom_file=atom_file)


JAZZ_LINK = "https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7"
BSO_LINK = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra"
IN_CONCERT_LINK = "https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts"


def generate_all_gbh_music_feed(rss_file=None, atom_file=None):
    link = "https://www.wgbh.org/music"
    return generate_combined_feed(
        "GBH Music: All Shows", link,
        "Every episode of GBH Music shows in one feed: GBH Music's Jazz on 89.7, "
        "WCRB In Concert, and the WCRB Boston Symphony Orchestra. Not affiliated "
        "with GBH or CRB; all content is copyright GBH/CRB. Please donate to "
        "https://donate.wgbh.org to support the shows you love.",
        [(JAZZ_LINK, latest_shows_scraper.get_gbh_downloads),
         (BSO_LINK, latest_shows_scraper.get_crb_downloads),
         (IN_CONCERT_LINK, latest_shows_scraper.get_crb_downloads)],
        rss_file=rss_file, atom_file=atom_file)


def generate_all_classical_feed(rss_file=None, atom_file=None):
    link = "https://www.classicalwcrb.org"
    return generate_combined_feed(
        "WCRB Classical: All Shows", link,
        "Every episode of WCRB classical shows in one feed: WCRB In Concert and "
        "the WCRB Boston Symphony Orchestra. Not affiliated with GBH or CRB; all "
        "content is copyright CRB. Please donate to "
        "https://donate.wgbh.org/wgbh/wcrb-donate to support the shows you love.",
        [(BSO_LINK, latest_shows_scraper.get_crb_downloads),
         (IN_CONCERT_LINK, latest_shows_scraper.get_crb_downloads)],
        rss_file=rss_file, atom_file=atom_file)


if __name__ == '__main__':
    generate_all_gbh_music_feed(atom_file="feeds/all_gbh_music_latest_atom.xml",
                                rss_file="feeds/all_gbh_music_latest_rss.xml")
    generate_all_classical_feed(atom_file="feeds/all_classical_latest_atom.xml",
                                rss_file="feeds/all_classical_latest_rss.xml")