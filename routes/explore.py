from datetime import datetime

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from playhouse.shortcuts import model_to_dict

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.palettes import Category20c, brewer, Turbo256
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.embed import components
from math import pi
import pandas as pd

from config.template import templates
from controllers import case as c_case
from controllers.utils import COUNTRIES
from echr.data_models.case import Case

router = APIRouter()


@router.route('/charts/', include_in_schema=False)
async def charts(request):
    template = "charts.html"

    res = list(c_case.get_stats().tuples())
    violation = {e[0]: e[2] for e in res if e[1] == 'violation'}
    no_violation = {e[0]: e[2] for e in res if e[1] == 'no-violation'}
    articles = list(set(list(violation.keys()) + list(no_violation.keys())))
    count_violation = [violation.get(k, 0) for k in articles]
    count_no_violation = [no_violation.get(k, 0) for k in articles]

    labels = ["no-violation", "violation"]
    colors = ["#718dbf", "#e84d60"]

    data = {'articles': articles,
            'no-violation': count_no_violation,
            'violation': count_violation}

    p = figure(x_range=articles, plot_height=250, title="Cases per article", sizing_mode='stretch_width', #plot_width='100',
               toolbar_location=None, tools="hover", tooltips="$name @articles: @$name")

    p.vbar_stack(labels, x='articles', width=0.9, color=colors, source=data, legend_label=labels)
    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"

    script, div = components(p)
    graph = {
        'script': script,
        'div': div
    }

    source = ColumnDataSource(data)
    columns = [
        TableColumn(field="articles", title="Article"),
        TableColumn(field="violation", title="Violation"),
        TableColumn(field="no-violation", title="No Violation")
    ]
    data_table = DataTable(source=source, columns=columns, width=200, height=280, index_position=None)
    script, div = components(data_table)
    table = {
        'script': script,
        'div': div
    }


    case_per_country = c_case.get_cases_per_country()
    number_of_countries = 10
    data = pd.Series(case_per_country).reset_index(name='value').rename(columns={'index': 'country'})\
        .sort_values('value', ascending=False)
    data['pct'] = ((data['value'] / data['value'].sum()) * 100).round(2).astype(str) + '%'
    part_data = data[:number_of_countries]
    part_data['angle'] = part_data['value'] / data['value'].sum() * 2 * pi
    part_data['color'] = Category20c[len(part_data)]

    p = figure(plot_height=350, title=f"Top {number_of_countries} countries with most cases judged by the ECHR",
               toolbar_location=None,
               tools="hover", tooltips="@country: @value (@pct)", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=part_data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    script, div = components(p)
    pie = {
        'script': script,
        'div': div
    }

    source = ColumnDataSource(data)
    columns = [
        TableColumn(field="country", title="Country"),
        TableColumn(field="value", title="Cases"),
        TableColumn(field="pct", title="%")
    ]
    data_table = DataTable(source=source, columns=columns, height=280, index_position=None)
    script, div = components(data_table)
    table2 = {
        'script': script,
        'div': div
    }

    context = {"request": request, "context": {'graph': graph, 'table': table, 'pie': pie, 'table2': table2}}
    return templates.TemplateResponse(template, context)



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

    from echr.data_models.base import db
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
    if 'value' in req['search'] and req['search']['value']:
        t = req['search']['value']
        cases = Case.select().where(Case.docname.contains(t)).order_by(order_col)
        filtered_cases = cases.count()
        cases = cases.paginate(page, length)
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
    filtered_cases_number = filtered_cases if 'value' in req['search'] and req['search']['value'] else cases_number
    return JSONResponse({'data': res, 'recordsTotal': cases_number, 'recordsFiltered': filtered_cases_number})


@router.get('/cases/{itemid}', include_in_schema=False)
async def show_case(request: Request, itemid: str):
    case = c_case.get_case_info(itemid, with_html=True)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")


    template = "case.html"
    context = {"request": request, 'case': case}
    return templates.TemplateResponse(template, context)
