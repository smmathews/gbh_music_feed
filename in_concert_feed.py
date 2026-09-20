from feedgen.feed import FeedGenerator
import latest_shows_scraper
from feed_utils import add_entries, write_feed


def get_in_concert_feed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    fg.title("WCRB In Concert")
    info = latest_shows_scraper.get_crb_show_info(link)
    if info["image"]:
        fg.logo(info["image"])
    fg.subtitle('In Concert captures the wealth of incredible music being performed in and around the Boston area, from the Handel and Haydn Society to A Far Cry, from the Gardner Museum to Rockport Music, and beyond. See a full list of broadcast partners here: https://www.classicalwcrb.org/in-concert-broadcast-partners.')  # TODO: scrape this, in case it changes
    fg.language('en')
    fg.description("Feed is not affiliated with CRB/GBH in any way. All content is copyright CRB/GBH, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/wcrb-donate to support the shows you love.")

    add_entries(fg, latest_shows_scraper.get_crb_downloads(link))
    return write_feed(fg, rss_file=rss_file, atom_file=atom_file)


if __name__ == '__main__':
    get_in_concert_feed(atom_file="feeds/in_concert_latest_atom.xml", rss_file="feeds/in_concert_latest_rss.xml")
