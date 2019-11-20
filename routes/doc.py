from fastapi import APIRouter

router = APIRouter()


@router.route('/doc/', include_in_schema=False)
async def documentation(request):
    template = "doc.html"
    context = {"request": request}
    from app import templates
    return templates.TemplateResponse(template, context)
