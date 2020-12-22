from fastapi import APIRouter

from config.template import templates
from controllers.build import get_latest_build
from controllers.case import get_cases_number

router = APIRouter()


@router.route('/', include_in_schema=False)
async def homepage(request):
    latest_build = get_latest_build()
    cases_number = get_cases_number()
    build = {
        'date': latest_build['date'],
        'cases': cases_number
    }
    template = "index.html"
    context = {"request": request, 'build': build}
    return templates.TemplateResponse(template, context)
