import unittest
import jazz_feed


class TestFunction(unittest.TestCase):
    def test_jazz_feed(self):
        result = jazz_feed.get_jazz_feed(atom_file="feeds/jazz_89_7_latest_atom.xml", rss_file="feeds/jazz_89_7_latest_rss.xml")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
