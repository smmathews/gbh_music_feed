from feedgen.feed import FeedGenerator
import latest_shows_scraper
from feed_utils import add_entries, write_feed


def get_jazz_feed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    info = latest_shows_scraper.get_gbh_show_info(link)
    fg.logo(info["image"])
    fg.title(info["title"])
    fg.language('en')
    fg.description("Feed is not affiliated with GBH in any way. All content is copyright GBH, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/radio-pledge to support the shows you love.")

    add_entries(fg, latest_shows_scraper.get_gbh_downloads(link))
    return write_feed(fg, rss_file=rss_file, atom_file=atom_file)


if __name__ == '__main__':
    get_jazz_feed(atom_file="feeds/jazz_89_7_latest_atom.xml", rss_file="feeds/jazz_89_7_latest_rss.xml")
