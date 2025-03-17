import pgf

import nlg.country
import nlg.country_list
import nlg.capital
import nlg.city
import nlg.human
import nlg.profession
import nlg.language
import nlg.university
from nlg.util import *

def render(cnc, lex_expr,entity): 
	class_qids = get_items("P31",entity,qual=False)

	s=cnc.linearize(lex_expr, title=True)
	yield '<h1 class="gp-page-title">'+s+'</h1>'
	
	if "Q6256" in class_qids:
		renderer = nlg.country.render
	elif "Q5119" in class_qids:
		renderer = nlg.capital.render
	elif "Q1549591" in class_qids:
		renderer = nlg.city.render
	elif "Q515" in class_qids:
		renderer = nlg.city.render
	elif "Q200250" in class_qids:
		renderer = nlg.city.render
	elif "Q129676344" in class_qids:
		renderer = nlg.city.render
	elif "Q5" in class_qids:
		renderer = nlg.human.render
	elif "Q28640" in class_qids or "Q12737077" in class_qids or "Q828803" in class_qids:
		renderer = nlg.profession.render
	elif "Q3918" in class_qids or "Q5341295" in class_qids or "Q875538" in class_qids:
		renderer = nlg.university.render
	elif "Q34770" in class_qids:
		renderer = nlg.language.render
	else:
		renderer = None
		yield "<p>Define a renderer for at least one of the following classes: "+", ".join(class_qids)+"</p>"

	if renderer:
		for s in renderer(cnc,lex_expr,entity):
			yield s

def render_list(cnc,qid):
	return nlg.country_list.render(cnc)
