from app.utils.app.urls import get_backoffice_url_for_entity


def get_text_node(value):
    return {"type": "text", "value": value}


def get_entity_link_label(entity):
    # from app.api.database.permissions import User
    # from app.api.database.tasks import Task, TaskTemplate, Project, ProjectTemplate

    # title
    # if isinstance(entity, User):
    #     return entity.name

    # if (
    #     isinstance(entity, Task)
    #     or isinstance(entity, TaskTemplate)
    #     or isinstance(entity, Project)
    #     or isinstance(entity, ProjectTemplate)
    # ):
    #     return f"{entity.label} - {entity.title}"

    if hasattr(entity, "label") and entity.label is not None:
        return entity.label
    if hasattr(entity, "title"):
        return entity.title
    if hasattr(entity, "name") and entity.name is not None:
        return entity.name
    return str(entity)


def get_link_node(entity, label=None):
    from app.utils.database import get_discriminator

    from app.utils.services import get_generic_entity

    if entity.__class__.__name__ == "ZombieModel":
        real_entity = get_generic_entity(get_discriminator(entity.model), entity.id)
        if real_entity is not None:
            entity = real_entity
        else:
            return get_text_node(label)

    if label is None:
        label = get_entity_link_label(entity)

    return {
        "type": "link",
        "ref": get_discriminator(entity.__class__),
        "id": entity.id,
        "label": label,
    }


def get_entity_link_node(entity):
    label = f"#{entity.id} - {entity.__class__.__name__.capitalize()}"

    if hasattr(entity, "label"):
        label = entity.label

    if hasattr(entity, "title"):
        label = entity.title

    return get_link_node(entity, label)


def get_tag_node(label, color="#d9d9d9"):
    return {
        "type": "tag",
        "label": label,
        "color": color,
    }


def rich_text_to_html(rich_text):
    html = []

    if not isinstance(rich_text, list):
        return rich_text

    for node in rich_text:
        if node["type"] == "text":
            # Text node with styling
            text_html = (
                f'<span style="color: black; font-weight: bold;">{node["value"]}</span>'
            )
            html.append(text_html)
        elif node["type"] == "link":
            # Link node with styling
            link_html = f'<a href="{get_backoffice_url_for_entity(node["ref"],node["id"])}" style="text-decoration: none; color: blue; font-weight: bold; padding: 0.5rem 1rem; border-radius: 0.5rem;">{node["label"]}</a>'
            html.append(link_html)

    return "".join(html)


def rich_text_to_text(rich_text):
    text = []

    if not isinstance(rich_text, list):
        return rich_text

    for node in rich_text:
        if node["type"] == "text":
            # Text node with styling
            if node["value"] is not None:

                text.append(node["value"])
        elif node["type"] == "link":
            # Link node with styling
            if node["label"] is not None:
                text.append(node["label"])
        else:
            print(f"Unknown node type: {node['type']}", flush=True)
    return "".join(text)
