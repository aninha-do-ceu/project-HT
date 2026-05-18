# define a URL padrão dos portais
portals_template = {
    'cnn':'https://www.cnnbrasil.com.br',
    'carta_capital':'https://www.cartacapital.com.br',
    'amazonas_atual': 'https://amazonasatual.com.br',
    'agazetadoacre':'https://agazetadoacre.com',
    'selesnafes':'https://selesnafes.com',
    'dol':'https://dol.com.br',
    'correiobraziliense':'https://www.correiobraziliense.com.br',
    'bnc_amazonas':'https://bncamazonas.com.br'

}

# define os termos a serem buscados
terms = ["trafico-de-pessoas","trafico-humano"]
#terms = ["trafico-humano"]
# ver se adiciona "tráfico sexual"

# define a pagina padrão para busca
page = 1

# define a URL padrão de busca de termos para cada portal
# cnn brasil
urls_search_cnn = { term: f"https://www.cnnbrasil.com.br/pagina/{page}/?search={term}" for term in terms}
# carta capital
urls_search_cc = { term: f"https://www.cartacapital.com.br/page/{page}/?s={term}" for term in terms}
# amazonas atual
urls_search_aa = { term: f"https://amazonasatual.com.br/page/{page}/?s={term}" for term in terms}
# BNC amazonas
urls_search_bnc = { term: f"https://bncamazonas.com.br/page/{page}/?s={term}" for term in terms}
# Gazeta do Acre
urls_search_gazeta_acre = { term: f"https://agazetadoacre.com/page/{page}/?s={term}" for term in terms}
# Seles Nafes
urls_search_seles_nafes = { term: f"https://selesnafes.com/page/{page}/?s={term}" for term in terms}
#DOL
urls_search_dol = { term: f"https://dol.com.br/?page={page}&q={term}" for term in terms}
# Correio Braziliense
urls_search_cor_bra = { term: f"https://www.correiobraziliense.com.br/busca/{term}/page/{page}/" for term in terms}


portals_template_search = {
    #'cnn':urls_search_cnn,
    #'carta_capital':urls_search_cc,
    #'amazonas_atual':urls_search_aa,
    #'agazetadoacre':urls_search_gazeta_acre,
    #'selesnafes':urls_search_seles_nafes,
    #'dol':urls_search_dol,
    'correiobraziliense':urls_search_cor_bra,
    #'bnc_amazonas':urls_search_bnc
}

portals_div_urls = {
    'cnn':['div', 'flex flex-col gap-4'],
    'carta_capital': ['div','l-list__left'],
    'amazonas_atual': ['h3','entry-title'],
    'agazetadoacre':['h3','jeg_post_title'],
    'selesnafes':['h3','evo-entry-title'],
    'dol':['h1', 'dol-title-bold'],
    'correiobraziliense':['div','box-text'],
    'bnc_amazonas':['div','grid grid-cols-1 gap-12 lg:gap-[60px]']
}
