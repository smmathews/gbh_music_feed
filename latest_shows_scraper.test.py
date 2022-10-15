import unittest

latest_shows_scraper = __import__('latest_shows_scraper')

class TestFunction(unittest.TestCase):
    def test_classical_in_concert(self):
        result = latest_shows_scraper.GetInConcertDownloads()
        self.assertTrue(len(result))
        for show in result:
            self.assertTrue(show["title"])
            self.assertTrue(show["href"].startswith("https://www.classicalwcrb.org"))
            self.assertTrue(show["download"].endswith(".mp3"))
            self.assertTrue(show["logo"].endswith(".jpg"))

    def test_jazz_89_7(self):
        result = latest_shows_scraper.GetJazz897Downloads()
        self.assertTrue(len(result))
        for show in result:
            self.assertIn("Jazz on 89.7", show["title"])
            self.assertTrue(show["href"].startswith("https://www.wgbh.org/jazz/"))
            self.assertTrue(show["download"].startswith("https://wgbh.brightspotcdn.com"))
            self.assertTrue(show["download"].endswith(".mp3"))

if __name__ == '__main__':
    unittest.main()