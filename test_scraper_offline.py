"""Offline unit tests for latest_shows_scraper.

These pin the parsing behavior with canned HTML (no network), so they catch
regressions in the scrapers even when the live sites are unreachable.
"""
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import combined_feed
import latest_shows_scraper


FAKE_LOGO_DATA_URI = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg=="
FAKE_LOGO_URL = "https://cdn.grove.wgbh.org/dims4/logo/300x300/logo.png"
SHOW_URL = "https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7"


def show_page(anchors_html):
    """Minimal GBH show page: lazy-loaded show image + episode promo links."""
    return (
        '<html><head><meta property="og:title" content="GBH Music\'s Jazz on 89.7"></head>'
        '<body>'
        f'<img class="Image" alt="GBHMusic_Jazz897_Web_1080x1080_v5.png" loading="lazy" '
        f'src="{FAKE_LOGO_DATA_URI}" data-src="{FAKE_LOGO_URL}">'
        + "".join(anchors_html)
        + '</body></html>'
    )


def episode_anchor(href, text):
    return f'<div class="promo-title"><a class="Link" href="{href}">{text}</a></div>'


def fake_session(pages):
    """Build a fake requests.Session whose GETs return canned HTML pages."""

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeSession:
        def __init__(self):
            self.headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            if url not in pages:
                raise KeyError(f"unexpected URL: {url}")
            return FakeResponse(pages[url])

    return FakeSession


def patched(pages):
    return patch.object(latest_shows_scraper, '_create_session', lambda: fake_session(pages)())


class TestGetGbhLinks(unittest.TestCase):
    def test_uses_current_promo_markup(self):
        """Episode links are a.Link anchors under /shows/<show>/<episode>."""
        html = (
            '<html><body>'
            '<a class="Link" href="https://www.wgbh.org/tv-shows/gbh-channel-2">Watch Live</a>'
            '<a class="Link" href="https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7">GBH Music\'s Jazz on 89.7</a>'
            '<div class="promo-title"><a class="Link" '
            'href="https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/gbh-musics-jazz-on-89-7-sunday-september-13-2026">'
            'GBH Music\'s Jazz on 89.7: Sunday, September 13, 2026</a></div>'
            '<div class="promo-title"><a class="Link" '
            'href="https://www.wgbh.org/shows/classical-crb-app-content/crb-episode">'
            'GBH Music\'s Jazz on 89.7: Friday, September 11, 2026</a></div>'
            '</body></html>'
        )
        with patched({SHOW_URL: html}):
            performances = latest_shows_scraper.get_gbh_links(SHOW_URL)
        self.assertEqual(len(performances), 2)
        self.assertEqual(performances[0]['title'], "GBH Music's Jazz on 89.7: Sunday, September 13, 2026")
        self.assertEqual(performances[0]['pretty_date'], "Sunday, September 13, 2026")
        self.assertEqual(
            performances[0]['href'],
            "https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/gbh-musics-jazz-on-89-7-sunday-september-13-2026")
        # Cross-linked episodes from classical-crb-app-content are still kept.
        self.assertEqual(
            performances[1]['href'],
            "https://www.wgbh.org/shows/classical-crb-app-content/crb-episode")

    def test_colon_without_space_does_not_crash(self):
        """Regression: a title containing ':' but not ': ' must not raise IndexError."""
        html = show_page([
            episode_anchor("https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/episode-sept",
                           "Episode:Sept 5")
        ])
        with patched({SHOW_URL: html}):
            performances = latest_shows_scraper.get_gbh_links(SHOW_URL)
        self.assertEqual(len(performances), 1)
        self.assertEqual(performances[0]['title'], "GBH Music's Jazz on 89.7: Episode:Sept 5")
        self.assertEqual(performances[0]['pretty_date'], "Episode:Sept 5")


class TestGetGbhShowInfo(unittest.TestCase):
    def test_uses_lazy_loaded_image_and_og_title(self):
        """Regression: the logo is lazy-loaded (src is a placeholder data URI)
        and the img alt text is a bare file name, so use data-src and og:title."""
        html = (
            '<html><head><meta property="og:title" content="GBH Music\'s Jazz on 89.7"></head>'
            '<body><img class="Image" alt="GBHMusic_Jazz897_Web_1080x1080_v5.png" loading="lazy" '
            f'src="{FAKE_LOGO_DATA_URI}" data-src="{FAKE_LOGO_URL}"></body></html>'
        )
        with patched({SHOW_URL: html}):
            info = latest_shows_scraper.get_gbh_show_info(SHOW_URL)
        self.assertEqual(info, {"image": FAKE_LOGO_URL, "title": "GBH Music's Jazz on 89.7"})

    def test_falls_back_to_src_and_alt(self):
        html = (
            '<html><body><img class="Image" alt="Show title" src="https://cdn.example.com/logo.png">'
            '</body></html>'
        )
        with patched({SHOW_URL: html}):
            info = latest_shows_scraper.get_gbh_show_info(SHOW_URL)
        self.assertEqual(info, {"image": "https://cdn.example.com/logo.png", "title": "Show title"})


class TestGetGbhDownloads(unittest.TestCase):
    def _run(self, pages):
        with patched(pages):
            return latest_shows_scraper.get_gbh_downloads(SHOW_URL)

    def test_button_download_reads_data_stream_url(self):
        """Regression: the button branch matched on data-stream-url but read
        data-src, raising KeyError when data-src was absent."""
        episode_a = 'https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/episode-a'
        episode_b = 'https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/episode-b'
        episode_c = 'https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/episode-c'
        html = show_page([
            episode_anchor(episode_a, "GBH Music's Jazz on 89.7: Episode A"),
            episode_anchor(episode_b, "GBH Music's Jazz on 89.7: Episode B"),
            episode_anchor(episode_c, "GBH Music's Jazz on 89.7: Episode C"),
        ])
        page_a = ('<html><body><button data-stream-url="https://cdn.example.com/a.mp3">'
                  '<span>Play</span></button></body></html>')
        page_b = ('<html><body><ps-stream-url data-stream-format="audio/mpeg" '
                  'data-stream-url="https://cdn.example.com/b.mp3"></ps-stream-url></body></html>')
        page_c = '<html><body><p>no audio here</p></body></html>'
        result = self._run({SHOW_URL: html, episode_a: page_a, episode_b: page_b, episode_c: page_c})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['download'], 'https://cdn.example.com/a.mp3')
        self.assertEqual(result[1]['download'], 'https://cdn.example.com/b.mp3')

    def test_skips_non_cdn_stream_urls(self):
        """Only cdn-hosted mp3s count as downloads (live streams are excluded)."""
        episode = 'https://www.wgbh.org/shows/gbh-musics-jazz-on-89-7/episode-a'
        html = show_page([episode_anchor(episode, "GBH Music's Jazz on 89.7: Episode A")])
        page = ('<html><body><ps-stream-url data-stream-format="audio/mpeg" '
                'data-stream-url="https://wgbh-live.streamguys1.com/wgbh.mp3"></ps-stream-url>'
                '</body></html>')
        result = self._run({SHOW_URL: html, episode: page})
        self.assertEqual(len(result), 0)


class TestGetCrbDownloads(unittest.TestCase):
    def test_parses_promo_and_skips_promos_without_audio(self):
        crb_url = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra"
        html = (
            '<html><body>'
            '<ps-promo data-content-type="episodic-radio-episode">'
            '<ps-stream-url data-stream-format="audio/mpeg" '
            'data-stream-url="https://cpa.ds.npr.org/s1142/audio/2025/09/bso.mp3"></ps-stream-url>'
            '<a class="Link" aria-label="Encore: Mahler’s Fourth" '
            'href="https://www.classicalwcrb.org/show/the-boston-symphony-orchestra/2025-09-09/mahler"></a>'
            '</ps-promo>'
            '<ps-promo data-content-type="episodic-radio-episode">'
            '<a class="Link" aria-label="Upcoming broadcast" '
            'href="https://www.classicalwcrb.org/show/the-boston-symphony-orchestra/2026-03-31/tanglewood"></a>'
            '</ps-promo>'
            '</body></html>'
        )
        with patched({crb_url: html}):
            performances = latest_shows_scraper.get_crb_downloads(crb_url)
        self.assertEqual(len(performances), 1)
        self.assertEqual(performances[0]['title'], 'Encore: Mahler’s Fourth')
        self.assertEqual(performances[0]['download'], 'https://cpa.ds.npr.org/s1142/audio/2025/09/bso.mp3')

    def test_extracts_timestamp_and_description(self):
        """Issue #3: PromoA-timestamp / PromoA-description become the entry's
        published datetime and summary."""
        crb_url = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra"
        html = (
            '<html><body>'
            '<ps-promo data-content-type="episodic-radio-episode">'
            '<ps-stream-url data-stream-format="audio/mpeg" '
            'data-stream-url="https://cpa.ds.npr.org/s1142/audio/2025/09/bso.mp3"></ps-stream-url>'
            '<a class="Link" aria-label="Encore: Mahler’s Fourth" '
            'href="https://www.classicalwcrb.org/show/the-boston-symphony-orchestra/2025-09-09/mahler"></a>'
            '<div class="PromoA-date"><div class="PromoA-timestamp" '
            'data-date="September 12, 2026 at 8:00 PM EDT" '
            'data-promo-date="September 12, 2026" data-timestamp="1789257600000"></div></div>'
            '<div class="PromoA-description">'
            '  In an encore broadcast, Andris Nelsons leads the BSO in Mahler’s Fourth. '
            '</div>'
            '</ps-promo>'
            '<ps-promo data-content-type="episodic-radio-episode">'
            '<ps-stream-url data-stream-format="audio/mpeg" '
            'data-stream-url="https://cpa.ds.npr.org/s1142/audio/2025/09/other.mp3"></ps-stream-url>'
            '<a class="Link" aria-label="No metadata promo" '
            'href="https://www.classicalwcrb.org/show/the-boston-symphony-orchestra/2025-09-10/other"></a>'
            '</ps-promo>'
            '</body></html>'
        )
        with patched({crb_url: html}):
            performances = latest_shows_scraper.get_crb_downloads(crb_url)
        self.assertEqual(len(performances), 2)
        # 1789257600000 ms == 2026-09-13 00:00 UTC == Sept 12, 2026 8:00 PM EDT
        self.assertEqual(performances[0]['published'],
                         datetime(2026, 9, 13, tzinfo=timezone.utc))
        self.assertEqual(
            performances[0]['summary'],
            'In an encore broadcast, Andris Nelsons leads the BSO in Mahler’s Fourth.')
        # Promos without timestamp/description simply lack the keys.
        self.assertNotIn('published', performances[1])
        self.assertNotIn('summary', performances[1])


class TestGetCrbShowInfo(unittest.TestCase):
    def test_uses_og_image_and_og_title(self):
        """Issue #2: CRB feeds need a per-show logo; og:image provides one."""
        crb_url = "https://www.classicalwcrb.org/show/the-boston-symphony-orchestra"
        html = (
            '<html><head>'
            '<meta property="og:image" content="https://cdn.example.com/bso-banner.png">'
            '<meta property="og:title" content="The Boston Symphony Orchestra">'
            '</head><body></body></html>'
        )
        with patched({crb_url: html}):
            info = latest_shows_scraper.get_crb_show_info(crb_url)
        self.assertEqual(info, {"image": "https://cdn.example.com/bso-banner.png",
                                "title": "The Boston Symphony Orchestra"})

    def test_falls_back_to_promo_photo_without_og_image(self):
        """Issue #2: the In Concert page has no og:image; fall back to the
        featured episode's promo photo."""
        crb_url = "https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts"
        html = (
            '<html><head><meta property="og:title" content="In Concert"></head><body>'
            '<ps-promo data-content-type="episodic-radio-episode">'
            '<img class="Image" alt="Ensemble photo" '
            'src="https://cdn.example.com/promo-photo.png">'
            '</ps-promo>'
            '</body></html>'
        )
        with patched({crb_url: html}):
            info = latest_shows_scraper.get_crb_show_info(crb_url)
        self.assertEqual(info["image"], "https://cdn.example.com/promo-photo.png")
        self.assertEqual(info["title"], "In Concert")

    def test_get_og_info_reads_any_page(self):
        url = "https://www.wgbh.org/music"
        html = (
            '<html><head>'
            '<meta property="og:image" content="https://cdn.example.com/gbh-music.jpg">'
            '<meta property="og:title" content="GBH Music">'
            '</head><body></body></html>'
        )
        with patched({url: html}):
            info = latest_shows_scraper.get_og_info(url)
        self.assertEqual(info, {"image": "https://cdn.example.com/gbh-music.jpg",
                                "title": "GBH Music"})


class TestCombinedFeed(unittest.TestCase):
    def test_merges_dedupes_and_sorts_by_published(self):
        """Issue #1: entries from multiple shows merge into one feed,
        de-duplicated by href and sorted newest-first."""
        def jazz_scraper(link):
            return [{'title': 'Jazz Episode', 'href': 'https://x/jazz-1',
                     'download': 'https://cdn.example.com/jazz-1.mp3'}]

        def classical_scraper(link):
            shows = {
                'bso': ([{'title': 'Old BSO Episode', 'href': 'https://x/bso-1',
                          'download': 'https://cdn.example.com/bso-1.mp3',
                          'published': datetime(2026, 1, 1, tzinfo=timezone.utc),
                          'summary': 'An old episode'},
                         {'title': 'Duplicate', 'href': 'https://x/dup',
                          'download': 'https://cdn.example.com/dup.mp3',
                          'published': datetime(2026, 2, 1, tzinfo=timezone.utc)}]),
                'ic': ([{'title': 'New In Concert Episode', 'href': 'https://x/ic-1',
                         'download': 'https://cdn.example.com/ic-1.mp3',
                         'published': datetime(2026, 3, 1, tzinfo=timezone.utc)},
                        {'title': 'Duplicate', 'href': 'https://x/dup',
                         'download': 'https://cdn.example.com/dup.mp3',
                         'published': datetime(2026, 2, 1, tzinfo=timezone.utc)}]),
            }
            return shows['bso'] if link.endswith('/bso') else shows['ic']

        result = combined_feed.generate_combined_feed(
            "Test Combined", "https://example.com/all", "desc",
            [('https://x/bso', classical_scraper),
             ('https://x/ic', classical_scraper),
             ('https://x/jazz', jazz_scraper)],
            atom_file="/tmp/test_combined_atom.xml", rss_file="/tmp/test_combined_rss.xml")
        if isinstance(result, bytes):
            result = result.decode()
        self.assertIn('<entry>', result)
        titles = [t for t in result.split('<title>')[1:]]
        entry_titles = [t.split('</title>')[0] for t in titles[1:]]  # skip feed title
        # newest first; the duplicate href appears once
        self.assertEqual(entry_titles,
                         ['New In Concert Episode', 'Duplicate', 'Old BSO Episode', 'Jazz Episode'])

    def test_combined_feed_output_has_pubdate_and_description(self):
        """Issue #3 propagation: published/summary land in RSS pubDate and
        description."""
        def scraper(link):
            return [{'title': 'Encore: Mahler', 'href': 'https://x/mahler',
                     'download': 'https://cdn.example.com/mahler.mp3',
                     'published': datetime(2026, 9, 13, tzinfo=timezone.utc),
                     'summary': 'Nelsons conducts Mahler’s Fourth.'}]

        with patched({"https://x": (
                '<html><head><meta property="og:image" '
                'content="https://cdn.example.com/all-art.jpg"></head><body></body></html>')}):
            combined_feed.generate_combined_feed(
                "Test Combined", "https://x", "desc", [('https://x/bso', scraper)],
                rss_file="/tmp/test_combined2_rss.xml")
        import xml.etree.ElementTree as ET
        root = ET.parse('/tmp/test_combined2_rss.xml').getroot()
        item = root.find('.//item')
        self.assertEqual(item.find('pubDate').text, 'Sun, 13 Sep 2026 00:00:00 +0000')
        self.assertEqual(item.find('description').text, 'Nelsons conducts Mahler’s Fourth.')


if __name__ == '__main__':
    unittest.main()