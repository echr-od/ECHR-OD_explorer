import yaml

from fastapi import FastAPI
from api.api import api
from starlette.staticfiles import StaticFiles
import uvicorn
import os

from utils.config import config
from config.template import templates
from echr.data_models.base import db
from echr.data_models.case import Case
from echr.data_models.detail import Detail
from echr.data_models.party import Party
from echr.data_models.kpthesaurus import KPThesaurus
from echr.data_models.issue import Issue
from echr.data_models.documentcollectionid import DocumentCollectionId
from echr.data_models.extractedappno import ExtractedApp
from echr.data_models.scl import SCL
from echr.data_models.decisionbody import DecisionBodyMember, DecisionBodyCase
from echr.data_models.externalsource import ExternalSource

db_path = os.path.join(config()['data']['data_folder'], config()['data']['build_name'], 'structured', 'echr-db.db')
db.init(db_path)

from routes import connect, doc, download, explore, homepage, license

app = FastAPI(debug=True)
app.mount('/static', StaticFiles(directory='statics'), name='static')
app.mount('/assets', StaticFiles(directory='statics/assets'), name='assets')

app.include_router(homepage.router)
app.include_router(license.router)
app.include_router(explore.router)
app.include_router(download.router)
app.include_router(connect.router)
app.include_router(doc.router)

app.mount("/api/v1", api)


@app.route('/error', include_in_schema=False)
async def error(request):
    """
    An example error. Switch the `debug` setting to see either tracebacks or 500 pages.
    """
    raise RuntimeError("Oh no")


@app.exception_handler(404)
async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8005, proxy_headers=True, forwarded_allow_ips='*')
