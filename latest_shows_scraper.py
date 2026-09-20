import requests, re
from bs4 import BeautifulSoup


def _create_session():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Custom user agent'})
    return session


def get_gbh_show_info(link):
    with _create_session() as session:
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        img = soup.find('img', attrs={"class": "Image"})
        # The show logo is lazy-loaded: `src` is a placeholder data URI and the
        # real image URL lives in `data-src`. The show title comes from the
        # og:title meta tag; the img `alt` is now a bare file name, not a title.
        title_tag = soup.find('meta', attrs={"property": "og:title"})
        return {
            "image": img.attrs.get("data-src") or img.attrs["src"],
            "title": title_tag.attrs["content"] if title_tag else img.attrs["alt"],
        }


def get_gbh_links(link):
    with _create_session() as session:
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        # Episode promos link to detail pages like /shows/<show>/<episode>.
        # The old "title-link" class no longer exists; links are now a.Link
        # anchors. Filter on the href shape so nav links (e.g. /tv-shows) and
        # the show's own landing-page link are excluded, while episodes that
        # GBH cross-links from classical-crb-app-content are still included.
        for performance in soup.find_all('a', attrs={"class": "Link", "href": re.compile(r'/shows/[^/]+/.+')}):
            title = performance.text
            pretty_date = title
            if ": " in title:
                pretty_date = title.split(": ", 1)[1]
            else:
                title = "GBH Music's Jazz on 89.7: " + pretty_date
            href = performance["href"]
            performances.append({'title': title, 'href': href, 'pretty_date': pretty_date})
        return performances


def get_gbh_downloads(link):
    performances = get_gbh_links(link)
    with _create_session() as session:
        for performance in performances:
            html_text = session.get(performance["href"]).text
            soup = BeautifulSoup(html_text, 'html.parser')
            download = soup.find('button', attrs={"data-stream-url": re.compile('.*cdn.*mp3')})
            if download:
                # Read the attribute that was actually matched; a button may
                # only carry data-stream-url, and data-src is not guaranteed.
                performance.update({'download': download.attrs["data-stream-url"]})
            else:
                download = soup.find('ps-stream-url', attrs={"data-stream-url": re.compile('.*cdn.*mp3')})
                if download:
                    performance.update({'download': download.attrs["data-stream-url"]})
                else:
                    performance.update({'download': False})
    return [item for item in performances if item['download']]


def get_crb_downloads(link):
    with _create_session() as session:
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('ps-promo', attrs={"data-content-type": "episodic-radio-episode"}):
            download = performance.find('ps-stream-url', attrs={"data-stream-format": "audio/mpeg"})
            if download:
                download = download.attrs["data-stream-url"]
                title = performance.find('a', attrs={"class": "Link"})['aria-label']
                href = performance.find('a', attrs={"class": "Link"})['href']
                performances.append({'title': title, 'href': href, 'download': download})
        return performances
