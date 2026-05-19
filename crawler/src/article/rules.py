from bs4 import BeautifulSoup
import copy
from datetime import datetime

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
