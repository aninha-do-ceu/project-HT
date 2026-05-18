from crawler.crawler_base import CrawlerBase
from crawler import config as crawler_config
from extractors.extractor import Extractor
import pandas as pd
from article.extract import batch_extract_from_url

if __name__ == '__main__':

    crawler = CrawlerBase()
    extractor = Extractor()

    # buscando o número máximo de páginas retornadas ao se pesquisar algum termo em cada portal
    dict_max_url = crawler.get_max_search_pages_number_portal(portals = crawler_config.portals_template_search)

    # pegando html das paginas de buscas para puxar os links
    html_search_pages = crawler.get_html_search_pages(portals = crawler_config.portals_template_search,
                                                      #url_max_opt = 19, url_max_force = True,
                                                      dict_max_url = dict_max_url)

    # puxando os links das paginas
    link_pairs = extractor.extract_links(dict_html = html_search_pages,
                                    portals_template = crawler_config.portals_template)
    links = [url for _, url in link_pairs]

    print(f'Número de links extraídos: {len(links)}')
    pd.DataFrame(links).to_csv(r'/tmp/links_of_articles_correcao_full.csv', index=False,sep="~", encoding='utf-8')


    #test = [("bnc_amazonas", a) for (a, b) in links]
    extraction_links = [(portal, url) for portal, (url, title) in link_pairs]
    batch_extract_from_url(extraction_links)
