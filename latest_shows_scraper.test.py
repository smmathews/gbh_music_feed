import unittest

latest_shows_scraper = __import__('latest_shows_scraper')

class TestFunction(unittest.TestCase):
    def test_shows(self):
        result = latest_shows_scraper.GetShowLinks(latest_shows_scraper.shows["jazz"]["jazz-on-89-7"])
        self.assertTrue(len(result))
        for show in result:
            self.assertIn("Jazz on 89.7", show["title"])
            self.assertTrue(show["href"].startswith("https://www.wgbh.org/jazz/"))

    def test_download(self):
        result = latest_shows_scraper.GetShowDownloads(latest_shows_scraper.shows["jazz"]["jazz-on-89-7"])
        self.assertTrue(len(result))
        for show in result:
            self.assertIn("Jazz on 89.7", show["title"])
            self.assertTrue(show["download"].startswith("https://wgbh.brightspotcdn.com"))
            self.assertTrue(show["download"].endswith(".mp3"))

if __name__ == '__main__':
    unittest.main()