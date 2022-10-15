import unittest

latest_shows_scraper = __import__('latest_shows_scraper')

class TestFunction(unittest.TestCase):
    def test_classical_in_concert(self):
        result = latest_shows_scraper.GetCRBDownloads("https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts#previous-and-on-demand-episodes")
        self.assertTrue(len(result))
        for show in result:
            self.assertTrue(show["title"])
            self.assertTrue(show["href"].startswith("https://www.classicalwcrb.org"))
            self.assertTrue(show["download"].endswith(".mp3"))
            self.assertTrue(show["logo"].endswith(".jpg"))

    def test_bso(self):
        result = latest_shows_scraper.GetCRBDownloads("https://www.classicalwcrb.org/show/the-boston-symphony-orchestra#previous-and-on-demand-broadcasts")
        self.assertTrue(len(result))
        for show in result:
            self.assertTrue(show["title"])
            self.assertTrue(show["href"].startswith("https://www.classicalwcrb.org"))
            self.assertTrue(show["download"].endswith(".mp3"))
            self.assertTrue(show["logo"].endswith(".jpg"))

    def test_jazz_89_7(self):
        result = latest_shows_scraper.GetGBHDownloads("https://www.wgbh.org/music/jazz/jazz-on-89-7")
        self.assertTrue(len(result))
        for show in result:
            self.assertIn("Jazz on 89.7", show["title"])
            self.assertTrue(show["href"].startswith("https://www.wgbh.org/jazz/"))
            self.assertTrue(show["download"].startswith("https://wgbh.brightspotcdn.com"))
            self.assertTrue(show["download"].endswith(".mp3"))

if __name__ == '__main__':
    unittest.main()