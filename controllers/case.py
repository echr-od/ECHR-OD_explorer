from datetime import datetime
import os
import re

from playhouse.shortcuts import model_to_dict

from controllers.utils import COUNTRIES, DOCS_FOLDERS
from data_models.case import Case


def get_cases(page: int = 1, limit: int = 100):
    return Case.select().paginate(page, limit)


def get_case(itemid: str):
    return Case.get_by_id(itemid)


def get_case_info(itemid: str):
    case = get_case(itemid)
    if not case:
        return None
    articles = []
    list_articles = []
    for p in case.conclusions:
        e = model_to_dict(p)['conclusion']
        if e['article'] not in list_articles:
            list_articles.append(e['article'])
            articles.append(e)
    parties = []
    for p in case.parties:
        parties.append(p.party.name)
    scl = []
    for p in case.scl:
        scl.append(p.scl.name)
    representedby = []
    for p in case.representedby:
        representedby.append(p.representative.name)
    extractedapps = []
    for p in case.extractedapps:
        extractedapps.append(p.name)
    decisionbody = []
    for m in case.decisionbody:
        decisionbody.append(model_to_dict(m.member))
    res = model_to_dict(case)
    res['articles'] = articles
    res['conclusions'] = articles
    res['parties'] = parties
    res['representedby'] = representedby
    res['extractedapps'] = extractedapps
    res['scl'] = scl
    res['decisionbody'] = decisionbody
    res['country'] = COUNTRIES[case.respondent.split(';')[0]]
    res['originatingbody'] = {'name': case.originatingbody_name, 'type': case.originatingbody_type}
    res['documents'] = available_documents(case.itemid)
    res['judgment'] = process_judgement_content(res)
    res['rank'] = float(res['rank'])
    res['respondentOrderEng'] = int(res['respondentOrderEng'])
    for k in res:
        if isinstance(res[k], datetime):
            res[k] = str(res[k].strftime('%Y-%m-%d'))
    return res


def available_documents(itemid: str):
    case = get_case(itemid)
    if not case:
        return None
    res = {}
    for t, f in DOCS_FOLDERS.items():
        if os.path.isfile(f(itemid)):
            res[t] = {
                'available': True,
                'uri': '/api/v1/cases/{}/docs/{}'.format(itemid, t)
            }
        else:
            res[t] = {'available': False}
    res['parsed_judgment'] = {
        'available': True,
        'uri': '/api/v1/cases/{}/docs/{}'.format(itemid, 'parsed_judgment')
    }
    return res


def process_judgement_content(case):
    elements = case['judgment']
    apps = case['extractedapps']

    def modify_tree(elements, apps):
        for e in elements:
            if not e['elements']:
                for app in apps:
                    e['content'] = re.sub(app,
                                          '<mark class="cited-app" id="{id}"><a href="/apps/{id}/">{app}</a></mark>'.format(
                                              id=app.replace(' ', '_').replace('/', '_').lower(), app=app),
                                          e['content'])
            e['elements'] = modify_tree(e['elements'], apps)
        return elements

    return modify_tree(elements, apps)
