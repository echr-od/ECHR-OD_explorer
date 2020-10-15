import yaml

from fastapi import FastAPI
from api.api import api
from starlette.staticfiles import StaticFiles
import uvicorn
import os

from utils.config import config
from config.template import templates
from data_models.base import db
from data_models.case import Case
from data_models.article import Article
from data_models.conclusion import Conclusion, ConclusionCase, ConclusionDetail, ConclusionMention
from data_models.detail import Detail
from data_models.mention import Mention
from data_models.party import Party
from data_models.kpthesaurus import KPThesaurus
from data_models.representative import Representative
from data_models.issue import Issue
from data_models.documentcollectionid import DocumentCollectionId
from data_models.extractedappno import ExtractedApp
from data_models.scl import SCL
from data_models.decisionbody import DecisionBodyMember, DecisionBodyCase
from data_models.externalsource import ExternalSource

db_path = os.path.join(config()['data']['data_folder'], 'structured', 'echr-db.db')
print(db_path)
db.init(db_path)

from routes import connect, doc, download, explore, homepage

app = FastAPI(debug=True)
app.mount('/static', StaticFiles(directory='statics'), name='static')
app.mount('/assets', StaticFiles(directory='statics/assets'), name='assets')

app.include_router(homepage.router)
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
