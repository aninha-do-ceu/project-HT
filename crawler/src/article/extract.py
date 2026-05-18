from bs4 import BeautifulSoup
import requests
import copy
from datetime import datetime
import pandas as pd
import traceback
import time

#Portais por Região:
#
#Norte
#
# OK - Rio Branco (AC) — A Gazeta do Acre
# Tags e data - Macapá (AP) — Seles Nafes
# Sem busca? Manaus (AM) — Portal do Holanda
# OK - Belém (PA) — O Liberal / DOL (Diário Online)
# OK - Porto Velho (RO) — Rondoniaovivo
# CLOUDFARE - Boa Vista (RR) — Folha de Boa Vista
# Buscar outro site mais significante? - Palmas (TO) — Conexão Tocantins / Jornal do Tocantins
#
#Nordeste
#
# Data complexa, analisar depois - Salvador (BA) — Correio 24h
#Fortaleza (CE) — Diário do Nordeste / O Povo
#São Luís (MA) — Imirante
#João Pessoa (PB) — ClickPB
#Recife (PE) — JC Online (Jornal do Commercio)
#Teresina (PI) — CidadeVerde
#Natal (RN) — Tribuna do Norte
#Aracaju (SE) — Infonet
# OK, mas precisa de busca em JS - Maceió (AL) — GazetaWeb
#
#Centro-Oeste
#
# OK - Brasília (DF) — Metrópoles → entre os maiores portais do Brasil
#Goiânia (GO) — Mais Goiás / Jornal Opção
#Cuiabá (MT) — Olhar Direto
#Campo Grande (MS) — Midiamax → líder em audiência estadual
#
#Sudeste
#
#São Paulo (SP) — G1 São Paulo / UOL Notícias / Folha de S.Paulo
#Rio de Janeiro (RJ) — G1 Rio
#Belo Horizonte (MG) — Estado de Minas / O Tempo / Por Dentro de Minas
#Vitória (ES) — A Gazeta (ES)
#
#Sul
#
# Cloudfare / ??? Curitiba (PR) — Bem Paraná / Gazeta do Povo
#Florianópolis (SC) — ND Mais → um dos maiores portais do país
#Porto Alegre (RS) — GZH (GaúchaZH / Zero Hora)


# Expected returns for custom functions:
#   title:          tag object
#   body:           tag object
#   published_date: datetime object
#   img_area:       tag object

def rondoniaovivo_title(soup):
    title = soup.find("div", class_="conteudoNoticia").find("h1")

    return title

def carta_capital_title(soup):
    title = soup.find("section", class_="s-content__heading").find("h1")

    return title

def dol_title(soup):
    title = soup.find("section", class_="article-header").find("h1")

    return title

def correio24horas_body(soup):
    body = soup.find_all("div", class_="leading-[30px]")

    new_soup = BeautifulSoup("", features="lxml")

    for tag in body:
        new_soup.append(copy.deepcopy(tag))

    return new_soup

def gazetaweb_body(soup):
    body = soup.find("article", id="article").find_all("p", recursive=False)

    new_soup = BeautifulSoup("", features="lxml")

    for tag in body:
        new_soup.append(copy.deepcopy(tag))

    return new_soup

def gazetaweb_date(soup):
    tmp = soup.find("div", class_="articleInfos").find("p")

    direct_text = "".join(
        str(node)
        for node in tmp.contents
        if node.name is None  # means it's a text node
    ).strip()

    return datetime.strptime(direct_text, "%d/%m/%Y às %H:%M")

def gazetaweb_img(soup):
    img_area = soup.find("article", id="article").find_all("figure", recursive=False)

    new_soup = BeautifulSoup("", features="lxml")

    for tag in img_area:
        new_soup.append(copy.deepcopy(tag))

    return new_soup

def bnc_amazonas_body(soup):
    tmp = soup.find("div", class_="space-y-5 py-8 lg:space-y-6 lg:text-[21px] [&_blockquote]:font-bold [&_blockquote]:text-primary")

    new_soup = BeautifulSoup("", features="lxml")

    def relevante(tag):
        return tag.name not in ("aside")

    body = tmp.find_all(relevante, recursive=False)

    for tag in body:
        new_soup.append(copy.deepcopy(tag))

    return new_soup

def bnc_amazonas_date(soup):
    tmp = soup.find("div", class_="text-sm mt-3 font-bold text-[#777777] lg:text-base [&_span]:text-[#C02626]")

    published_date = (
        tmp
        .find_all("p", recursive=False)[2]
        .get_text(separator=" ", strip=True)
        .split("|", 1)[0]
        .strip()
    )

    return published_date


extract_templates = {
    'agazetadoacre': {
        'title': ("h1", "jeg_post_title"),
        'body': ("div", "content-inner"),
        'published_date': ("div", "jeg_meta_date", "%d/%m/%Y - %H:%M"),
        'img_area': ("div", "featured_image"),
    },
    'selesnafes': {
        'title': ("h1", "evo-entry-title"),
        'body': ("div", "markdown prose dark:prose-invert w-full break-words light"),
        'published_date': ("div", "evo-post-date"),
        'tags': ("div", "evo-post-tags"),
    },
    'dol': {
        'title': dol_title,
        #'body': ("div", "dol-c-carajas"),
        'body': ("section", "article-container"),
        'published_date': ("div", "article-info"),
        'tags': ("section", "mw-blocoVertical-title-tags"),
    },
    'rondoniaovivo': {
        'title': rondoniaovivo_title,
        'body': ("div", "conteudoTexto"),
        'published_date': ("div", "post-meta-date"),
    },
    'folhabv': {
        'title': ("h1", "single-head-title"),
        'body': ("div", "single-content"),
        'published_date': ("span", "single-datetime-text", "%d/%m/%Y %H:%M"),
        'img_area': ("section", "single-body"),
    },
    'correio24horas': {
        'title': ("h1", "component--titulo"),
        'body': correio24horas_body,
        #'published_date': ("span", "single-datetime-text", "%d/%m/%Y %H:%M"),
        'img_area': ("figure", "imagem-notas"),
    },
    'bemparana': {
        'title': ("h1", "post-title"),
        'body': ("div", "post-content"),
        #'published_date': ("span", "published", "%d/%m/%Y às %H:%M"),
        'published_date': ("span", "published"),
    },
    'gazetaweb': {
        'title': ("h1", None),
        'body': gazetaweb_body,
        'published_date': gazetaweb_date,
        'img_area': gazetaweb_img,
    },
    'metropoles': {
        'title': ("h1", "Text__TextBase-sc-1d75gww-0 TcJvw"),
        'body': ("div", "ConteudoNoticiaWrapper__Artigo-sc-19fsm27-1 eehoEi"),
        'published_date': ("time", "HeaderNoticiaWrapper__DataPublicacao-sc-4exe2y-3 dAMWSS", "%d/%m/%Y %H:%M,"),
    },
    'cnn': {
        'title': ("h1", "font-bold text-3xl lg:text-4xl"),
        'body': ("div", "text-lg w-full pt-6 font-light text-neutral-800 group-[.isActiveSource>*]:text-xl md:pt-10 [&>*:not(.single-product)]:mx-auto [&>*:not(.single-product)]:max-w-2xl [&_.gallery]:mb-4 [&_p]:my-4 first:[&_p]:mt-0 [&_strong]:font-medium"),
        'published_date': ("time", "text-sm font-normal text-neutral-400"),
        'tags': ("div", "mt-4 flex flex-wrap gap-2.5"),
    },
    'carta_capital': {
        'title': carta_capital_title,
        'body': ("div", "contentOpen"),
        #'published_date':
    },
    'correiobraziliense': {
        'title': ("h1", None),
        #'body': ("div", "cb-content-materia"),
        'body': ("article", "article"),
        'published_date': ("div", "date"),
        #'tags': ("div", "tags"), # causes issues on some articles
    },
    'g1': {
        #'title': ("h1", "content-head__title"),
        'title': ("div", "title"),
        'body': ("article", None),
        'published_date': ("time", None),
    },
    'amazonas_atual': {
        'title': ("h1", "s-title fw-headline"),
        'body': ("div", "entry-content rbct clearfix is-highlight-shares"),
        'published_date': ("abbr", "date published"),
        'tags': ("span", "tags-list"),
        'url_area': ("div", "e-ct-outer"),
    },
    'bnc_amazonas': {
        'title': ("h1", None),
        'body': ("div", "space-y-5 py-8 lg:space-y-6 lg:text-[21px] [&_blockquote]:font-bold [&_blockquote]:text-primary"),
        #'body': bnc_amazonas_body,
        #'published_date': ("div", "text-sm mt-3 font-bold text-[#777777] lg:text-base [&_span]:text-[#C02626]"),
        'published_date': bnc_amazonas_date,
        'tags': ("ul", "pb-6 flex flex-wrap [&_a]:text-sm gap-3 [&_a]:uppercase [&_a]:transition-all hover:[&_a]:bg-primary hover:[&_a]:text-white hover:[&_a]:scale-95 [&_a]:text-primary [&_a]:block [&_a]:font-bold [&_a]:px-3 [&_a]:py-2 [&_a]:rounded-md [&_a]:border-2 [&_a]:border-primary"),
    },
}

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

    time.sleep(1)

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
    #print(html_text)
    ret = extract(html_text, template_key)
    ret["article_url"] = url
    return ret

# WARNING: Does not store article URL in CSV
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
                "exception": e,
                "traceback": traceback.format_exc(),
            })

    export_csv(rows, failed)

def export_csv(rows, failed):
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    df = pd.DataFrame(rows)
    df.to_csv(f"output/{filename}.csv", sep=",", index=False)

    if failed:
        print(failed)
        df = pd.DataFrame(failed)
        df.to_csv(f"output/{filename}-failed.csv", sep=",", index=False)

    print(f"Success: {len(rows)}")
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
