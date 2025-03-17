import pgf
from wordnet import *
from nlg.util import *
# from nlg.lists import *

def copula_number(cnc, number):
    if cnc.name in ['ParseFre']:
        return mkAdv(w.of_1_Prep, number)
    elif cnc.name in ['ParseSpa']:
        return w.UseComp_ser(w.CompAdv(mkAdv(w.of_1_Prep, number)))
    elif cnc.name in ["ParseRus"]:
        return mkVP(w.amount_to_1_V2, number)
    else:
        return number

def render(cnc, lexeme, entity):
    yield "<div class='infobox'><table border=1>"
    # show the flag and the coat of arms if available
    for media,qual in get_medias("P18",entity):
        yield "<tr><td><img src='"+escape(media)+"' width=250/></td><tr>"
        break
    # show the location
    for media,qual in get_medias("P242",entity):
        yield "<tr><td><img src='"+escape(media)+"' width=250></td></tr>"
        break
    yield "</table></div>"

    yield "<p>"

    is_largest = []
    for qid, quals in get_items("P31", entity):
        if qid == "Q51929311":
            is_largest = cnc.get_lexeme_qualifiers("P642",quals)
            break
    country_qids = get_items("P17", entity)
    if country_qids:
        country_qid = country_qids[0][0]
        country = cnc.get_lex_fun(country_qid)

    if country:
        is_capital = None
        for qid, quals in get_items("P1376", entity):
            if qid == country_qid:
                if get_time_qualifier("P582",quals):
                    is_capital = mkCN(w.former_3_A,w.capital_3_N)
                else:
                    is_capital = mkCN(w.capital_3_N)
                break

        if is_capital and country in is_largest:
            np = mkNP(mkNP(w.and_Conj,mkNP(theSg_Det,is_capital),mkNP(mkDet(the_Quant,mkOrd(w.large_1_A)),mkCN(w.city_1_N))),mkAdv(w.in_1_Prep,mkNP(country)))
        elif is_capital:
            np = mkNP(theSg_Det,w.PossNP(is_capital,mkNP(country)))
        elif is_largest:
            np = mkNP(mkNP(mkDet(the_Quant,mkOrd(w.large_1_A)),mkCN(w.city_1_N)),mkAdv(w.in_1_Prep,mkNP(country)))
        else:
            np = mkNP(aSg_Det,mkCN(mkCN(w.city_1_N),mkAdv(w.in_1_Prep,mkNP(country))))
    else:
        np = mkNP(aSg_Det,mkCN(w.city_1_N))

    # add the number of inhabitants
    population_list = sorted(((population,get_time_qualifier("P585",quals) or "X") for population,quals in get_quantities("P1082",entity)),key=lambda p: p[1],reverse=True)
    if population_list:
        population = int(population_list[0][0])
        np = mkNP(np,mkAdv(w.with_Prep,mkNP(mkNum(population),w.inhabitantMasc_1_N)))

    phr=mkPhr(mkUtt(mkS(mkCl(mkNP(lexeme),np))),fullStopPunct)
    yield cnc.linearize(phr)


    # state the area
    area_list = sorted(((area,get_time_qualifier("P585",quals)) for area,quals in get_quantities("P2046",entity)),key=lambda p: p[1] or "",reverse=True)
    if area_list:
        area = area_list[0][0]
        if cnc.name in ["ParseSwe", "ParseGer", "ParseFin"]:
            sq_km = w.CompoundN(w.square_1_N,w.kilometre_1_N)
        else:
            sq_km = mkCN(w.square_1_A,w.kilometre_1_N)

        number = mkNP(mkDecimal(int(area)), sq_km)
        verb = copula_number(cnc, number)
        phr = mkPhr(mkUtt(mkS(mkCl(mkNP(theSg_Det,w.area_6_N),verb))),fullStopPunct)
        yield " " + cnc.linearize(phr)



    # State current head of government (HOG), previous HOG, HOG' gender and kinship:
    name_date_gov = []
    curr_head_gov_qid = None
    prev_head_gov_qid = None
    for head_government, qual in get_items("P6", entity):
        if 'P582' not in qual: # No end date == current head of government
            curr_head_gov_qid = head_government
        else: # End date == previous heads of government
            date = get_time_qualifier("P582",qual) # Checking end date
            if date:
                name_date_gov.append((head_government,date))
            else:
                curr_head_gov_qid = head_government

    # Sorting by dates
    if name_date_gov:
        name_date_gov.sort(key=lambda x: x[1], reverse=True)
        prev_head_gov_qid = name_date_gov[0][0]

    head_gov = []
    if curr_head_gov_qid:
        head_gov.append(curr_head_gov_qid)
    if prev_head_gov_qid:
        head_gov.append(prev_head_gov_qid)
    entities = get_entity(head_gov)

    # Linearizing:
    # The current head of government is [position] [name], who took office after [position] [name].
    # We need to consider keeping the long sentence into two simple sentences for cases like the United Arab Emirates,
    # where there is no data for the previous head of government!
    if curr_head_gov_qid:
        head_entity = entities[curr_head_gov_qid]
        curr_head_gov = cnc.get_person_name(head_entity)

        if curr_head_gov:
            # Checking gender
            gender = w.he_Pron if any(gender_qid == "Q6581097" for gender_qid, qual in get_items("P21", head_entity)) else w.she_Pron

            # Checking kinship
            father_qid = False
            mother_qid = False

            # Checking if there is a 'father' property (P22)
            for father_qid, quad in get_items("P22", head_entity):
                break

            # Checking if there is a 'mother' property (P25)
            for mother_qid, quad in get_items("P25", head_entity):
                break

            subj = mkNP(the_Det,mkCN(w.current_A, w.head_of_government_N))

            if prev_head_gov_qid:
                head_entity = entities[prev_head_gov_qid]
                prev_head_gov = cnc.get_person_name(head_entity)

                if prev_head_gov:
                    if prev_head_gov_qid == father_qid:
                        # his/her father [name]
                        prev_head_gov = mkNP(mkQuant(gender), mkCN(mkCN(w.father_1_N), prev_head_gov))
                    elif prev_head_gov_qid == mother_qid:
                        # He/She took office after his/her mother [name]
                        prev_head_gov = mkNP(mkQuant(gender), mkCN(mkCN(w.mother_1_N), prev_head_gov))

                    curr_head_gov = w.ExtRelNP(curr_head_gov, mkRS(pastSimpleTense, mkRCl(which_RP,mkVP(mkVP(w.take_office_V), mkAdv(w.after_Prep, prev_head_gov)))))
            phr = mkPhr(mkUtt(mkS(mkCl(subj, curr_head_gov))),fullStopPunct)
            yield " " + cnc.linearize(phr)

    yield "</p>"

    divisions = cnc.get_lexemes("P150",entity,qual=False)
    if divisions:
        yield '<h2 class="gp-page-title">'+cnc.linearize(mkNP(aPl_Det,mkCN(w.administrative_A,w.unit_3_N)))+'</h2>'
        # The country has the following administrative units:
        yield '<p>'+cnc.linearize(mkPhr(mkUtt(mkCl(mkNP(theSg_Det,w.country_1_N),mkVP(w.have_1_V2,mkNP(thePl_Det,mkCN(w.following_2_A,mkCN(w.administrative_A,w.unit_3_N))))))))+':'
        if len(divisions) < 5:
            column_count = 1
        elif len(divisions) < 10:
            column_count = 2
        else:
            column_count = 4
        yield "<ul style='column-count: "+str(column_count)+"'>"
        for division in divisions:
            yield "<li>"+cnc.linearize(division)+"</li>"
        yield '</ul></p>'

    objs = []

    gdp_list = sorted(((gdp,get_time_qualifier("P585",quals)) for gdp,quals in get_quantities("P2131",entity)),key=lambda p: p[1],reverse=True)
    if gdp_list:
        gdp = int(gdp_list[0][0])
        objs.append(mkNP(gdp,w.dollar_MU))

    gdp_list = sorted(((gdp,get_time_qualifier("P585",quals)) for gdp,quals in get_quantities("P2132",entity)),key=lambda p: p[1],reverse=True)
    if gdp_list:
        gdpp = int(gdp_list[0][0])
        objs.append(mkNP(mkNP(gdpp,w.dollar_MU),w.per_capita_Adv))

    if objs:
        yield '<h2 class="gp-page-title">'+cnc.linearize(w.economy_1_N)+'</h2>'

        yield "<p>"

        gdp = mkNP(w.and_Conj,objs)
        gdp_rate_list = sorted(((rate,get_time_qualifier("P585",quals)) for rate,quals in get_quantities("P2219",entity)),key=lambda p: p[1],reverse=True)
        if gdp_rate_list:
            gdp_rate = float(gdp_rate_list[0][0])
            if gdp_rate > 0:
                gdp = mkNP(gdp, mkAdv(w.with_Prep, mkNP(mkNP(aSg_Det,w.growth_3_N), mkAdv(w.of_1_Prep, mkNP(gdp_rate,w.percent_MU)))))
            elif gdp_rate < 0:
                gdp = mkNP(gdp, mkAdv(w.with_Prep, mkNP(mkNP(aSg_Det,w.decline_1_N), mkAdv(w.of_1_Prep, mkNP(-gdp_rate,w.percent_MU)))))
            else:
                pass

        # The gross domestic product is [...] / El producto interno bruto es de [...] / Le produit intérieur brut est de [...]
        verb = copula_number(cnc, gdp)
        phr = mkPhr(mkUtt(mkS(mkCl(mkNP(theSg_Det, w.gross_domestic_product_N), verb))), fullStopPunct)
        yield " " + cnc.linearize(phr)

        median_income = None
        median_income_list = sorted(((median_income,get_time_qualifier("P585",quals) or "X") for median_income,quals in get_quantities("P3529",entity)),key=lambda p: p[1],reverse=True)
        if median_income_list:
            median_income = int(median_income_list[0][0])
            median_income = mkNP(median_income,w.dollar_MU)
            verb = copula_number(cnc, median_income)
            phr = mkPhr(mkUtt(mkCl(mkNP(theSg_Det, mkCN(w.median_3_A, w.income_N)), verb)), fullStopPunct)
            yield " " + cnc.linearize(phr)

        yield "</p>"
