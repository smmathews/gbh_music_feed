import requests, re
from bs4 import BeautifulSoup

def GetGBHShowInfo(link):
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
        clazz = "Image"
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        img = soup.find('img', attrs={"class":clazz})
        return {"image":img.attrs["src"], "title":img.attrs["alt"]}

def GetGBHLinks(link):
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
        clazz = "title-link"
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('a', attrs={"class":clazz}):
            title = performance.text
            pretty_date = title
            if ":" in title:
                pretty_date = title.split(": ",1)[1]
            else:
                title = "GBH Music's Jazz on 89.7: " + pretty_date
            href = performance["href"]
            performances.append({'title':title, 'href':href, 'pretty_date':pretty_date})
        return performances

def GetGBHDownloads(link):
    performances = GetGBHLinks(link)
    for performance in performances:
        with requests.Session() as session:
            session.headers.update({'User-Agent': 'Custom user agent'})
            html_text = session.get(performance["href"]).text
            soup = BeautifulSoup(html_text, 'html.parser')
            download = soup.find('button', attrs={"data-stream-url":re.compile('.*cdn.*mp3')})
            if download:
                performance.update({'download':download.attrs["data-src"]})
            else:
                download = soup.find('ps-stream-url', attrs={"data-stream-url":re.compile('.*cdn.*mp3')})
                performance.update({'download':download.attrs["data-stream-url"]})
    return performances


def GetCRBDownloads(link):
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
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
                performances.append({'title':title, 'href':href, 'download':download, 'logo':logo})
        return performances
