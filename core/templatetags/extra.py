from django import template

register = template.Library()

@register.filter(name='is_admin_area')
def is_admin_area(path):
    """
    Checks if a django application is located in the admin area. If the application is located in the admin area, some content in master.html will not be visible.
    """
    admin_area_apps = [
        "group",
        "account",
        "bait",
        "buffer",
        "areatype",
        "body",
        "method",
        "barcodeset",
        "migration",
        "sequencingfile",
        "gene",
        "wiki",
        "analysisrun",
        "cns",
        "qc",
    ]

    app_name = path.split("/")[1]

    return app_name in admin_area_apps
