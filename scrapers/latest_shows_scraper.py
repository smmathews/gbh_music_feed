import requests, re
from bs4 import BeautifulSoup

shows = {
    "jazz":{
        "jazz-on-89-7":{"link":"https://www.wgbh.org/music/jazz/jazz-on-89-7","class":"LinksListItem Link"}
    }
}

def GetShowLinks(show):
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Custom user agent'})
        link = show["link"]
        #cached_text_link = "http://webcache.googleusercontent.com/search?q=cache:" + link + "&strip=1&vwsrc=0"
        clazz = show["class"]
        html_text = session.get(link).text
        soup = BeautifulSoup(html_text, 'html.parser')
        performances = []
        for performance in soup.find_all('a', attrs={"class":clazz}):
            title = performance.find('div').contents[0]
            pretty_date = title.split(": ",1)[1]
            href = performance["href"]
            performances.append({'title':title, 'href':href, 'pretty_date':pretty_date})
        return performances

def GetShowDownloads(show):
    performances = GetShowLinks(show)
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
