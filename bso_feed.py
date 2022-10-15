from pathlib import Path
from feedgen.feed import FeedGenerator

latest_shows_scraper = __import__('latest_shows_scraper')

def GenerateConcertFeeds(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra#previous-and-on-demand-broadcasts"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    fg.title("WCRB Boston Symphony Orchesta")
    fg.logo('https://wgbh.brightspotcdn.com/2c/c4/dcae41df41c59226cc785e7740bd/wgbh-logo.svg')# GBH logo. TODO: get logo from show
    fg.subtitle('CRB brings you performances, live from Symphony Hall, with host Brian McCreath, Saturdays at 8pm, with repeat broadcasts on Mondays at 8pm.') # TODO: scrape this, in case it changes
    fg.language('en')
    fg.description("Feed is not affiliated with CRB in any way. All content is copyright CRB, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/wcrb-donate to support the shows you love.")
    
    for download in latest_shows_scraper.GetCRBDownloads(link):
        fe = fg.add_entry()
        fe.podcast.itunes_image(download["logo"])
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
    GenerateConcertFeeds(atom_file="feeds/bso_latest_atom.xml", rss_file="feeds/bso_latest_rss.xml")
    