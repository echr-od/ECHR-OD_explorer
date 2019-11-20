import re

from jinja2 import Markup
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')


def regex_replace(s, find, replace):
    return Markup(re.sub(find, replace, s))


templates.env.filters['regex_replace'] = regex_replace
