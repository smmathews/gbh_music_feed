import unittest

in_concert_feed = __import__('in_concert_feed')


class TestFunction(unittest.TestCase):
  def test_in_concert_feed(self):
    result = in_concert_feed.GetInConcertFeed(atom_file="feeds/in_concert_latest_atom.xml", rss_file="feeds/in_concert_latest_rss.xml")
    self.assertTrue(result)
    # todo, make sure atom and rss files have been saved

if __name__ == '__main__':
    unittest.main()