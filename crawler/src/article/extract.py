from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import traceback
import time

from .rules import extract_templates

def extract(html_text, template_key):
    soup = BeautifulSoup(html_text, features="lxml")
    template=extract_templates[template_key]

    print(template_key)

    title = None
    if callable(template["title"]):
        title = template["title"](soup)
    else:
        title = soup.find(template["title"][0], class_=template["title"][1])

    body = None
    if callable(template["body"]):
        body = template["body"](soup)
    else:
        body = soup.find(template["body"][0], class_=template["body"][1])

    collected_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    published_date = None
    if "published_date" in template:
        if callable(template["published_date"]):
            published_date = template["published_date"](soup)
        else:
            published_date = soup.find(template["published_date"][0], class_=template["published_date"][1]).text.strip()
            if len(template["published_date"]) > 2:
                published_date = datetime.strptime(published_date, template["published_date"][2])

    tags = None
    if "tags" in template:
        tags = soup.find(template["tags"][0], class_=template["tags"][1])
        if tags is not None:
            tags = tags.text


    if "img_area" in template:
        if callable(template["img_area"]):
            images = template["img_area"](soup)
        else:
            images = soup.find(template["img_area"][0], class_=template["img_area"][1])
    else:
        images = body

    images = images.find_all("img")
    image_urls = [img.get("src") for img in images if img.get("src")]

    if "url_area" in template:
        url_obj = soup.find(template["url_area"][0], class_=template["url_area"][1]).find_all("a")
    else:
        url_obj = body.find_all("a")
        #url_obj = soup.find_all("a")

    urls = [url.get("href") for url in url_obj if url.get("href")]


    #return title.get_text(), body.text, collected_date, published_date, tags, image_urls, urls
    return {
        "title": title.get_text(separator=" ", strip=True),
        "body": body.get_text(separator="\n", strip=True),
        "collected_date": collected_date,
        "published_date": published_date,
        "tags": tags,
        "image_urls": image_urls,
        "urls": urls,
    }

def extract_from_url(url, template_key):
    html_text = requests.get(url).text
    time.sleep(1)
    #print(html_text)
    ret = extract(html_text, template_key)
    ret["article_url"] = url
    return ret

# NOTE: Does not store article URL in CSV
# html_pairs = [(portal_name, html_text)]
def batch_extract_from_html(html_pairs):
    rows = []
    failed = []
    for portal, html_text in html_pairs:
        try:
            artigo = extract(html_text, portal)

            rows.append(artigo)

        except Exception as e:
            failed.append({
                "portal": portal,
                #"url": url,
                "exception": e,
                "traceback": traceback.format_exc(),
            })

    export_csv(rows, failed)

# url_pairs = [(portal_name, article_url)]
def batch_extract_from_url(url_pairs):
    rows = []
    failed = []
    for portal, url in url_pairs:
        try:
            artigo = extract_from_url(url, portal)

            rows.append(artigo)

        except Exception as e:
            failed.append({
                "portal": portal,
                "url": url,
                #"exception": e,
                #"traceback": traceback.format_exc(),
            })

    export_csv(rows, failed)

def export_csv(rows, failed):
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    df = pd.DataFrame(rows)
    df.to_csv(f"output/{filename}.csv", sep=",", index=False)

    if failed:
        #print(failed)
        df = pd.DataFrame(failed)
        df.to_csv(f"output/{filename}-failed.csv", sep=",", index=False)

    print(f"Successful: {len(rows)}")
    print(f"Failed: {len(failed)}")


"""
def main():
    url_pairs = [
            ("agazetadoacre", "https://agazetadoacre.com/2025/04/colunistas/guia-gazeta/6o-guia-gazeta/van-damme-e-acusado-de-ter-relacoes-sexuais-com-romenas-vitimas-de-trafico-humano/"),
            ("selesnafes", "https://selesnafes.com/2025/07/ex-agente-que-inspirou-filme-som-da-liberdade-estara-no-amapa/"),
            ("dol", "https://dol.com.br/carajas/noticias/935475/trafico-na-asia-brasileiros-sao-resgatados-de-regime-escravo"),
            ("rondoniaovivo", "https://rondoniaovivo.com/noticia/brasilemundo/2023/03/29/escravidao-brasileiros-sao-vitimas-de-trafico-humano-na-asia-apos-cairem-em-golpe.html"),
            ("folhabv", "https://www.folhabv.com.br/policia/migrantes-sao-as-principais-vitimas-de-trafico-humano-em-roraima/"),
            ("correio24horas", "https://www.correio24horas.com.br/minha-bahia/enfermeira-e-presa-suspeita-de-matar-o-marido-a-facadas-em-salvador-0326"),
            ("bemparana", "https://www.bemparana.com.br/cultura/caso-diddy-rapper-e-acusado-de-trafico-humano-em-novo-processo/"),
            ("gazetaweb", "https://www.gazetaweb.com/noticias/policia/preso-suspeito-de-torturar-namorada-de-16-anos-e-mante-la-em-casinha-de-cachorro-894338"),
            ("metropoles", "https://www.metropoles.com/sao-paulo/brasileiro-trafico-humano-camboja"),
            ("amazonas_atual", "https://amazonasatual.com.br/pf-deflagra-operacao-dark-bet-de-combate-ao-trafico-de-brasileiros/"),
            ("amazonas_atual", "https://amazonasatual.com.br/operacao-cassandra-combate-trafico-de-brasileiras-para-exploracao-sexual/"),
            ("cnn", "https://www.cnnbrasil.com.br/internacional/ataque-dos-eua-a-embarcacao-no-pacifico-deixa-mortos/"),
            ("cnn", "https://www.cnnbrasil.com.br/internacional/e-mail-parece-confirmar-que-foto-de-andrew-e-virginia-giuffre-e-real/"),
            ("bnc_amazonas", "https://bncamazonas.com.br/migracao-e-trafico-de-pessoas-na-fronteira-norte/"),
            ("g1", "https://g1.globo.com/rr/roraima/noticia/2026/02/05/policia-estima-que-200-cubanos-foram-vitimas-de-esquema-de-trafico-humano-pela-fronteira-do-brasil-com-a-guiana-em-3-meses.ghtml"),
            ("g1", "https://g1.globo.com/rr/roraima/noticia/2026/02/05/policia-estima-que-200-cubanos-foram-vitimas-de-esquema-de-trafico-humano-pela-fronteira-do-brasil-com-a-guiana-em-3-meses.ghtml"),
            ("g1", "https://g1.globo.com/rj/rio-de-janeiro/noticia/2026/03/12/pf-faz-buscas-em-copacabana-e-na-barra-em-operacao-contra-esquema-de-passaportes-brasileiros-usados-para-migracao-ilegal.ghtml"),
            ("g1", "https://g1.globo.com/podcast/o-assunto/noticia/2025/03/17/o-assunto-1427-o-relato-de-luckas-vitima-de-trafico-humano-em-mianmar.ghtml"),
            ("g1", "https://g1.globo.com/pb/paraiba/noticia/2025/08/15/quem-e-hytalo-santos-influenciador-preso-por-suspeita-de-exploracao-sexual-infantil.ghtml"),
    ]

    batch_extract_from_url(url_pairs)

if __name__ == "__main__":
    main()
"""
