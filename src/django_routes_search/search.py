from thefuzz import process
from collections import defaultdict
from django.conf import settings
import importlib.util
from django.urls import path
from django.apps import apps as django_apps


__all__ = [
    "search",
    "urls_dict",
    "urls_tree",
    "load_from_apps",
    "load_from_registry",
    "s_path",
]

urls_dict = {}
urls_tree = defaultdict(dict)


def search(term, limit=10):
    term_ = term.lower()
    result = process.extract(term_, urls_dict.keys(), limit=limit)
    return {name: urls_dict[name] for name, _ in result}


def load_from_registry():
    pass


def s_path(route, view, kwargs=None, name=None):
    p = path(route, view, kwargs, name)
    urls_dict[name] = p.pattern
    return p


def load_from_apps():
    include_apps = getattr(settings, "SEARCH_ROUTES_APPS", settings.INSTALLED_APPS)
    for app in django_apps.get_app_configs():
        if app.name not in include_apps:
            continue

        spec = importlib.util.find_spec(f"{app.name}.urls")
        if not spec:
            continue

        url_module = importlib.import_module(spec.name)
        if urlpatterns := getattr(url_module, "urlpatterns", None):
            _parse_urlpatterns(urlpatterns)


def _parse_urlpatterns(urlpatterns, base="", namespace=None):
    for entry in urlpatterns:
        if hasattr(entry, "url_patterns"):
            if namespace:
                urls_tree[namespace] = {}

            _parse_urlpatterns(
                entry.url_patterns,
                base=f"{base}{str(entry.pattern)}",
                namespace=entry.namespace,
            )
        elif hasattr(entry, "callback"):
            if not entry.name or entry.pattern.converters:
                continue

            name = f"{namespace}:{entry.name}" if namespace else entry.name
            path = f"{base}{str(entry.pattern)}"
            urls_dict[name] = path
            if namespace:
                urls_tree[namespace][entry.name] = path
            else:
                urls_tree[name] = path
