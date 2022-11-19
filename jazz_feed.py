from pathlib import Path
from feedgen.feed import FeedGenerator

latest_shows_scraper = __import__('latest_shows_scraper')

def GetJazzFeed(rss_file=None, atom_file=None):
    fg = FeedGenerator()
    link = "https://www.wgbh.org/music/jazz/jazz-on-89-7"
    fg.id(link)
    fg.link(href=link)
    fg.load_extension('podcast')
    info = latest_shows_scraper.GetGBHShowInfo(link)
    fg.logo(info["image"])
    fg.title(info["title"])
    fg.language('en')
    fg.description("Feed is not affiliated with GBH in any way. All content is copyright GBH, and should be enjoyed just as you would streaming the show directly from their website. Please donate to https://donate.wgbh.org/wgbh/radio-pledge to support the shows you love.")
    
    for download in latest_shows_scraper.GetGBHDownloads(link):
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
    