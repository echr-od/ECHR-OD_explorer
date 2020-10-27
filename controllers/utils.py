import json
from os import path

from utils.config import config

df = path.join(config()['data']['data_folder'], config()['data']['build_name'])

DOCS_FOLDERS = {
    'judgment': lambda x: path.join(df, 'raw', 'judgments', '{}.docx'.format(x)),
    'bow': lambda x: path.join(df, 'structured/bow/{}_bow.txt'.format(x)),
    'tfidf': lambda x: path.join(df, 'structured/tfidf/{}_tfidf.txt'.format(x))
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
