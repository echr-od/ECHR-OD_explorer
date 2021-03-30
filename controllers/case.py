from datetime import datetime
import os
import re
from spacy import displacy
from playhouse.shortcuts import model_to_dict
from bs4 import BeautifulSoup
from controllers.utils import COUNTRIES, DOCS_FOLDERS
from echr.data_models.case import Case
from echr.data_models.conclusion import ConclusionCase, Conclusion
from echr.data_models.entity import Entity
from echr.data_models.attachment import Table
from peewee import fn
from json2html import *


def get_cases(page: int = 1, limit: int = 100):
    return Case.select().paginate(page, limit)


def get_case(itemid: str):
    return Case.get_by_id(itemid)


def get_stats():
    res = Case.select(Conclusion.article, Conclusion.type, fn.COUNT(Case.itemid)).join(ConclusionCase)\
        .join(Conclusion)\
        .where(Conclusion.article != None)\
        .group_by(Conclusion.base_article, Conclusion.type)

    return res


def get_cases_per_country():
    query = list(Case.select(Case.respondent, fn.COUNT(Case.respondent)).group_by(Case.respondent).tuples())
    res = {}
    for c in query:
        for e in c[0].split(';'):
            country = COUNTRIES[e]['name']
            res[country] = res.get(country, 0) + c[1]
    return res


def get_cases_number():
    res = Case.select(Case.itemid).count()
    return res


def get_case_info(itemid: str, with_html=False):
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
    res['rank'] = float(res['rank'])
    res['respondentOrderEng'] = int(res['respondentOrderEng'])
    for k in res:
        if isinstance(res[k], datetime):
            res[k] = str(res[k].strftime('%Y-%m-%d'))
    if with_html:
        import re
        re_prefix = re.compile(r"^\d+\.?")
        def assign_html(node):
            ents = node.get('metadata', {}).get('ents')
            if ents:
                if not node['elements']:
                    text = node['content']
                    html = displacy.render([{'ents': ents, 'text': text}], style="ent", page=True,
                                               manual=True)
                    soup = BeautifulSoup(html, 'html.parser')
                    node['html'] = '\n'.join([str(e) for e in soup.div.contents])

            for j, e in enumerate(node['elements']):
                node['elements'][j] = assign_html(e)
            return node

        tables = Table.select().where(Table.case == case.itemid)
        table_map = {}
        for table in tables:
            table_map[table.tag] = table.content
        for i, part in enumerate(res['judgment']):
            res['judgment'][i] = assign_html(part)
    res['judgment'] = process_judgement_content(res, table_map)
    res['tables'] = table_map
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


def json_table_to_html(table, tag):
    return json2html.convert(table, table_attributes="id=\"{}\" class=\"judgment-table\"".format(tag))


def process_judgement_content(case, tables=None, content_key='content'):
    elements = case['judgment']
    apps = case['extractedapps']

    def modify_tree(elements, apps, tables=None):
        for e in elements:
            if not e['elements']:
                key = 'html' if 'html' in e else 'content'
                if tables and e[key].startswith('table') and e[key] in tables:
                    table = tables.get(e[key])
                    if table:
                        e['html'] = json_table_to_html(table, e[key])
                for app in apps:
                    e[key] = re.sub(app,
                                          '<mark class="cited-app" id="{id}"><a href="/apps/{id}/">{app}</a></mark>'.format(
                                              id=app.replace(' ', '_').replace('/', '_').lower(), app=app),
                                          e[key])
            e['elements'] = modify_tree(e['elements'], apps, tables)
        return elements

    return modify_tree(elements, apps, tables)
