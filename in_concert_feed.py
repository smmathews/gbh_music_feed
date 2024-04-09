from pathlib import Path
from feedgen.feed import FeedGenerator

latest_shows_scraper = __import__('latest_shows_scraper')

def GetInConcertFeed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    fg.title("WCRB In Concert")
    # TODO: get logo from show
    fg.subtitle('In Concert captures the wealth of incredible music being performed in and around the Boston area, from the Handel and Haydn Society to A Far Cry, from the Gardner Museum to Rockport Music, and beyond. See a full list of broadcast partners here: https://www.classicalwcrb.org/in-concert-broadcast-partners.')# TODO: scrape this, in case it changes
    fg.language('en')
    fg.description("Feed is not affiliated with CRB/GBH in any way. All content is copyright CRB/GBH, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/wcrb-donate to support the shows you love.")
    
    for download in latest_shows_scraper.GetCRBDownloads(link):
        fe = fg.add_entry()
        fe.id(download["href"])
        fe.link(href=download["href"])
        fe.title(download["title"])
        fe.enclosure(download["download"], 0, 'audio/mpeg')

    if(atom_file):
        output_file = Path(atom_file)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        fg.atom_file(atom_file) # Write the ATOM feed to a file
    if(rss_file):
        output_file = Path(rss_file)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        fg.rss_file(rss_file) # Write the RSS feed to a file

    return fg.atom_str(pretty=True); # Get the ATOM feed as string


if __name__ == '__main__':
    GetInConcertFeed(atom_file="feeds/in_concert_latest_atom.xml", rss_file="feeds/in_concert_latest_rss.xml")
    