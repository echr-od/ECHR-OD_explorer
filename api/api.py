import os

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from playhouse.shortcuts import model_to_dict
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from controllers import build as c_build
from controllers import case as c_case
from controllers import party as c_party
from controllers import representative as c_representative
from controllers import scl as c_scl
from controllers import conclusion as c_conclusion
from schemas.case import Case as sCase
from controllers.utils import DOCS_FOLDERS
from utils.config import config

api = FastAPI(
    title="European Court of Human Rights OpenData API",
    version="1.0.0",
    description="European Court of Human Rights OpenData OpenAPI schema",
    root_path="/api/v1/")

@api.get("/stats")
def get_stats():
    res = list(c_case.get_stats().tuples())
    res = [
        {
            'article': e[0],
            'count': e[2],
            'type': e[1],
        }
        for e in res
    ]
    return JSONResponse([c for c in res])


@api.get('/build/status')
def build_status():
    status = c_build.is_building_in_progress()
    latest_build = c_build.get_latest_build()
    message = 'in progress' if status else latest_build['date']
    color = 'green'
    if status:
        color = 'blue'
    elif latest_build['date'] == 'never built':
        color = 'grey'
    return JSONResponse({"schemaVersion": 1, "label": "Database Update", "message": message, "color": color})


@api.get('/build/update')
def build_history():
    return JSONResponse(c_build.update_build())


@api.get('/build/history')
def build_history():
    return JSONResponse(c_build.get_build_history())


@api.get('/build/latest')
def build_history():
    return JSONResponse(c_build.get_latest_build())


@api.get('/build/current')
def current_build():
    return JSONResponse(c_build.get_current_build())


@api.get('/build/available')
def available_builds():
    return JSONResponse(c_build.list_available_build_with_info())


@api.get('/build/new_build_available')
def new_build_available():
    return JSONResponse(c_build.is_new_build_available())


@api.get('/version')
def get_version():
    return '2.0.0'


@api.get('/cases/{itemid}/docs')
def get_documents(request: Request, itemid: str):
    docs = c_case.available_documents(itemid)
    if not docs:
        raise HTTPException(status_code=404, detail="Case not found")
    return docs


@api.get('/cases/{itemid}/docs/{doctype}')
def get_document(request: Request, itemid: str, doctype: str):
    case = c_case.get_case(itemid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if doctype in DOCS_FOLDERS:
        if os.path.isfile(DOCS_FOLDERS[doctype](itemid)):
            filename = DOCS_FOLDERS[doctype](itemid).split('/')[-1]
            return FileResponse(DOCS_FOLDERS[doctype](itemid), filename=filename)
    elif doctype == 'parsed_judgment':
        return JSONResponse(case.judgment)
    raise HTTPException(status_code=404, detail="Could not find the document")


@api.get("/cases/{itemid}")
def get_case(itemid: str):
    case = c_case.get_case(itemid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    res = model_to_dict(case)
    res['parties'] = []
    for p in case.parties:
        res['parties'].append(p.party.name)
    return res


@api.get("/cases/{itemid}/entities")
def get_entities(itemid: str):
    case = c_case.get_case(itemid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return [model_to_dict(e.entity) for e in case.entities]


@api.get("/cases/{itemid}/citedapps")
def get_citedapps(itemid: str):
    case = c_case.get_case(itemid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return [e.name for e in case.extractedapps]


@api.get("/cases")
def get_cases(page: int = 1, limit: int = 1000):
    cases = list(c_case.get_cases(page, limit))
    res = []
    for c in cases:
        parties = []
        for p in c.parties:
            parties.append(p.party.name)
        res.append(model_to_dict(c))
        res[-1]['parties'] = parties
    return res


@api.get("/parties")
def get_parties():
    parties = c_party.get_parties()
    res = {}
    for party in parties:
        if party.id not in res:
            cases = [c.case.itemid for c in party.cases]
            res[party.id] = model_to_dict(party)
            res[party.id]['cases'] = cases
    return res


@api.get("/parties/{id}")
def get_party(id):
    party = c_party.get_party(id)
    res = model_to_dict(party)
    res['cases'] = [c.case.itemid for c in party.cases]
    return res


@api.get("/representatives")
def get_representatives():
    representatives = list(c_representative.get_representatives())
    res = {}
    for representative in representatives:
        cases = [c.case.itemid for c in representative.representsin]
        if representative.name not in res:
            res[representative.name] = {'cases': cases, 'id': representative.id}
    return res


@api.get("/representatives/{id}")
def get_representative(id):
    representative = c_representative.get_representative(id)
    return {'name': representative.name, 'id': id, 'cases': [c.case.itemid for c in representative.representsin]}


@api.get("/scl")
def get_scls():
    scls = list(c_scl.get_scls())
    res = {}
    for scl in scls:
        cases = [c.case.itemid for c in scl.citedin]
        if scl.name not in res:
            res[scl.name] = {'cases': cases, 'id': scl.id}
    return res


@api.get("/scl/{id}")
def get_scl(id):
    scl = c_scl.get_scl(id)
    return {'name': scl.name, 'id': id, 'cases': [c.case.itemid for c in scl.citedin]}


@api.get("/conclusions")
def get_conclusions():
    conclusions = list(c_conclusion.get_conclusions())
    res = {}
    for conclusion in conclusions:
        cases = [c.case.itemid for c in conclusion.in_cases]
        if conclusion.id not in res:
            res[conclusion.id] = model_to_dict(conclusion)
            res[conclusion.id]['cases'] = cases
    return res


@api.get("/conclusions/{id}")
def get_conclusion(id):
    conclusion = c_conclusion.get_conclusion(id)
    res = model_to_dict(conclusion)

    res['cases'] = [c.case.itemid for c in conclusion.in_cases]
    res['mentions'] = [c.mention.mention for c in conclusion.mentions]
    res['details'] = [c.detail.detail for c in conclusion.details]
    return res
