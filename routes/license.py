from fastapi import APIRouter

from config.template import templates

router = APIRouter()

@router.route('/license', include_in_schema=False)
async def license(request):
    template = "license.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)
