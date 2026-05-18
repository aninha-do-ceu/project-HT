# ---------------------------------------- #

# Classe do extrator de informações

# ---------------------------------------- #

from bs4 import BeautifulSoup
import re
from crawler import config as crawler_config

class Extractor:
    """
    Base para a extração de dados
    Métodos:
        extract_page_search_numbers
        recognize_link
        extract_links
    """

    def __init__(self):
        pass

    def extract_page_search_numbers(self, html: BeautifulSoup):
        num_url_max = 1
        for a in html.find_all("a", href=True):
            match1 = re.search(r'/pagina/(\d+)/', a.get("href"))
            match2 = re.search(r'/page/(\d+)/', a.get("href"))
            if match1:
                if int(match1.group(1)) >= int(num_url_max):
                    num_url_max = int(match1.group(1)) + 1
            elif match2:
                if int(match2.group(1)) >= int(num_url_max):
                    num_url_max = int(match2.group(1)) + 1

        return num_url_max


    def recognize_link(self, html: str, portal_template: str):
        pattern = re.compile(
            fr'<a[^>]*href="(?P<url>{portal_template}/[^"]*)"[^>]*>'
            r'.*?<h2[^>]*>(?P<title>.*?)</h2>.*?</a>',
            re.DOTALL
        )
        matches = pattern.findall(str(html))
        return matches

    def extract_links(self, dict_html: dict, portals_template: dict):
        list_urls = []
        for portal, list_html_search in dict_html.items():
            for html_search in list_html_search:
                if portal == 'cnn':
                    links = html_search.find_all(class_=crawler_config.portals_div_urls[portal][1])
                    for link in links:
                        link = link.find('a')
                        url = link.get('href')
                        title = link.get_text()
                        list_urls.append((portal, (url, title)))
                if portal == 'correiobraziliense':
                    links = html_search.find_all(class_=crawler_config.portals_div_urls[portal][1])
                    for link in links:
                        title = link.find('h2').get_text()
                        url = link.parent.parent.get('href')
                        list_urls.append((portal, (url, title)))
                if portal == 'dol':
                    links = html_search.find_all(class_=crawler_config.portals_div_urls[portal][1])
                    for link in links:
                        title = link.get_text()
                        url = portals_template[portal] + link.parent.get('href')
                        list_urls.append((portal, (url, title)))
                if portal == 'bnc_amazonas':
                    links = html_search.find_all("a", href=True)
                    for link in links:
                        # só aceitar links que sejam cards de notícia
                        if not link.find("article"):
                            continue
                        if not link.find("h2"):
                            continue
                        urls = self.recognize_link(link, portals_template[portal])

                        for url in urls:
                            list_urls.append((portal, url))
                else:
                    divs_links = html_search.find_all(class_=crawler_config.portals_div_urls[portal][1])
                    for link in divs_links:
                        urls = self.recognize_link(link, portals_template[portal])

                        for url in urls:
                            list_urls.append((portal, url))

        return list_urls
