from pathlib import Path


def write_feed(fg, rss_file=None, atom_file=None):
    """Write feed to RSS/ATOM files and return ATOM string."""
    if atom_file:
        Path(atom_file).parent.mkdir(exist_ok=True, parents=True)
        fg.atom_file(atom_file)
    if rss_file:
        Path(rss_file).parent.mkdir(exist_ok=True, parents=True)
        fg.rss_file(rss_file)
    return fg.atom_str(pretty=True)


def add_entries(fg, downloads):
    """Add episode entries to a feed from a list of download dicts.

    Recognized keys: href, title, download, and optionally published
    (datetime) and summary (str), which become pubDate/description in RSS.
    """
    for download in downloads:
        # append (not feedgen's default prepend) so entries appear in the
        # order given — the scrapers return newest-first
        fe = fg.add_entry(order='append')
        fe.id(download["href"])
        fe.link(href=download["href"])
        fe.title(download["title"])
        fe.enclosure(download["download"], 0, 'audio/mpeg')
        if download.get("published"):
            fe.published(download["published"])
        if download.get("summary"):
            fe.summary(download["summary"])
