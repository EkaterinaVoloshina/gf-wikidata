import json
import html
import urllib.request
from urllib.parse import parse_qs
from daison import *

import pgf
gr = pgf.readNGF("/usr/local/share/x86_64-linux-ghc-8.0.2/gf-4.0.0/www/Parse.ngf")
gr.embed("wordnet")
import wordnet as w
from wordnet.api import *
from wordnet.semantics import *

#import nlg.country
#import nlg.capital
#import nlg.city

db = openDB("/usr/local/www/gf-wordnet/semantics.db")

prelude = [
  b'<html>',
  b' <title>GFpedia</title>',
  b' <head>',
  b'     <link rel="stylesheet" type="text/css" href="gf-wikidata.css">',
  b'     <script src="gf-wikidata.js"></script>',
  b' </head>',
  b' <body>',
  b'     <div class="gp-head">',
  b'          <form class="search-box">',
  b'             <input class="search-box-input" type="search" name="search"',
  b'                    placeholder="Search GFpedia" aria-label="Search GFpedia"',
  b'                    autocapitalize="sentences" title="Search GFpedia" id="searchInput"',
  b'                    autocomplete="off"',
  b'                    oninput="showSearches(this)"',
  b'                    onkeypress="searchInputOnKeyPress(event)"',
  b'                    onkeydown="searchInputOnKeyDown(event)">',
  b'             <img class="search-box-button" src="search.svg">',
  b'             <table class="search-box-results" id="searchResults"></table>',
  b'         </form>',
  b'     </div>',
  b'     <div class="gp-panel">',
  b'         <img class="gp-logo" src="gp-logo.svg">',
  b'         <div class="gp-panel-section">',
  b'           <table>'
  ]

langs = {
  "af": ("Afrikaans", "ParseAfr"),
  "bg": ("Bulgarian", "ParseBul"),
  "ca": ("Catalan",   "ParseCat"),
  "zh": ("Chinese",   "ParseChi"),
  "nl": ("Dutch",     "ParseDut"),
  "en": ("English",   "ParseEng"),
  "et": ("Estonian",  "ParseEst"),
  "fi": ("Finnish",   "ParseFin"),
  "fr": ("French",    "ParseFre"),
  "de": ("German",    "ParseGer"),
  "it": ("Italian",   "ParseIta"),
  "ko": ("Korean",    "ParseKor"),
  "mt": ("Maltese",   "ParseMlt"),
  "pl": ("Polish",    "ParsePol"),
  "pt": ("Portuguese","ParsePor"),
  "ro": ("Romanian",  "ParseRon"),
  "ru": ("Russian",   "ParseRus"),
  "sl": ("Slovenian", "ParseSlv"),
  "so": ("Somali",    "ParseSom"),
  "es": ("Spanish",   "ParseSpa"),
  "sw": ("Swahili",   "ParseSwa"),
  "sv": ("Swedish",   "ParseSwe"),
  "th": ("Thai",      "ParseTha"),
  "tr": ("Turkish",   "ParseTur")
  }

home = [
  b'<h1>GF Pedia</h1>',
  b'<p>This is an experiment to see to what extend we can generate encyclopedic articles ',
  b'based on information from <a href="https://www.wikidata.org/">Wikidata</a> and by using ',
  b'the resource grammars in <a href="http://www.grammaticalframework.org/">GF</a> plus ',
  b'lexical resources in <a href="https://cloud.grammaticalframework.org/wordnet/">GF WordNet</a>.</p>'
  b'<p>Search for a Wikidata entity in the upper left corner.</p>'
  ]

epilogue = [
  b'     </div>',
  b' </body>',
  b'</html>'
  ]

def get_lex_fun(qid):
    with db.run("w") as t:
        for synset_id in t.cursor(synsets_qid, qid):
            for lexeme_id in t.cursor(lexemes_synset, synset_id):
                for lexeme in t.cursor(lexemes, lexeme_id):
                    return lexeme.lex_fun
    return None

def country_render(lexeme, cnc, entity):
	for value in entity["claims"]["P30"]:
		continent_qid = value["mainsnak"]["datavalue"]["value"]["id"]
		break
		
	if continent_qid:
		cn = mkCN(mkCN(w.country_1_N),mkAdv(w.in_1_Prep,mkNP(pgf.ExprFun(get_lex_fun(continent_qid)))))
	else:
		cn = mkCN(w.country_1_N)

	s=cnc.linearize(mkS(mkCl(mkNP(lexeme),mkNP(aSg_Det,cn))))
	yield "<p>"+html.escape(s)+"</p>"

def capital_render(lexeme, cnc, entity):
    for value in entity["claims"]["P17"]:
        country_qid = value["mainsnak"]["datavalue"]["value"]["id"]
        break
		
    if country_qid:
        cn = w.PossNP(mkCN(w.capital_3_N),mkNP(pgf.ExprFun(get_lex_fun(country_qid))))
    else:
        cn = mkCN(w.capital_3_N)

    s=cnc.linearize(mkS(mkCl(mkNP(lexeme),mkNP(the_Det,cn))))
    yield "<p>"+html.escape(s)+"</p>"

def city_render(lexeme, cnc, entity):
	for value in entity["claims"]["P17"]:
		country_qid = value["mainsnak"]["datavalue"]["value"]["id"]
		break
		
	if country_qid:
		cn = mkCN(mkCN(w.city_1_N),mkAdv(w.in_1_Prep,mkNP(pgf.ExprFun(get_lex_fun(country_qid)))))
	else:
		cn = mkCN(w.city_1_N)

	s=cnc.linearize(mkS(mkCl(mkNP(lexeme),mkNP(aSg_Det,cn))))
	yield "<p>"+html.escape(s)+"</p>"

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html; charset=utf-8')])
    query = parse_qs(env["QUERY_STRING"])
    
    qid   = query.get("id",[None])[0]
    if qid != None and (qid[0] != "Q" or not qid[1:].isdigit()):
        qid = None

    lang  = query.get("lang",["en"])[0]
    if lang not in langs:
        lang="en"

    content = []
    for line in prelude:
        content.append(line)

    if qid:
        content.append(b'             <tr><td><a href="https://cloud.grammaticalframework.org/wikidata">Main page</a></td></tr>')
        content.append(b'             <tr><td><a href="https://www.wikidata.org/wiki/'+bytes(qid,"utf8")+b'">Wikidata item</a></td></tr>')

    content.append(b'           </table>')
    content.append(b'         </div>')

    content.append(b'         <div class="gp-panel-section">')
    content.append(b'           <h3>Languages</h3>')
    content.append(b'           <table id="from">'),
    for code,(name,cnc) in langs.items():
        if code != lang:
            if qid != None:
                content.append(bytes('             <tr><td><a href="index.wsgi?id='+qid+'&lang='+code+'">'+name+'</a></td></tr>','utf8'))
            else:
                content.append(bytes('             <tr><td><a href="index.wsgi?lang='+code+'">'+name+'</a></td></tr>','utf8'))
        else:
            content.append(bytes('             <tr><td><b>'+name+'</b></td></tr>','utf8'))
    content.append(b'         </table>')
    content.append(b'       </div>')
    content.append(b'     </div>')
    content.append(b'     <div class="gp-body" id="content" data-lang="'+bytes(lang,"utf8")+b'">')

    if qid != None:
        u2 = urllib.request.urlopen('https://www.wikidata.org/wiki/Special:EntityData/'+qid+'.json')
        result = json.loads(u2.read())
        entity = result["entities"][qid]
        cnc = gr.languages[langs[lang][1]]

        lex_fun = get_lex_fun(qid)

        class_qids = []
        for value in entity["claims"]["P31"]:
            class_qid = value["mainsnak"]["datavalue"]["value"]["id"]
            class_qids.append(class_qid)

        if lex_fun:
            lex_expr = pgf.ExprFun(lex_fun)
            s=cnc.linearize(lex_expr).title()
            content.append(bytes("<h1>"+html.escape(s)+"</h1>","utf8"))
            
            if "Q6256" in class_qids:
                renderer = country_render
            elif "Q5119" in class_qids:
                renderer = capital_render
            elif "Q1549591" in class_qids:
                renderer = city_render
            elif "Q515" in class_qids:
                renderer = city_render
            else:
                renderer = None
                content.append(bytes("<p>Define a renderer for at least one of the following classes: "+", ".join(class_qids)+"</p>","utf8"))
				
            if renderer:
                for s in renderer(lex_expr,cnc,entity):
                    content.append(bytes(s,"utf8"))
        else:
            content.append(bytes("<h1>"+qid+"</h1>","utf8"))
            content.append(bytes("<p>There is no NLG for this item yet.</p>","utf8"))
    else:
        for line in home:
            content.append(line)

    for line in epilogue:
        content.append(line)
    return content
