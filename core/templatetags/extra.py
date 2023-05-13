from django import template

register = template.Library()

@register.filter(name='is_admin_area')
def is_admin_area(path):
    admin_area_apps = [
        "group",
        "account",
        "bait",
        "buffer",
        "body",
        "method",
        "barcodeset",
        "migration",
        "sequencingfile",
    ]

    app_name = path.split("/")[1]

    return app_name in admin_area_apps
