from datetime import datetime

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from playhouse.shortcuts import model_to_dict

from config.template import templates
from controllers import case as c_case
from controllers.utils import COUNTRIES
from data_models.case import Case

router = APIRouter()


@router.route('/explore/', include_in_schema=False)
async def explore(request):
    template = "explorer.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@router.get('/load-cases/', include_in_schema=False)
async def get_cases(request: Request):
    def parse_request(params):
        req = {
            'order': {},
            'search': {}
        }
        for k, v in params:
            if k.startswith('order'):
                i = list(map(lambda x: x[:-1], k.split('[')[1:]))
                req['order'][i[1]] = v
            elif k.startswith('search'):
                i = list(map(lambda x: x[:-1], k.split('[')[1:]))
                if i[0] not in req['search']:
                    req['search'][i[0]] = v
            elif not k.startswith('columns'):
                req[k] = v
        return req

    from data_models.base import db
    @db.collation()
    def country_asc(s1, s2):
        return COUNTRIES[s1.split(';')[0]]['name'] < COUNTRIES[s2.split(';')[0]]['name']

    @db.collation()
    def country_desc(s1, s2):
        return -country_asc(s1, s2)

    sorting_map = {
        '0': Case.itemid,
        '2': Case.judgementdate,
        '3': Case.importance,
        '4': Case.docname,
        '5': country_asc.collation(Case.respondent),
        '8': Case.separateopinion
    }

    req = parse_request(request.query_params.items())
    order_col = sorting_map[req['order']['column']].asc()
    if req['order']['dir'] == 'desc':
        order_col = sorting_map[req['order']['column']].desc()
        if req['order']['column'] == '5':
            order_col = country_desc.collation(Case.respondent).desc()
    length = int(req['length'])
    page = (int(req['start']) // length) + 1
    if 'value' in req['search']:
        t = req['search']['value']
        cases = Case.select().where(Case.docname.contains(t)).order_by(order_col).paginate(page, length)
    else:
        cases = Case.select().order_by(order_col).paginate(page, length)
    res = []
    for c in cases:
        articles = []
        list_articles = []
        for p in c.conclusions:
            e = model_to_dict(p)['conclusion']
            if e['article'] not in list_articles:
                list_articles.append(e['article'])
                articles.append(e)
        parties = []
        for p in c.parties:
            parties.append(p.party.name)
        res.append(model_to_dict(c))
        res[-1]['articles'] = articles
        res[-1]['parties'] = parties
        res[-1]['country'] = COUNTRIES[c.respondent.split(';')[0]]
        res[-1]['originatingbody'] = {'name': c.originatingbody_name, 'type': c.originatingbody_type}
        res[-1]['documents'] = c_case.available_documents(c.itemid)
        for k in res[-1]:
            if isinstance(res[-1][k], datetime):
                res[-1][k] = {
                    'display': str(res[-1][k].strftime('%b %d, %Y')),
                    'timestamp': (int(datetime.timestamp(res[-1][k])))
                }
    cases_number = Case.select().count()
    filtered_cases_number = len(list(cases)) if 'value' in req['search'] else cases_number
    return JSONResponse({'data': res, 'recordsTotal': cases_number, 'recordsFiltered': filtered_cases_number})


@router.get('/cases/{itemid}', include_in_schema=False)
async def show_case(request: Request, itemid: str):
    case = c_case.get_case_info(itemid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    template = "case.html"
    context = {"request": request, 'case': case}
    return templates.TemplateResponse(template, context)
