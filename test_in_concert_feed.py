import unittest
import in_concert_feed


class TestFunction(unittest.TestCase):
    def test_in_concert_feed(self):
        result = in_concert_feed.get_in_concert_feed(atom_file="feeds/in_concert_latest_atom.xml", rss_file="feeds/in_concert_latest_rss.xml")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
