# your_app/templatetags/date_filters.py
from django import template
import datetime

register = template.Library()

@register.filter
def unix_to_date(value):
    if value and isinstance(value, int):
        try:
            return datetime.datetime.utcfromtimestamp(value).strftime('%d.%m.%Y')
        except (OSError, ValueError):
            return "—"
    return "—"