from datetime import datetime

SESSION_KEY = "dateoverride_datetime_string"

def get_default_date():
    return datetime.now()

def get_comparison_date(request):
    return get_comparison_datetime(request).date()

def get_comparison_datetime(request):
    return datetime.now()

def set_session_value(request, value):
    request.session[SESSION_KEY] = value

def get_session_value(request):
    if SESSION_KEY in request.session:
        return request.session[SESSION_KEY]

def clear_session_value(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]

def is_valid_datetime_string(value):
    if get_parse_error(value):
        return False
    return True


def get_parse_error(value):
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return
    except Exception as ex:
        return str(ex)

