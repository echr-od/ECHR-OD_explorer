import json
from os import path

# from app import config

df = 'statics/data/releases'
CURRENT_RELEASE = '2.0.0'

DOCS_FOLDERS = {
    'judgment': lambda x: path.join(df, CURRENT_RELEASE, 'raw/judgments/{}.docx'.format(x)),
    'bow': lambda x: path.join(df, CURRENT_RELEASE, 'structured/bow/{}_bow.txt'.format(x)),
    'tfidf': lambda x: path.join(df, CURRENT_RELEASE, 'structured/tfidf/{}_tfidf.txt'.format(x))
}

COUNTRIES = {}
with open('statics/countries.json') as f:
    data = json.load(f)
    for c in data:
        COUNTRIES[c['alpha-3']] = {
            'alpha2': c['alpha-2'].lower(),
            'name': c['name']
        }

with open('statics/originatingbody.json') as f:
    ORIGINATING_BODY = json.load(f)
