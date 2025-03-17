import pgf
from wordnet import *
from nlg.util import *

def marry(cnc, gender, verb=None):
    if cnc.name in ["ParseRus"]:
        if "Q6581072" in gender:
            if verb == "V2":
                return w.marry_1b_V2
            else:
                return w.marry_1b_V
        else:
            if verb == "V2":
                return w.marry_1a_V2
            else:
                return w.marry_1a_V
    else:
        if verb == "V2":
            return w.marry_1a_V2
        elif verb == "in":
            return w.marry_in_V
        else:
            return w.marry_1a_V

def render(cnc, lexeme, entity):
    yield "<div class='infobox'><table border=1><tr><table>"
    for media,qual in get_medias("P18",entity):
        yield "<tr><td><img src='"+escape(media)+"' width=250/></td></tr>"
        break
    for media,qual in get_medias("P109",entity):
        yield "<tr><td><img src='"+escape(media)+"' width=250/></td></tr>"
        break
    yield "</table></tr></table></div>"

    gender = get_items("P21",entity,qual=False)

    yield "<p>"

    if "Q6581072" in gender:
        if cnc.name in ["ParseSpa"]:
            pron = w.ProDrop(w.she_Pron)
        else:
            pron = w.she_Pron
    else:
        if cnc.name in ["ParseSpa"]:
            pron = w.ProDrop(w.he_Pron)
        else:
            pron = w.he_Pron

    if cnc.name in ["ParseBul"]:
        useTense = presentTense
        usePastTense = presentTense
        usePastSimpleTense = presentTense
        usePasseCompose = anteriorAnt
    elif cnc.name in ["ParseSpa"]:
        useTense = presentTense
        usePastTense = pastSimpleTense
        usePastSimpleTense = pastSimpleTense
        usePasseCompose = anteriorAnt
    else:
        if get_date("P570",entity):  # dead
            useTense = pastTense
        else:
            useTense = presentTense
        usePastTense = pastTense
        usePastSimpleTense = pastSimpleTense
        usePasseCompose = anteriorAnt

    current_position = []
    prev_position = []

    if cnc.name in ["ParseRus"]:
        filter = "Masc"
    else:
        filter = "Fem" if "Q6581072" in gender else "Masc"

    for position, qual in cnc.get_lexemes("P39", entity, filter=filter):
        if 'P582' in qual:
            prev_position.append(mkCN(position))
        else:
            current_position.append(mkCN(position))
    if cnc.name not in ["ParseRus"]:
        current_position = mkCN(w.and_Conj, current_position)
    prev_position = mkCN(w.and_Conj, prev_position)

    occupations = [mkCN(occupation) for occupation in
                                    cnc.get_lexemes("P106", entity, qual=False, filter=filter)]

    if not occupations:
        if get_items("P184",entity):
            occupations = [mkCN(w.scientistFem_N if "Q6581072" in gender else w.scientistMasc_N)]
        elif "Q6581097" in gender:
            occupations = [mkCN(w.man_1_N)]
        elif "Q6581072" in gender:
            occupations = [mkCN(w.woman_1_N)]
        else:
            occupations = [mkCN(w.human_N)]

    extra_description = False
    all_adjs,ds = cnc.get_demonyms("P27", entity)
    if ds:
        if all_adjs:
            ap = mkAP(w.and_Conj,[mkAP(adj) for adj in ds])
            if current_position:
                if cnc.name in ["ParseRus"]:
                    positions = [mkCN(ap, current_position[0]),]
                    positions.extend(current_position[1:])
                    description = mkCN(w.and_Conj,positions)
                    extra_description = mkCN(w.and_Conj,occupations)
                else:
                    description = mkCN(ap, current_position)  # né / nacido
                    extra_description = mkCN(w.and_Conj,occupations)
            else:
                if cnc.name in ["ParseRus"]:
                    positions = [mkCN(ap, occupations[0])]
                    positions.extend(occupations[1:])
                    occupations = mkCN(w.and_Conj, occupations)
                    description = mkCN(w.and_Conj, positions)
                else:
                    description = mkCN(ap, mkCN(w.and_Conj,occupations))
        else:
            np = mkNP(w.and_Conj,[mkNP(pn) for pn in ds])
            description = mkCN(mkCN(w.and_Conj, occupations),mkAdv(w.from_Prep,np))
            if current_position:
                if cnc.name in ["ParseRus"]:
                    description = mkCN(mkCN(w.and_Conj, current_position), mkAdv(w.from_Prep, np))
                else:
                    description = mkCN(current_position,mkAdv(w.from_Prep,np))
                extra_description = mkCN(w.and_Conj, occupations)
    else:
        if current_position:
            description = current_position
            extra_description = mkCN(w.and_Conj, occupations)
        else:
            description = mkCN(w.and_Conj, occupations)

    birthday   = get_date("P569",entity)
    birthplace = cnc.get_lexemes("P19", entity, qual=False)
    if birthday or birthplace:
        verb = mkVPSlash(w.bear_2_V2)
        if birthday:
            verb = mkVPSlash(verb,birthday)
        if birthplace:
            verb = mkVPSlash(verb,mkAdv(birthplace[0]))
        if cnc.name in ["ParseRus"] and isinstance(description, list):
            desc_positions = [mkCN(mkAP(verb), description[0]),]
            desc_positions.extend(description[1:])
            description = mkCN(w.and_Conj,desc_positions)
        else:
            description = mkCN(mkAP(verb),description)

    if cnc.name in ["ParseRus"]:
        phr = mkPhr(mkUtt(mkS(presentTense,mkCl(lexeme,mkNP(aSg_Det,description)))),fullStopPunct)
    else:
        phr = mkPhr(mkUtt(mkS(useTense,mkCl(lexeme,mkNP(aSg_Det,description)))),fullStopPunct)
    yield " "+cnc.linearize(phr)

    if extra_description:
        phr = mkPhr(mkUtt(mkS(mkCl(mkNP(pron), mkVP(w.also_AdV, mkVP(mkNP(aSg_Det,extra_description)))))),fullStopPunct)
        yield " "+cnc.linearize(phr)
    if prev_position:
        phr = mkPhr(mkUtt(mkS(pastSimpleTense, mkCl(mkNP(pron),mkNP(aSg_Det,prev_position)))),fullStopPunct)
        yield " "+cnc.linearize(phr)

    
    advisors = []
    for advisor in get_entities(["P184"],entity,qual=False):
        name = cnc.get_person_name(advisor)
        if name:
            advisors.append(name)
    if advisors:
        num = singularNum if len(advisors) == 1 else pluralNum
        advisors = mkNP(w.and_Conj,advisors)
        if cnc.name in ["ParseRus"]:
            yield " " + cnc.linearize(
                mkPhr(mkUtt(mkS(presentTense, mkCl(mkNP(mkDet(pron, num), mkCN(w.doctoral_adviser_N)), advisors))),
                      fullStopPunct))
        else:
            yield " "+cnc.linearize(mkPhr(mkUtt(mkS(usePastTense,mkCl(mkNP(mkDet(pron,num),mkCN(w.doctoral_adviser_N)),advisors))),fullStopPunct))

    teachers = []
    adviser_teacher = False
    for teacher in get_entities(["P1066"],entity,qual=False):
        if teacher["id"] not in get_items("P184",entity,qual=False):
            name = cnc.get_person_name(teacher)
            if name:
                teachers.append(name)
        else:
            adviser_teacher = True
    if teachers:
        num = singularNum if len(teachers) == 1 else pluralNum
        teachers = mkNP(w.and_Conj,teachers)
        if cnc.name in ["ParseRus"]:
            tense = presentTense
        else:
            tense = useTense
        if adviser_teacher:
            yield " "+cnc.linearize(mkPhr(mkUtt(mkS(tense,mkCl(mkNP(pron),mkVP(w.also_AdV, mkVP(mkNP(aSg_Det,w.PossNP(mkCN(w.studentMasc_1_N),teachers))))))),fullStopPunct))
        else:
            yield " "+cnc.linearize(mkPhr(mkUtt(mkS(tense,mkCl(mkNP(pron),mkNP(aSg_Det,w.PossNP(mkCN(w.studentMasc_1_N),teachers))))),fullStopPunct))
    
    students = []
    for student in get_entities(["P802","P185"],entity,qual=False):
        name = cnc.get_person_name(student)
        if name:
            students.append(name)
    if students:
        students = mkNP(w.and_Conj,students)
        if cnc.name in ["ParseRus"]:
            phr = mkPhr(
                mkUtt(mkS(presentTense, mkCl(mkNP(pron), mkNP(theSg_Det, w.PossNP(mkCN(w.supervisorMasc_1_N), students))))),
                fullStopPunct)
        else:
            phr = mkPhr(mkUtt(mkS(useTense,mkCl(mkNP(pron),mkNP(theSg_Det,w.PossNP(mkCN(w.supervisorMasc_1_N),students))))),fullStopPunct)
        yield " "+cnc.linearize(phr)
    

    # Property native language - P103
    native_language_qid = cnc.get_lexemes("P103",entity,qual=False)
    native_lang = []
    if native_language_qid:
        for qid in native_language_qid:
            native_lang.append(mkNP(qid))

    # Property languages spoken, written or signed - P1412
    other_langs = []
    for qid in cnc.get_lexemes("P1412",entity,qual=False):
        if qid not in native_language_qid:
            other_langs.append(mkNP(qid))

    if native_lang:
        num = singularNum if len(native_lang) == 1 else pluralNum
        native_lang = mkNP(w.and_Conj,native_lang)
        other_langs = mkNP(w.and_Conj,other_langs)

        if cnc.name in ["ParseRus"]:
            phr = mkS(presentTense, mkCl(mkNP(mkDet(pron, num), mkCN(w.native_language_N)), native_lang))
        else:
            phr = mkS(useTense,mkCl(mkNP(mkDet(pron,num), mkCN(w.native_language_N)), native_lang))
        if other_langs:
            # His/Her native lang(s) is/are [...] but he also speaks [...]
            if cnc.name in ["ParseRus"]:
                phr = mkS(w.but_1_Conj, phr,
                          mkS(usePastTense, mkCl(mkNP(pron), mkVP(w.also_AdV, mkVP(w.speak_3_V2, other_langs)))))
            else:
                phr = mkS(w.but_1_Conj,phr,mkS(useTense,mkCl(mkNP(pron), mkVP(w.also_AdV,mkVP(w.speak_3_V2, other_langs)))))
        phr = mkPhr(mkUtt(phr),fullStopPunct)
        yield " " + cnc.linearize(phr)
    elif other_langs:
        other_langs = mkNP(w.and_Conj,other_langs)
        # He/She speaks [...]
        phr = mkPhr(mkUtt(mkS(useTense,mkCl(mkNP(pron),mkVP(w.speak_3_V2, other_langs)))),fullStopPunct)
        yield " " + cnc.linearize(phr)
    

    # member of - P463
    institutions = set()
    for qid,qual in get_items("P463",entity):
        inst = cnc.get_lex_fun(qid)
        if "P582" not in qual and inst != None:
            institutions.add(mkNP(inst))

    if institutions:
        # He/She is a member of [...]
        institutions = mkNP(w.and_Conj, list(institutions))
        phr = mkPhr(mkUtt(mkS(mkCl(mkNP(pron), mkNP(aSg_Det, w.PossNP(mkCN(w.member_4_N), institutions))))),fullStopPunct)
        yield " " + cnc.linearize(phr)
    yield "</p>"

    father = None
    for father in get_entities("P22",entity,qual=False):
        father = cnc.get_person_name(father)
        break
    mother = None
    for mother in get_entities("P25",entity,qual=False):
        mother = cnc.get_person_name(mother)
        break

    sisters  = []
    brothers = []
    for sibling in get_entities("P3373",entity,qual=False):
        name = cnc.get_person_name(sibling)
        if not name:
            continue
        if "Q6581072" in get_items("P21",sibling,qual=False):
            sisters.append(name)
        else:
            brothers.append(name)
    siblings = []
    if brothers:
        if len(brothers) == 1:
            det = aSg_Det
        elif len(brothers) < 10:
            det = mkDet(a_Quant,mkNum(mkNumeral(len(brothers))))
        else:
            det = mkDet(a_Quant,mkNum(len(brothers)))
        siblings.append(mkNP(det,mkCN(w.brother_1_N, mkNP(w.and_Conj,brothers))))
    if sisters:
        if len(sisters) == 1:
            det = aSg_Det
        elif len(sisters) < 10:
            det = mkDet(a_Quant,mkNum(mkNumeral(len(sisters))))
        else:
            det = mkDet(a_Quant,mkNum(len(sisters)))
        siblings.append(mkNP(det,mkCN(w.sister_1_N, mkNP(w.and_Conj,sisters))))
    siblings = mkNP(w.and_Conj, siblings)

    children = get_entities("P40",entity, qual=False)

    number_children_prop = get_quantities("P1971",entity)
    number = None
    for item in number_children_prop:
        number = int(item[0])
    child_count = 0

    unmarried_partners = sorted([(partner,
                           get_time_qualifier("P580",quals) or "X",
                           get_time_qualifier("P582",quals),
                           get_item_qualifier("P1534",quals)) for partner,quals in get_entities("P451",entity)],key=lambda p: p[1])

    spouse_novalue = has_novalue("P26",entity)
    spouses = sorted([(spouse,
                       get_time_qualifier("P580",quals) or "X",
                       cnc.get_lexeme_qualifiers("P2842",quals),
                       get_time_qualifier("P582",quals),
                       get_item_qualifier("P1534",quals)) for spouse,quals in get_entities("P26",entity)],key=lambda p: p[1])

    deathday   = get_date("P570",entity)
    deathplace = cnc.get_lexemes("P20", entity, qual=False)

    personal_life = [mother, father, sisters, brothers, siblings, children, number_children_prop, number, unmarried_partners, spouses, spouse_novalue, deathday, deathplace]
    if any(personal_life):
        yield '<h2 class="gp-page-title">'+cnc.linearize(mkCN(w.personal_1_A,w.life_3_N))+'</h2>'
        yield "<p>"

    if mother and father:
        if cnc.name in ["ParseFre", "ParseSpa", "ParseRus"]:
            prep = w.into_1_Prep if cnc.name in ["ParseFre"] else w.in_1_Prep
            vp = mkVP(mkVP(w.be_born_V), mkAdv(prep, mkNP(theSg_Det,w.PossNP(mkCN(w.family_1_N),mkNP(w.and_Conj,[father,mother])))))
        else:
            vp = mkVP(passiveVP(w.bear_2_V2), mkAdv(w.in_1_Prep, mkNP(theSg_Det,w.PossNP(mkCN(w.family_1_N),mkNP(w.and_Conj,[father,mother])))))
        if siblings:
            if cnc.name in ["ParseFre"]:
                vp = w.ConjVPS(w.and_Conj,w.BaseVPS(w.MkVPS(mkTemp(useTense, usePasseCompose),positivePol,vp), w.MkVPS(mkTemp(presentTense,simultaneousAnt),positivePol,mkVP(w.have_1_V2,siblings))))
                phr = mkPhr(mkUtt(w.PredVPS(mkNP(pron), vp)), fullStopPunct)
            elif cnc.name in ["ParseRus"]:
                stm2 = mkS(mkAdv(w.at_1_Prep, mkNP(pron)), mkS(mkCl(siblings)))
                phr = mkPhr(mkUtt(mkS(w.and_Conj, mkS(usePastTense,mkCl(mkNP(pron),vp)), stm2)), fullStopPunct)
                #phr = mkPhr(mkUtt(stm2),fullStopPunct)
            else:
                vp = w.ConjVPS(w.and_Conj,w.BaseVPS(w.MkVPS(mkTemp(usePastTense,simultaneousAnt),positivePol,vp), w.MkVPS(mkTemp(presentTense,simultaneousAnt),positivePol,mkVP(w.have_1_V2,siblings))))
                phr = mkPhr(mkUtt(w.PredVPS(mkNP(pron),vp)),fullStopPunct)
        else:
            if cnc.name in ["ParseFre"]:
                phr = mkPhr(mkUtt(mkS(useTense, usePasseCompose,mkCl(mkNP(pron),vp))),fullStopPunct)
            else:
                phr = mkPhr(mkUtt(mkS(usePastTense,mkCl(mkNP(pron),vp))),fullStopPunct)
        yield " "+cnc.linearize(phr)
    elif mother:
        if cnc.name in ["ParseRus"]:
            stmt = mkS(presentTense, mkCl(mkNP(mkDet(pron, singularNum), mkCN(w.mother_1_N)), mother))
        else:
            stmt = mkS(useTense,mkCl(mkNP(mkDet(pron,singularNum),mkCN(w.mother_1_N)),mother))
        if siblings:
            stmt = mkS(w.and_Conj, stmt, mkS(mkCl(mkNP(pron), mkVP(w.have_1_V2,siblings))))
        phr = mkPhr(mkUtt(stmt),fullStopPunct)
        yield " "+cnc.linearize(phr)
    elif father:
        if cnc.name in ["ParseRus"]:
            stmt = mkS(presentTense, mkCl(mkNP(mkDet(pron, singularNum), mkCN(w.father_1_N)), father))
        else:
            stmt = mkS(useTense,mkCl(mkNP(mkDet(pron,singularNum),mkCN(w.father_1_N)),father))
        if siblings:
            stmt = mkS(w.and_Conj, stmt, mkS(mkCl(mkNP(pron), mkVP(w.have_1_V2,siblings))))
        phr = mkPhr(mkUtt(stmt),fullStopPunct)
        yield " "+cnc.linearize(phr)
    elif siblings:
        phr = mkPhr(mkUtt(mkS(mkCl(mkNP(pron), mkVP(w.have_1_V2,siblings)))),fullStopPunct)
        yield " "+cnc.linearize(phr)

    if spouse_novalue:
        spouses = None
        phr = mkPhr(mkUtt(mkS(useTense, mkCl(mkNP(pron), mkVP(w.never_1_AdV,mkVP(marry(cnc, gender, "in")))))),fullStopPunct)
        yield " "+cnc.linearize(phr)
    else:
        for spouse,start,place,end,end_cause in spouses:
            filter = "Fem" if "Q6581072" in get_items("P21",spouse,qual=False) else "Masc"
            occupation = cnc.get_lexemes("P106", spouse, qual=False, filter=filter)
            occupation = mkCN(occupation[0]) if occupation else None
            all_adjs, ds = cnc.get_demonyms("P27", spouse)
            if ds:
                ds = list(ds)[0]
                if all_adjs:
                    description = mkCN(mkAP(ds), occupation) if occupation else None
                else:
                    description = occupation
            else:
                description = occupation
            
            partner_spouse = False

            child = None
            child_name = []
            no_names = False
            same_parent_child = 0
            if children:
                for kid in children:
                    if any(mother == spouse["id"] or father == spouse["id"] for mother in get_items("P25", kid, qual=False) for father in get_items("P22", kid, qual=False)):
                        same_parent_child += 1
                        child = cnc.get_person_name(kid)
                        if child:
                            child_name.append(child)
                        else:
                            no_names = True
            number_children = len(child_name)
            child_name = mkNP(w.and_Conj, child_name)

            name = cnc.get_person_name(spouse)
            spouse_pron = w.she_Pron if "Q6581072" in get_items("P21",spouse,qual=False) else w.he_Pron

            for partner,start_up,end_up,end_cause_up in unmarried_partners:
                if partner["id"] == spouse["id"] and end_cause_up == 'Q8445':
                    partner_spouse = True
                    if name:
                        if description:
                            if cnc.name in ["ParseFre", "ParseSpa", "ParseBul"]:
                                name = mkNP(the_Det, mkCN(description, name))
                                vp = mkVP(w.start_2_V2, mkNP(mkNP(aSg_Det, w.relationship_2_N), mkAdv(w.with_Prep, name)))
                            else:
                                name = mkCN(description, name)
                                vp = mkVP(w.start_2_V2, mkNP(mkNP(aSg_Det, w.relationship_2_N), mkAdv(w.with_Prep, mkNP(name))))
                        if cnc.name in ["ParseFre"]:
                            stmt = mkS(useTense, mkCl(mkNP(pron), vp))
                        else:
                            stmt = mkS(usePastTense, mkCl(mkNP(pron), vp))
                        if start_up:
                                start_date = str2date(start_up)
                                if start_date:
                                    stmt = w.ExtAdvS(start_date,stmt)
                        #vp = mkVP(w.marry_1_V2,mkNP(spouse_pron))
                        vp = mkVP(marry(cnc, gender, "V"))
                        #Spanish / French: they married (se casaron/ils se sont mariés)
                        if place:
                            vp = mkVP(vp,mkAdv(place[0]))
                        if start:
                            start_date = str2date(start)
                            if start_date:
                                vp = mkVP(vp, start_date)
                        #stmt2 = mkS(usePastTense, mkCl(mkNP(pron), vp))
                        #stmt2 = mkS(usePastSimpleTense, mkCl(mkNP(w.they_Pron), vp))
                        if cnc.name in ["ParseFre"]:
                            stmt2 = mkS(useTense, usePasseCompose, mkCl(mkNP(w.they_Pron), vp))
                        else:
                            stmt2 = mkS(usePastTense, mkCl(mkNP(w.they_Pron), vp))
                        phr = mkPhr(mkUtt(mkS(w.and_Conj, stmt, stmt2)), fullStopPunct)
                        yield " "+cnc.linearize(phr)
                        break

            if not partner_spouse and name:
                if description:
                    if cnc.name in ["ParseFre", "ParseBul"]:
                        name = mkNP(the_Det, mkCN(description, name))
                        vp = mkVP(w.marry_1a_V2,name)
                    elif cnc.name in ["ParseSpa"]:
                        name = mkNP(the_Det, mkCN(description, name))
                        vp = mkVP(mkVP(w.marry_1a_V), mkAdv(w.with_Prep, name))
                    else:
                        name = mkNP(mkCN(description, name))
                        vp = mkVP(marry(cnc, gender, "V2"),name)
                else:
                    vp = mkVP(marry(cnc, gender, "V2"),name)

                if place:
                    vp = mkVP(vp,mkAdv(place[0]))
                if cnc.name in ["ParseFre"]:
                    stmt = mkS(useTense, mkCl(mkNP(pron), vp))
                else:
                    stmt = mkS(usePastTense, mkCl(mkNP(pron), vp))
                if start:
                    start = str2date(start)
                    if start:
                        stmt = w.ExtAdvS(start,stmt)
                phr = mkPhr(mkUtt(stmt),fullStopPunct)
                yield " "+cnc.linearize(phr)

            if no_names:
                child_count += same_parent_child
                det = mkDet(a_Quant, mkNum(mkNumeral(same_parent_child))) if same_parent_child in range(1,10) else mkDet(a_Quant, mkNum(same_parent_child))
                phr = mkPhr(mkUtt(mkS(useTense, mkCl(mkNP(w.they_Pron), mkVP(w.have_1_V2, mkNP(det, mkCN(w.child_2_N)))))), fullStopPunct)
                yield " " + cnc.linearize(phr)
            else:
                if child_name:
                # They have X children: [list of names]
                    if number_children < 10:
                        det = mkDet(a_Quant,mkNum(mkNumeral(number_children)))
                    else:
                        det = mkDet(a_Quant,mkNum(number_children))
                    child_count += number_children
                    if cnc.name in ["ParseRus"]:
                        children_sent = mkS(mkAdv(w.at_1_Prep, mkNP(pron)), mkS(useTense, mkCl(mkNP(det, mkCN(w.child_2_N)))))
                    else:
                        children_sent = mkS(useTense, mkCl(mkNP(w.they_Pron), mkVP(w.have_1_V2, mkNP(det, mkCN(w.child_2_N)))))
                    yield " " + cnc.linearize(mkPhr(mkUtt(children_sent))) + ":" + cnc.linearize(child_name) + "."
        
            if end and end_cause not in ["Q4", "Q99521170", "Q24037741"]:
                vp = mkVP(mkVP(w.divorce_2_V),str2date(end))
                if cnc.name in ["ParseFre"]:
                    phr = mkPhr(mkUtt(mkS(useTense, mkCl(mkNP(w.they_Pron), vp))),fullStopPunct)
                else:
                    phr = mkPhr(mkUtt(mkS(usePastTense, mkCl(mkNP(w.they_Pron), vp))),fullStopPunct)
                yield " "+cnc.linearize(phr)

    if spouses and not children and number_children_prop:
        child_count += number
        if number == 0:
            phr = mkPhr(mkUtt(mkS(negativePol, mkCl(mkNP(pron), mkVP(w.have_1_V2, mkNP(aPl_Det, mkCN(w.child_2_N)))))), fullStopPunct)
        else:
            det = mkDet(a_Quant, mkNum(mkNumeral(number))) if number in range(1,10) else mkDet(a_Quant, mkNum(number))
            if cnc.name in ["ParseRus"]:
                phr = mkPhr(mkUtt(mkS(mkAdv(w.at_1_Prep, mkNP(pron)), mkS(mkCl(mkNP(det, mkCN(w.child_2_N)))))), fullStopPunct)
            else:
                phr = mkPhr(mkUtt(mkS(mkCl(mkNP(pron), mkVP(w.have_1_V2, mkNP(det, mkCN(w.child_2_N)))))), fullStopPunct)
        yield " " + cnc.linearize(phr)

    for partner,start,end,end_cause in unmarried_partners:
        occupation = cnc.get_lexemes("P106", partner, qual=False)
        occupation = mkCN(occupation[0]) if occupation else None
        all_adjs, ds = cnc.get_demonyms("P27", partner)
        if ds:
            ds = list(ds)[0]
            if all_adjs:
                description = mkCN(mkAP(ds), occupation) if occupation else None
            else:
                description = occupation
        else:
            description = occupation
        
        child = None
        child_name = []
        no_names = False
        same_parent_child = 0
        if children:
            for kid in children:
                if any(mother == partner["id"] or father == partner["id"] for mother in get_items("P25", kid, qual=False) for father in get_items("P22", kid, qual=False)):
                    same_parent_child += 1
                    child = cnc.get_person_name(kid)
                    if child:
                        child_name.append(child)
                    else:
                        no_names = True # to avoid cases where we have names for some chidren (from the same couple) but not for others
        number_children = len(child_name)
        child_name = mkNP(w.and_Conj, child_name)

        name = cnc.get_person_name(partner)
        if name and not end:
            if description:
                if cnc.name in ["ParseFre", "ParseSpa", "ParseBul"]:
                    name = mkNP(the_Det, mkCN(description, name))
                else:
                    name = mkNP(mkCN(description, name))
            vp = mkVP(w.start_2_V2, mkNP(mkNP(aSg_Det, w.relationship_2_N), mkAdv(w.with_Prep, name)))

            if cnc.name in ["ParseFre"]:
                stmt = mkS(useTense, mkCl(mkNP(pron), vp))
            else:
                stmt = mkS(usePastTense, mkCl(mkNP(pron), vp))
            if start:
                    start = str2date(start)
                    if start:
                        stmt = w.ExtAdvS(start,stmt)
            phr = mkPhr(mkUtt(stmt),fullStopPunct)
            yield " "+cnc.linearize(phr)

            if no_names:
                child_count += same_parent_child
                det = mkDet(a_Quant, mkNum(mkNumeral(same_parent_child))) if number in range(1,10) else mkDet(a_Quant, mkNum(same_parent_child))
                phr = mkPhr(mkUtt(mkS(mkCl(mkNP(w.they_Pron), mkVP(w.have_1_V2, mkNP(det, mkCN(w.child_2_N)))))), fullStopPunct)
                yield " " + cnc.linearize(phr)
            else:
                if child_name:
                    # They have X children: [list of names]
                    if number_children < 10:
                        det = mkDet(a_Quant,mkNum(mkNumeral(number_children)))
                    else:
                        det = mkDet(a_Quant,mkNum(number_children))
                    child_count += number_children
                    if cnc.name in ["ParseRus"]:
                        children_sent = mkS(mkAdv(w.at_1_Prep, mkNP(pron)), mkS(mkCl(mkNP(det, mkCN(w.child_2_N)))))
                    else:
                        children_sent = mkS(mkCl(mkNP(w.they_Pron), mkVP(w.have_1_V2, mkNP(det, mkCN(w.child_2_N)))))
                    yield " " + cnc.linearize(mkPhr(mkUtt(children_sent))) + ":" + cnc.linearize(child_name) + "."
    
    # If the entity has (other) child(ren) but we have no info about the other parent
    # TO DO: Needs some specific work for SPA and FRE
    if number:
        other_child = number - child_count
        if other_child > 0:
            if child_count == 0: # no info about the other parent AND no other child(ren) mentioned before (child_count == 0)
                det = mkDet(a_Quant, mkNum(mkNumeral(other_child))) if other_child in range(1,10) else mkDet(a_Quant, mkNum(other_child))
            else:
                det = mkDet(a_Quant, w.NumMore(mkNum(mkNumeral(other_child)))) if other_child in range(1,10) else mkDet(a_Quant, w.NumMore(mkNum(other_child)))
            # [entity] has X child(ren) / [entity] has X more child(ren)
            phr = mkPhr(mkUtt(mkS(mkCl(lexeme, mkVP(w.have_1_V2, mkNP(det, w.child_2_N))))), fullStopPunct)
            yield " " + cnc.linearize(phr)

    if deathday or deathplace:
        deathmanner= get_items("P1196", entity, qual=False)
        killer = get_entities("P157", entity, qual=False)
        if killer:
            vp = passiveVP(w.kill_1_V2,cnc.get_person_name(killer[0]))
        elif "Q149086" in deathmanner:
            vp = passiveVP(w.kill_1_V2)
        else:
            vp = mkVP(w.die_1_V)
        if deathday:
            vp = mkVP(vp,deathday)
        if deathplace:
            if deathplace[0].name.endswith("_PN"):
                vp = mkVP(vp,mkAdv(w.in_1_Prep, deathplace[0]))
            else:
                vp = mkVP(vp,mkAdv(deathplace[0]))
        phr = mkPhr(mkUtt(mkS(useTense, mkCl(mkNP(pron), vp))),fullStopPunct)
        yield " "+cnc.linearize(phr)

    yield "</p>"

    university = cnc.get_lexemes("P69",entity,qual=False)
    if university:
        yield '<h2 class="gp-page-title">'+cnc.linearize(w.education_2_N)+'</h2>'
        yield "<p>"

        universities = set()
        for uni in university:
            universities.add(mkNP(uni))
        universities = mkNP(w.and_Conj, list(universities))

        if cnc.name in ["ParseFre"]: #Il/Elle a obtenu son diplôme de [la/le/l'] + institution(s)
            phr = mkPhr(mkUtt(mkS(useTense,usePasseCompose, mkCl(mkNP(pron), mkVP(mkVP(w.obtain_1_V2, mkNP(mkQuant(pron), w.degree_3_N)), mkAdv(w.from_Prep, universities))))),fullStopPunct)
        elif cnc.name in ["ParseDut"]:
            # He/She graduated from [university name]
            phr = mkPhr(mkUtt(mkS(presentTense,anteriorAnt, mkCl(mkNP(pron), mkVP(mkVP(w.graduate_V), mkAdv(w.at_1_Prep, universities))))),fullStopPunct)
        elif cnc.name in ["ParseRus"]:
            phr = mkPhr(mkUtt(mkS(pastTense, anteriorAnt,
                                  mkCl(mkNP(pron), mkVP(w.graduate_2_V2, universities)))),
                        fullStopPunct)

        else:
            # He/She graduated from [university name]
            phr = mkPhr(mkUtt(mkS(usePastTense, mkCl(mkNP(pron), mkVP(mkVP(w.graduate_V), mkAdv(w.from_Prep, universities))))),fullStopPunct)
        yield " " + cnc.linearize(phr)
        yield "</p>"

    notable_works = get_entities(["P800"],entity,qual=False)
    if notable_works:
        yield '<h2 class="gp-page-title">'+cnc.linearize(mkUtt(mkNP(aPl_Det,mkCN(w.notable_2_A,w.work_2_N))))+'</h2>'
        yield "<ul>"
        for notable_work in notable_works:
            lbl = notable_work["labels"]
            lbl = lbl.get(cnc.lang) or lbl.get("en")
            if lbl:
                lbl = lbl["value"]
                yield "<li><a href=\"index.wsgi?id="+notable_work["id"]+"&lang="+cnc.lang+"\">"+lbl+"</a></li>"
        yield "</ul>"

    # award received:
    awards_dict = {}
    for award,qual in get_entities("P166",entity,qual=True):
        dates = awards_dict.setdefault(award["id"],(award,[]))[1]
        if "P585" in qual:
            date = get_time_qualifier("P585",qual)
            dates.append(date)

    if awards_dict:
        yield '<h2 class="gp-page-title">'+cnc.linearize(mkNP(aPl_Det,w.award_3_N))+'</h2>'

        # He/She received the following awards:
        if cnc.name in ["ParseFre", "ParseSpa"]:
            yield '<p>'+cnc.linearize(mkPhr(mkUtt(mkS(useTense,usePasseCompose, mkCl(mkNP(pron), mkVP(w.receive_1_V2, mkNP(thePl_Det,mkCN(w.following_2_A, w.award_3_N))))))))+':'
        else:
            yield '<p>'+cnc.linearize(mkPhr(mkUtt(mkS(usePastTense, mkCl(mkNP(pron), mkVP(w.receive_1_V2, mkNP(thePl_Det,mkCN(w.following_2_A, w.award_3_N))))))))+':'


        # List of awards:
        if len(awards_dict) < 5:
            column_count = 1
        elif len(awards_dict) < 10:
            column_count = 2
        else:
            column_count = 4
        yield "<ul style='column-count: "+str(column_count)+"'>"
        for award,dates in awards_dict.values():
            lbl = award["labels"]
            lbl = lbl.get(cnc.lang) or lbl.get("en")
            if not lbl:
                continue
            if len(dates) > 1:
                # it extracts the year part (ex.: 2019) from each date string (ex.: '+2019-00-00T00:00:00Z') and constructs the date_string with years only
                date_string = ", ".join([date.split('-')[0].lstrip('+') for date in dates])
                yield "<li><a href=\"index.wsgi?id="+award["id"]+"&lang="+cnc.lang+"\">"+lbl["value"] + "</a> (" + cnc.linearize(w.in_1_Prep) + " " + date_string +")"+"</li>"
            else:
                yield "<li><a href=\"index.wsgi?id="+award["id"]+"&lang="+cnc.lang+"\">"+lbl["value"]+"</a></li>"
        yield '</ul></p>'

    #Nominated for - P1411
    #TO DO: Add year?
    nominations = get_entities(["P1411"],entity,qual=False)
    if nominations:
        prep = w.to_1_Prep if cnc.name in ["ParseSpa"] else w.for_Prep
        if awards_dict:
            yield '<p>'+cnc.linearize(mkPhr(mkUtt(mkS(useTense,usePasseCompose, mkCl(mkNP(pron), mkVP(w.also_AdV, mkVP(passiveVP(mkVPSlash(w.nominate_1_V2)), mkAdv(prep, mkNP(thePl_Det,mkCN(w.following_2_A, w.award_3_N))))))))))+':'
        else:
            yield '<p>'+cnc.linearize(mkPhr(mkUtt(mkS(useTense,usePasseCompose, mkCl(mkNP(pron), mkVP(passiveVP(mkVPSlash(w.nominate_1_V2)), mkAdv(prep, mkNP(thePl_Det,mkCN(w.following_2_A, w.award_3_N)))))))))+':'
        yield "<ul>"
        for nomination in nominations:
            lbl = nomination["labels"]
            lbl = lbl.get(cnc.lang) or lbl.get("en")
            if lbl:
                lbl = lbl["value"]
                yield "<li><a href=\"index.wsgi?id="+nomination["id"]+"&lang="+cnc.lang+"\">"+lbl+"</a></li>"
        yield "</ul>"
