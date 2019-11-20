from fastapi import APIRouter

from config.template import templates

router = APIRouter()


@router.route('/', include_in_schema=False)
async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)
