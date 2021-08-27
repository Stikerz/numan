from typing import Any
from typing import Dict
from typing import List

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from .models import BloodTestResults


class APIClass(View):
    """A parent class that makes it easier to write API views."""

    def dispatch(self, request, *args, **kwargs) -> JsonResponse:
        """Dispatch the request."""
        # Assume that this user is the one we're authenticating as.
        request.user = get_user_model().objects.all()[0]

        # Route the request through the method.
        response = super().dispatch(request, *args, **kwargs)

        # If the response includes an error, set the proper status codes.
        if "error" in response:
            return JsonResponse(response, status=422)
        else:
            return JsonResponse({"data": response})


class APIGeolocation(APIClass):
    def get(self, request) -> Dict[str, Any]:
        """Perform geolocation on a given IP address."""
        ip = request.GET.get("ip")
        # TODO: Write this code here.
        return {"country": "TBD", "city": "TBD"}


class APITestResults(APIClass):
    def get(self, request) -> List[Dict[str, Any]]:
        """Return a list of blood test results for the current user."""
        return [
            btr.to_dict() for btr in BloodTestResults.objects.filter(user=request.user)
        ]


def index(request) -> HttpResponse:
    """The main index view, for prettiness."""
    return render(request, "index.html")
