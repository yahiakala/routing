import anvil


def get_package_name():
    try:
        return anvil.app.package_name
    except Exception:
        from anvil.js.window import anvilAppMainPackage

        return anvilAppMainPackage


def import_module(module_name):
    package_name = get_package_name()

    mod = __import__(module_name, {"__package__": package_name}, level=-1)
    attrs = module_name.split(".")[1:]
    for attr in attrs:
        mod = getattr(mod, attr)
    
    return mod


def import_form(form, *args, **kws):
    if anvil.is_server_side():
        raise RuntimeError("open_form is not available on the server")

    if isinstance(form, anvil.Component):
        return form

    if not isinstance(form, str):
        raise TypeError(f"expected a form instance or a string, got {form!r}")

    mod = import_module(form)
    attrs = form.split(".")
    form_cls = getattr(mod, attrs[-1])

    return form_cls(*args, **kws)