import unittest

jazz_feed = __import__('jazz_feed')
latest_shows_scraper = __import__('latest_shows_scraper')


class TestFunction(unittest.TestCase):
  def test_jazz_feed(self):
    result = jazz_feed.GetJazzFeed(atom_file="feeds/jazz_89_7_latest_atom.xml", rss_file="feeds/jazz_89_7_latest_rss.xml")
    self.assertTrue(result)
    # todo, make sure atom and rss files have been saved

if __name__ == '__main__':
    unittest.main()