import pgf
from daison import *
from wordnet import *
from html import escape
import hashlib
import re
import json
import urllib.request

class ConcrHelper:
	def __init__(self,cnc,lang,edit):
		self.cnc  = cnc
		self.edit = edit
		self.links = {}
		self.name  = cnc.name
		self.lang  = lang
		self.exprs = []

	def addLink(self,lexeme,qid):
		if isinstance(lexeme,Lexeme):
			for lang,status in lexeme.status:
				if lang == self.cnc.name:
					break
			else:
				status = Status.Checked
			expr = pgf.ExprFun(lexeme.lex_fun)
			info = (qid,expr,status)
			self.links[expr] = info
			return info
		else:
			info = (qid,lexeme,Status.Checked)
			self.links[lexeme] = info

	def removeLink(self,lexeme):
		del self.links[lexeme]

	def linearize(self,e,title=False):
		if self.edit:
			self.exprs.append(e)
		text = ""
		bind = True
		info = None
		def flatten(xs):
			nonlocal text, bind, info
			for x in xs:
				if isinstance(x,str):
					if title:
						x = x.title();
					if bind:
						bind = False
					else:
						text += " "
					if info:
						if self.edit:
							text += '<span class="'+info[2].name.lower()+'" data-fun=\"'+escape(info[1].name)+'\" onclick="edit_lex(this,event)">'
						else:
							text += '<a href="index.wsgi?id='+info[0]+'&lang='+self.lang+'">'
						info = None
					text += escape(x)
				elif isinstance(x,pgf.Bracket):
					if x.fun == "FullName" and len(x.children) == 2 and isinstance(x.children[0],pgf.Bracket) and isinstance(x.children[1],pgf.Bracket) and not self.edit:
						expr = w.FullName(pgf.ExprFun(x.children[0].fun),
						                  pgf.ExprFun(x.children[1].fun))
						info = self.links.get(expr)
						tmp  = info
						if info:
							text += ' <a href="index.wsgi?id='+info[0]+'&lang='+self.lang+'">'
							info = None
						bind = True
						flatten(x.children)
						if tmp:
							text += '</a>'
					elif x.fun == "GivenName" and len(x.children) == 1 and isinstance(x.children[0],pgf.Bracket) and not self.edit:
						expr = w.GivenName(pgf.ExprFun(x.children[0].fun))
						info = self.links.get(expr)
						tmp  = info
						if info:
							text += ' <a href="index.wsgi?id='+info[0]+'&lang='+self.lang+'">'
							info = None
						bind = True
						flatten(x.children)
						if tmp:
							text += '</a>'
					elif x.fun == "MaleSurname" and len(x.children) == 1 and isinstance(x.children[0],pgf.Bracket) and not self.edit:
						expr = w.MaleSurname(pgf.ExprFun(x.children[0].fun))
						info = self.links.get(expr)
						tmp  = info
						if info:
							text += ' <a href="index.wsgi?id='+info[0]+'&lang='+self.lang+'">'
							info = None
						bind = True
						flatten(x.children)
						if tmp:
							text += '</a>'
					elif x.fun == "FemaleSurname" and len(x.children) == 1 and isinstance(x.children[0],pgf.Bracket) and not self.edit:
						expr = w.MaleSurname(pgf.ExprFun(x.children[0].fun))
						info = self.links.get(expr)
						tmp  = info
						if info:
							text += ' <a href="index.wsgi?id='+info[0]+'&lang='+self.lang+'">'
							info = None
						bind = True
						flatten(x.children)
						if tmp:
							text += '</a>'
					else:
						expr = pgf.ExprFun(x.fun)
						info = self.links.get(expr)
						if self.edit and info == None:
							self.links[expr] = False
							l = lexeme(x.fun)
							if l:
								info = self.addLink(l, None)
						tmp  = info

						flatten(x.children)
						if tmp:
							if self.edit:
								text += '</span>'
							else:
								text += '</a>'
				elif isinstance(x,pgf.BIND):
					bind = True
		lin = self.cnc.bracketedLinearize(e)
		if lin:
			flatten(lin)
		if len(text) > 0:
			text = text[0].upper()+text[1:]
			if self.edit:
				text = "<span data-expr=\""+escape(str(e))+"\">"+text+"</span>"
		return text

	def get_lex_fun(self, qid, link=True, filter=None):
		lexemes = wikilexemes(qid)
		if filter:
			lexemes = [lexeme for lexeme in lexemes if filter in lexeme.lex_fun] or lexemes
		if lexemes:
			if link:
				self.addLink(lexemes[0], qid)
			return pgf.ExprFun(lexemes[0].lex_fun)
		return None

	def get_lexemes(self,prop,entity,qual=True,link=True,filter=None):
		items = []
		if qual:
			for value in entity["claims"].get(prop,[]):
				try:
					qid = value["mainsnak"]["datavalue"]["value"]["id"]
				except KeyError:
					continue
				fun = self.get_lex_fun(qid,link,filter)
				if fun:
					items.append((fun,value.get("qualifiers",{})))
		else:
			for value in entity["claims"].get(prop,[]):
				try:
					qid = value["mainsnak"]["datavalue"]["value"]["id"]
				except KeyError:
					continue
				fun = self.get_lex_fun(qid,link,filter)
				if fun:
					items.append(fun)
		return items

	def get_lexeme_qualifiers(self,prop,quals,link=True):
		items = []
		for value in quals.get(prop,[]):
			try:
				qid = value["datavalue"]["value"]["id"]
			except KeyError:
				continue
			fun = self.get_lex_fun(qid,link)
			if fun:
				items.append(fun)
		return items

	def get_demonyms(self,prop,entity,link=True):
		adjs = set()
		pns  = set()
		all_adjs = True
		
		for value in entity["claims"].get(prop,[]):
			try:
				qid = value["mainsnak"]["datavalue"]["value"]["id"]
			except KeyError:
				continue

			pn  = False
			adj = False
			for lexeme in wikilexemes(qid):
				if not pn:
					if link:
						self.addLink(lexeme, qid)
					pns.add(pgf.ExprFun(lexeme.lex_fun))
					pn = True

				for lexeme2 in lexeme.synset().lexemes():
					if not adj:
						for adj_lexeme in lexeme2.derived():
							if w.__pgf__.functionType(adj_lexeme.lex_fun).cat != "A":
								continue
							if link:
								self.addLink(adj_lexeme, qid)
							adjs.add(pgf.ExprFun(adj_lexeme.lex_fun))
							adj = True
			if not adj:
				all_adjs = False

		return (all_adjs, adjs if all_adjs else pns)

	def get_person_name(self, entity):
		given_names  = self.get_lexemes("P735",entity,qual=False,link=False)
		family_names = self.get_lexemes("P734",entity,qual=False,link=False)

		if given_names and grammar.functionType(given_names[0].name).cat == "GN":
			if family_names and grammar.functionType(family_names[0].name).cat == "SN":
				expr = w.FullName(given_names[0], family_names[0])
			else:
				expr = w.GivenName(given_names[0])
		elif family_names and grammar.functionType(family_names[0].name).cat == "SN":
			if "Q6581072" in get_items("P21", entity):
				expr = w.FemaleSurname(family_names[0])
			else:
				expr = w.MaleSurname(family_names[0])
		else:
			return None

		self.addLink(expr, entity["id"])
		return expr


def get_items(prop,entity,qual=True):
	items = []
	if qual:
		for value in entity["claims"].get(prop,[]):
			try:
				items.append((value["mainsnak"]["datavalue"]["value"]["id"],value.get("qualifiers",{})))
			except KeyError:
				continue
	else:
		for value in entity["claims"].get(prop,[]):
			try:
				items.append(value["mainsnak"]["datavalue"]["value"]["id"])
			except KeyError:
				continue
	return items

def get_entities(prop,entity,qual=True):
	if isinstance(prop,list):
		props = prop
	else:
		props = [prop]

	items = {}
	for prop in props:
		for value in entity["claims"].get(prop,[]):
			if len(items) >= 50:
				break
			try:
				items[value["mainsnak"]["datavalue"]["value"]["id"]] = value.get("qualifiers",{})
			except KeyError:
				continue

	if not items:
		return []

	u2 = urllib.request.urlopen("https://www.wikidata.org/w/api.php?action=wbgetentities&ids="+"|".join(items)+"&languages=en&format=json")
	result = json.loads(u2.read())["entities"]

	entities = []
	if qual:
		for item,quals in items.items():
			try:
				entities.append((result[item],quals))
			except KeyError:
				continue
	else:
		for item,quals in items.items():
			try:
				entities.append(result[item])
			except KeyError:
				continue
	return entities

def get_quantities(prop,entity):
	quantities = []
	for value in entity["claims"].get(prop,[]):
		try:
			amount = float(value["mainsnak"]["datavalue"]["value"]["amount"])
		except:
			continue
		quantities.append((amount,value.get("qualifiers",{})))
	return quantities

def get_medias(prop,entity):
	medias = []
	for value in entity["claims"].get(prop,[]):
		try:
			img = value["mainsnak"]["datavalue"]["value"]
		except KeyError:
			continue
		img = img.replace(' ','_')
		h = hashlib.md5(img.encode("utf-8")).hexdigest()
		img = "https://upload.wikimedia.org/wikipedia/commons/"+h[0]+"/"+h[0:2]+"/"+img
		medias.append((img,value.get("qualifiers",{})))
	return medias

def get_date(prop,entity):
	for value in entity["claims"].get(prop,[]):
		try:
			match = str2date(value["mainsnak"]["datavalue"]["value"]["time"])
			if match:
				return match
		except KeyError:
			continue
	else:
		return None

def has_novalue(prop,entity):
	for value in entity["claims"].get(prop,[]):
		try:
			if value["mainsnak"]["snaktype"] == "novalue":
				return True
		except KeyError:
			continue
	else:
		return False

iso8601_regex = re.compile(r"^(?P<era>\+|-)?(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(T| )(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(?P<offset>(Z|(?P<offset_op>\+|-)?(?P<offset_hour>\d{2}):?(?P<offset_minute>\d{2})))?$")

def str2date(value):
	match = iso8601_regex.match(value)
	if not match:
		return None

	year = int(match.group("year"))
	if year == 0:
		return None

	match match.group("era"):
		case "-":
			year *= -1
		case _:
			year = year
	year = w.intYear(pgf.ExprLit(year))
	match int(match.group("month")):
		case 0:
			month = None
		case 1:
			month = w.january_Month
		case 2:
			month = w.february_Month
		case 3:
			month = w.march_Month
		case 4:
			month = w.april_Month
		case 5:
			month = w.may_Month
		case 6:
			month = w.june_Month
		case 7:
			month = w.july_Month
		case 8:
			month = w.august_Month
		case 9:
			month = w.september_Month
		case 10:
			month = w.october_Month
		case 11:
			month = w.november_Month
		case 12:
			month = w.december_Month

	match int(match.group("day")):
		case 0:
			day = None
		case d:
			day = w.intMonthday(pgf.ExprLit(d))

	if month:
		if day:
			return w.dayMonthYearAdv(day, month, year)
		else:
			return w.monthYearAdv(month, year)
	else:
		return w.yearAdv(year)

def get_item_qualifier(prop,quals):
	for value in quals.get(prop,[]):
		try:
			return value["datavalue"]["value"]["id"]
		except KeyError:
			continue
	return None

def get_time_qualifier(prop,quals):
	for value in quals.get(prop,[]):
		try:
			return value["datavalue"]["value"]["time"]
		except KeyError:
			continue
	return None

def get_quantity_qualifier(prop,quals):
	for value in quals.get(prop,[]):
		try:
			return float(value["datavalue"]["value"]["amount"])
		except KeyError:
			continue
	return None

def get_entity(qid):
	if isinstance(qid,str):
		u2 = urllib.request.urlopen('https://www.wikidata.org/wiki/Special:EntityData/'+qid+'.json')
		result = json.loads(u2.read())
		return next(iter(result["entities"].values()))
	elif not qid:
		return []
	else:
		items = set(qid)
		items.discard(None)
		u2 = urllib.request.urlopen("https://www.wikidata.org/w/api.php?action=wbgetentities&ids="+"|".join(items)+"&languages=en&format=json")
		result = json.loads(u2.read())["entities"]
		return result
