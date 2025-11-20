from django import template

register = template.Library()


@register.filter
def duration_hm(value):
    """
    Convert a total number of minutes into '1h03min', '45min', '2h', etc.
    """
    if value is None:
        return "0min"

    try:
        total = int(value)
    except (TypeError, ValueError):
        return "0min"

    hours = total // 60
    minutes = total % 60

    if hours and minutes:
        return f"{hours}h{minutes:02d}min"
    elif hours:
        return f"{hours}h"
    else:
        return f"{minutes}min"