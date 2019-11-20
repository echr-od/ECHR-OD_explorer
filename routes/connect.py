from fastapi import APIRouter

from config.template import templates

router = APIRouter()


@router.route('/connect/', include_in_schema=False)
async def download(request):
    template = "connect.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)
