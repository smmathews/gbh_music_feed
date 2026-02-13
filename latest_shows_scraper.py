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
        return {"image": img.attrs["src"], "title": img.attrs["alt"]}


def get_gbh_links(link):
    with _create_session() as session:
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('a', attrs={"class": "title-link"}):
            title = performance.text
            pretty_date = title
            if ":" in title:
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
                performance.update({'download': download.attrs["data-src"]})
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
