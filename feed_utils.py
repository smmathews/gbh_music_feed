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
    """Add episode entries to a feed from a list of download dicts."""
    for download in downloads:
        fe = fg.add_entry()
        fe.id(download["href"])
        fe.link(href=download["href"])
        fe.title(download["title"])
        fe.enclosure(download["download"], 0, 'audio/mpeg')
