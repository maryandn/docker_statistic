from django.http import HttpResponse

import json

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
@csrf_exempt
def notify(request):
    print(json.loads(request.body))
    return HttpResponse('')
