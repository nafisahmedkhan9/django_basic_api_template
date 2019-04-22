from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate
def is_user_authenticated(function):
    def wrap(request, *args, **kwargs):
        account = authenticate(request)
        if account != None:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            return JsonResponse({"success" : False, "error" : "auth error"})
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
