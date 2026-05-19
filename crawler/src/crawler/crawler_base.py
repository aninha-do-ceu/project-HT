# ---------------------------------------- #

# Base dos crawlers usados para extrair notícias

# ---------------------------------------- #

from typing import Optional
import requests
from bs4 import BeautifulSoup
import re
import time

from extractors.extractor import Extractor

class CrawlerBase:
    """
    Base para os crawlers dos portais de notícias.
    Métodos:
        fetch
        parse
        get_max_search_pages_number_portal
        get_html_search_pages
    """
    def __init__(self):
        self.extractor = Extractor()

    def fetch(self, url: str):
        """
        Faz requisição HTTP e retorna o HTML
        parametros:
            url: url da notícia analisada
        return:
            conteúdo HTML da página
        """
        req = requests.get(url)
        if req.status_code == 200:
            print('Request Successful!')
            content = req.content
        else:
            print('Request Failed!')
            content = None
        return content

    def parse(self, content: str):
        """
        Analisa o conteúdo HTML e o estrutura
        parametros:
            content: conteúdo HTML da página
        return:
            título da página e conteúdo HTML da página estruturado
        """
        soup = BeautifulSoup(content, 'html.parser')
        return soup

    def get_max_search_pages_number_portal(self, portals: dict):
        """
        A partir do conteúdo HTML de uma página de busca por um termo
        retorna o número máximo de páginas com a busca
        parametros:
            portals: dicionário onde cada chave refere-se a um portal
            de notícias e o valor é um link template para busca (que muda conforme portal)
            terms: termos a serem buscados
        return:
            dict onde a chave são os portais e cada valor é um dict com chave sendo
            o termo buscado e o valor o número máximo de páginas de busca
        """
        dict_max_url = {}

        for portal, terms in portals.items():
            list_max_url = {}
            for term in terms:
                print(portals[portal][term])
                content_search = self.fetch(portals[portal][term])
                html_content_search = self.parse(content_search)

                num_url_max = self.extractor.extract_page_search_numbers(html = html_content_search)

                list_max_url[term] = num_url_max
                time.sleep(10)

            dict_max_url[portal] = list_max_url

        return dict_max_url

    def get_html_search_pages(self, portals: dict, dict_max_url: dict, url_max_opt: Optional[int] = None, url_max_force: Optional[bool] = False):
        """
        Salva a estrutura HTML das páginas de busca em
        um dicionário onde a chave é o portal de notícias
        e o valor uma lista que contém a estrutura HTML
        de cada página de busca
        parametros:
            portals: dicionário onde cada chave refere-se a um portal
            de notícias e o valor é um link template para busca (que muda conforme portal)
            dict_max_url: dicionário onde cada chave refere-se a um portal
            de notícias e o valor é um dicionário com termos buscados como chave
            e valor o número máximo de páginas de busca presentes referentes
            ao termo
            url_max_opt: inteiro que define o número máximo de páginas a serem
            acessadas. Por padrão, determina-se o número de páginas para determinado
            termo e portal a partir do dicionário dict_max_url.
            url_max_force: booleano que indica se o máximo de páginas
            automaticamente detectado deve ser ignorado.
        return:
            dicionário onde chave é o portal de notícias
            e valor é uma lista que contém a estrutura HTML
        de cada página de busca
        """
        dict_list_html_content_search = {portal: [] for portal in portals.keys()}

        for portal, url_terms in portals.items():
            for term, url in url_terms.items():
                if url_max_opt is None:
                    url_max = dict_max_url[portal][term]
                elif (not url_max_force) and url_max_opt > dict_max_url[portal][term]:
                    url_max = dict_max_url[portal][term]
                else:
                    url_max = url_max_opt
                url = portals[portal][term]
                for i in range(1, int(url_max)+1):
                    print(f'Acessando pagina de busca do portal {portal} com termo {term} de número {i}')
                    if re.search(r'/pagina/(\d+)/', url):
                        url_search = re.sub(r'pagina/\d+/', f'pagina/{i}/', url)
                    elif re.search(r'/page/(\d+)/', url):
                        url_search = re.sub(r'page/\d+/', f'page/{i}/', url)
                    elif re.search(r'page=\d+', url):
                        url_search = re.sub(r'page=\d+', f'page={i}', url)
                    if url_search:
                        content_search = self.fetch(url_search)
                        content_search = self.parse(content_search)
                        dict_list_html_content_search[portal].append(content_search)
                    time.sleep(5)

        return dict_list_html_content_search





