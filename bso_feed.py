from feedgen.feed import FeedGenerator
import latest_shows_scraper
from feed_utils import add_entries, write_feed


def generate_bso_feed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    fg.title("WCRB Boston Symphony Orchestra")
    # TODO: get logo from show
    fg.subtitle(
        'CRB brings you performances, live from Symphony Hall, with host Brian McCreath, Saturdays at 8pm, with repeat broadcasts on Mondays at 8pm.')  # TODO: scrape this, in case it changes
    fg.language('en')
    fg.description(
        "Feed is not affiliated with CRB in any way. All content is copyright CRB, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/wcrb-donate to support the shows you love.")

    add_entries(fg, latest_shows_scraper.get_crb_downloads(link))
    return write_feed(fg, rss_file=rss_file, atom_file=atom_file)


if __name__ == '__main__':
    generate_bso_feed(atom_file="feeds/bso_latest_atom.xml", rss_file="feeds/bso_latest_rss.xml")
