import requests, re
from bs4 import BeautifulSoup

def GetJazz897Links():
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
        link = "https://www.wgbh.org/music/jazz/jazz-on-89-7"
        clazz = "LinksListItem Link"
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('a', attrs={"class":clazz}):
            title = performance.find('div').contents[0]
            pretty_date = title.split(": ",1)[1]
            href = performance["href"]
            performances.append({'title':title, 'href':href, 'pretty_date':pretty_date})
        return performances

def GetJazz897Downloads():
    performances = GetJazz897Links()
    for performance in performances:
        with requests.Session() as session:
            session.headers.update({'User-Agent': 'Custom user agent'})
            html_text = session.get(performance["href"]).text
            soup = BeautifulSoup(html_text, 'html.parser')
            download = soup.find('button', attrs={"data-title":performance["title"]})
            if not download:
                download = soup.find('button', attrs={"data-title":re.compile('.*'+performance["pretty_date"]+'.*')})
            if download:
                performance.update({'download':download.attrs["data-src"]})
    return performances


def GetInConcertDownloads():
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
        link = "https://www.classicalwcrb.org/show/upcoming-in-concert-broadcasts#previous-and-on-demand-episodes"
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('ps-promo', attrs={"data-content-type":"episodic-radio-episode"}):
            download = performance.find('ps-stream-url', attrs={"data-stream-format":"audio/mpeg"})
            if download:
                download = download['data-stream-url']
                title = performance.find('a', attrs={"class":"Link"})['aria-label']
                href = performance.find('a', attrs={"class":"Link"})['href']
                logo = performance.find_all('source')[1]['data-srcset']
                print(logo)
                performances.append({'title':title, 'href':href, 'download':download, 'logo':logo})
        return performances
