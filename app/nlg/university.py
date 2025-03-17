from os import name
import pgf
from wordnet import *
from nlg.util import *
from nlg.lists import *


def render(cnc, lexeme, entity):
	# show the location
	yield "<div class='infobox'><table border=1>"
	for media,qual in get_medias("P18",entity):
		yield "<tr><td><img src='"+escape(media)+"' width=250></td></tr>"
		break
	yield "</table></div>"

	cn = mkCN(w.university_1_N)

	country = cnc.get_lexemes("P17",entity,qual=False)
	if country:
		cn = mkCN(cn, mkAdv(country[0]))

	inception = get_date("P571",entity)
	founder   = get_entities("P112",entity,qual=False)
	if founder:
		founder = cnc.get_person_name(founder[0])
	vpslash = mkVPSlash(w.establish_4_V2)
	if inception:
		vpslash = mkVPSlash(vpslash,inception)
	ap = None
	if founder:
		ap = w.PastPartAgentAP(vpslash,founder)
	elif inception:
		ap = mkAP(vpslash)
	if ap:
		cn = mkCN(ap,cn)

	yield cnc.linearize(mkPhr(mkUtt(mkS(mkCl(mkNP(lexeme),mkNP(aSg_Det, cn)))),fullStopPunct))

	student_counts = sorted(((population,get_time_qualifier("P585",quals) or "X") for population,quals in get_quantities("P2196",entity)),key=lambda p: p[1],reverse=True)
	if student_counts:
		count, date = student_counts[0]
		s = mkCl(mkNP(mkNum(count),w.studentMasc_1_N))
		if date:
			date = str2date(date)
		if date:
			s = mkS(date,mkS(pastTense,s))
		else:
			s = mkS(s)
		yield " "+cnc.linearize(mkPhr(mkUtt(s),fullStopPunct))

	office = get_entities("P2388",entity,qual=False)
	if office:
		holder = sorted(((population,get_time_qualifier("P580",quals) or "X") for population,quals in get_items("P1308",office[0])),key=lambda p: p[1],reverse=True)
		if holder:
			holder = get_entity(holder[0][0])
			if holder:
				holder = cnc.get_person_name(holder)
				lexeme = cnc.get_lexemes("P279",office[0],qual=False)
				if not lexeme:
					lexeme = [w.presidentMasc_5_N]
				yield " "+cnc.linearize(mkPhr(mkUtt(mkS(mkCl(mkNP(theSg_Det,mkCN(w.current_A,lexeme[0])),holder))),fullStopPunct))
