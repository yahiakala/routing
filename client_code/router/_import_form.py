import anvil


def get_package_name():
    try:
        return anvil.app.package_name
    except AttributeError:
        from anvil.js.window import anvilAppMainPackage

        return anvilAppMainPackage


def import_form(form, *args, **kws):
    if anvil.is_server_side():
        raise RuntimeError("open_form is not available on the server")

    if isinstance(form, anvil.Component):
        return form

    if not isinstance(form, str):
        raise TypeError(f"expected a form instance or a string, got {form!r}")

    package_name = get_package_name()
    print(package_name)

    mod = __import__(form, {__package__: package_name}, level=-1)
    form_name = form.split(".").pop()

    form_cls = getattr(mod, form_name)

    return form_cls(*args, **kws)
