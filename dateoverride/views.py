from django.shortcuts import render_to_response
from django.template import RequestContext
from userservice.user import UserService
from authz_group import Group
from django.conf import settings
from django.http import Http404
from datetime import datetime
import logging
from django import template
from django.contrib.auth.decorators import login_required
from dateoverride.util import get_default_date, set_session_value
from dateoverride.util import get_session_value, clear_session_value
from dateoverride.util import is_valid_datetime_string, get_parse_error
from django.test.client import RequestFactory
from dateutil import tz
import pytz


@login_required
def override(request):
    logger = logging.getLogger(__name__)

    user_service = UserService()
    user_service.get_user()
    override_error_username = None
    override_error_msg = None
    # Do the group auth here.

    if not hasattr(settings, "USERSERVICE_ADMIN_GROUP"):
        print "You must have a group defined as your admin group."
        print 'Configure that using USERSERVICE_ADMIN_GROUP="foo_group"'
        raise Exception("Missing USERSERVICE_ADMIN_GROUP in settings")

    actual_user = user_service.get_original_user()
    if not actual_user:
        raise Exception("No user in session")

    g = Group()
    group_name = settings.USERSERVICE_ADMIN_GROUP
    is_admin = g.is_member_of_group(actual_user, group_name)
    if is_admin is False:
        return render_to_response('no_access.html', {})

    context = {}
    if request.method == "POST":
        _handle_post(request, context)

    try:
        extra_template = "userservice/user_override_extra_info.html"
        template.loader.get_template(extra_template)
        context['has_extra_template'] = True
        context['extra_template'] = 'userservice/user_override_extra_info.html'
    except template.TemplateDoesNotExist:
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    try:
        template.loader.get_template("userservice/user_override_wrapper.html")
        context['wrapper_template'] = 'userservice/user_override_wrapper.html'
    except template.TemplateDoesNotExist:
        context['wrapper_template'] = 'support_wrapper.html'
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    add_session_context(request, context)

    return render_to_response("override.html", context,
                              context_instance=RequestContext(request))


def _handle_post(request, context):
    if request.POST["date"]:
        if is_valid_datetime_string(request.POST["date"]):
            set_session_value(request, request.POST["date"])
        else:
            context["date_error"] = get_parse_error(request.POST["date"])

    else:
        clear_session_value(request)


def add_session_context(request, context):
    override = get_session_value(request)
    if override:
        context["override_date"] = override

    now_request = RequestFactory().get("/")
    now_request.session = {}

    now = datetime.now()
    default = get_default_date()

    used_date = datetime(default.year, default.month, default.day, now.hour,
                         now.minute, now.second)

    context["actual_now_date"] = used_date
