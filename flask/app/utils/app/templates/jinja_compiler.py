# https://jinja.palletsprojects.com/en/3.0.x/extensions/#ast
from jinja2 import Environment
from jinja2.nodes import Template, TemplateData
from typing import List, Dict
from jinja2.nodes import Output, TemplateData, Name

from app.exceptions import BusinessLogicException, ImplementationException


def compile(ast: List[Dict]) -> str:
    # TODO: use jinja2.nodes
    def literal(literal):
        """
        {
            "type": "literal",
            "value": <str>
        }
        """
        return literal["value"]

    def attribute(attribute):
        """
        {
            "type": "attribute",
            "value": EntityAttribute
        }
        """
        return "{{" + attribute["value"] + "}}"

    # { func_name: func } for every nested function in this scope
    func_mapping = {n: f for n, f in locals().items() if callable(f)}

    errors = []
    chunks = []
    for node in ast:
        try:
            if node["type"] not in func_mapping:
                raise BusinessLogicException(
                    f"Unknown node type: {node['type']}", code=400
                )

            chunks.append(func_mapping[node["type"]](node))
        except BusinessLogicException as e:
            errors.append(e)
        except Exception as e:
            errors.append(
                ImplementationException(f"Failed to compile node: {node}: {e}"),
                code=500,
            )

    return "".join(chunks)


def parse(template: str) -> List[Dict]:
    jinja_ast = Environment().parse(template)
    ast = []

    for node in jinja_ast.body:
        if isinstance(node, Output):
            for inner_node in node.nodes:
                if isinstance(inner_node, TemplateData):
                    ast.append({"type": "literal", "value": inner_node.data})
                elif isinstance(inner_node, Name):
                    ast.append({"type": "attribute", "value": inner_node.name})
                else:
                    raise Exception(f"Unknown node type: {type(inner_node)}")
        else:
            raise Exception(f"Unknown node type: {type(node)}")

    return ast
