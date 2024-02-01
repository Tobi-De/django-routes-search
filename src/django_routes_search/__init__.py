# SPDX-FileCopyrightText: 2024-present Tobi DEGNON <tobidegnon@proton.me>
#
# SPDX-License-Identifier: MIT

from django.conf import settings
import importlib.util
from pprint import pprint
from thefuzz import fuzz, process  # thefuzz[speedup]

# https://github.com/django-extensions/django-extensions/blob/main/django_extensions/management/commands/show_urls.py

root_url_conf = settings.ROOT_URLCONF

print(root_url_conf)

urls_dict = {}

include_apps = ["reports"]


def parse_urlpatterns(urlpatterns, base="", namespace=None):  #
    urlpatterns
    for entry in urlpatterns:
        if hasattr(entry, "url_patterns"):
            if entry.app_name not in include_apps:
                continue

            parse_urlpatterns(
                entry.url_patterns,
                base=str(entry.pattern),
                namespace=entry.namespace,
            )
        elif hasattr(entry, "callback"):
            if not entry.name:
                continue
            name = f"{namespace}:{entry.name}" if namespace else entry.name
            urls_dict[name] = f"{base}{str(entry.pattern)}"


spec = importlib.util.find_spec(root_url_conf)
url_module = importlib.import_module(spec.name)
if hasattr(url_module, "urlpatterns"):
    parse_urlpatterns(getattr(url_module, "urlpatterns"))

pprint(urls_dict)


def search(term, limit=10):
    term_ = term.lower()
    result = process.extract(term_, urls_dict.keys(), limit=limit)
    return {name: urls_dict[name] for name, _ in result}


pprint(search("report", 5))
