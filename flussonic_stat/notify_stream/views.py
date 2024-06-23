from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse


class StatusStreamView(APIView):

    def get(self, request):
        # print(request.data)
        if type(request.data) == list:
            for i in request.data:
                print(i)
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
