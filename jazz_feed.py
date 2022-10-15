from pathlib import Path
from feedgen.feed import FeedGenerator

latest_shows_scraper = __import__('latest_shows_scraper')

def GetJazzFeed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    fg.id("https://www.wgbh.org/music/jazz/jazz-on-89-7")
    fg.link(href="https://www.wgbh.org/music/jazz/jazz-on-89-7")
    fg.load_extension('podcast')
    fg.title("GBH Jazz on 89.7")
    fg.logo('https://wgbh.brightspotcdn.com/2c/c4/dcae41df41c59226cc785e7740bd/wgbh-logo.svg')# GBH logo. TODO: get logo from show
    fg.subtitle('')
    fg.language('en')
    fg.description("Feed is not affiliated with GBH/WGBH in any way. All content is copyright GBH/WGBH, and should be enjoyed just as you would streaming the show directly from their website. Please donate to donate.wgbh.org for more of the shows you love.")
    
    for download in latest_shows_scraper.GetJazz897Downloads():
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
    GetJazzFeed(atom_file="feeds/jazz_89_7_latest_atom.xml", rss_file="feeds/jazz_89_7_latest_rss.xml")
    