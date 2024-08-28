from anvil.js import window


def get_or_create_tag(type):
    tag = window.document.querySelector(type)
    if tag is None:
        tag = window.document.createElement(type)
        tag.textContent = ""
        window.document.head.appendChild(tag)
    return tag


def get_or_create_meta_tag(name):
    tag = window.document.querySelector(f'meta[name="{name}"]')
    if tag is None:
        tag = window.document.createElement("meta")
        tag.setAttribute("name", name)
        tag.setAttribute("content", "")
        window.document.head.appendChild(tag)
    return tag


title_tag = get_or_create_tag("title")
meta_title = get_or_create_meta_tag("title")
meta_title_og = get_or_create_meta_tag("og:title")
meta_description = get_or_create_meta_tag("description")
meta_description_og = get_or_create_meta_tag("og:description")

default_title = title_tag.textContent or meta_title.content
default_description = meta_description.content


def update_meta_tags(meta):
    title = meta.get("title") or default_title
    description = meta.get("description") or default_description
    title_tag.textContent = title
    meta_title.content = title
    meta_title_og.content = title
    window.document.title = title

    meta_description.content = description
    meta_description_og.content = description
