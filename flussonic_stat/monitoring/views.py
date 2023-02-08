from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class AstraMonitoringView(APIView):

    def post(self, request, *args, **kwargs):
        result = {}
        print(request)
        return Response(result, status.HTTP_200_OK)
