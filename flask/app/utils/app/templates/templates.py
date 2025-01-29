import re
from typing import List
from jinja2 import Environment, PackageLoader, select_autoescape


def render_from_template_file(template_name: str, **kwargs) -> str:
    env = Environment(loader=PackageLoader("app"), autoescape=select_autoescape())
    template = env.get_template(template_name)
    return template.render(**kwargs)


def render_from_template_string(template: str, **kwargs) -> str:
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(template)
    return template.render(**kwargs)


def extract_jinja_variables(template: str) -> List[str]:
    return re.findall(r"{{\s*([a-zA-Z]\w+?)\s*}}", template)
