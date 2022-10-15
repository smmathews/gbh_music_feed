# gbh_music_feed

THIS PROJECT IS NOT AFFILIATED WITH GBH/WGBH IN ANY WAY. All scraped content is copyright GBH/WGBH, and should be enjoyed just as you would streaming the show directly from their website. Please [donate to GBH](http://donate.wgbh.org) for more of the shows you love.

I got sick of only being able to access the latest GBH Jazz episodes on a browser, and would much rather use Podcast Addict to check for new episodes automatically. So I created a simple python scraper. Every four hours my raspberry pi scrapes the latest episode metadata, creates an rss and atom feed file, and pushes that file to my publically accessible s3 bucket.

If you want a public jazz feed, add this to your podcast app:
  - RSS: https://gbh-feed.s3.us-west-2.amazonaws.com/jazz_89_7_latest_rss.xml
  - ATOM: https://gbh-feed.s3.us-west-2.amazonaws.com/jazz_89_7_latest_atom.xml

If you want a public classical in-concert feed, add this to your podcast app:
  - RSS: https://gbh-feed.s3.us-west-2.amazonaws.com/in_concert_latest_rss.xml
  - ATOM: https://gbh-feed.s3.us-west-2.amazonaws.com/in_concert_latest_atom.xml

So far these are the only feeds I've tested and am actively using. I may add more in the future.
