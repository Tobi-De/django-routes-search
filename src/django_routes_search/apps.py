from django.apps import AppConfig


class RoutesSearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "routes_search"

    def ready(self):
        from .search import load_from_apps, load_from_registry
        from django.conf import settings

        if getattr(settings, "SEARCH_ROUTES_LOADER", "apps") == "apps":
            load_from_apps()
        else:
            load_from_registry()
