from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.get_client_ip import get_client_ip


class ConfigView(APIView):

    def post(self, request):
        data = request.data[0]
        print(data)
        ip = get_client_ip(request)
        print(ip)
        return Response(status=status.HTTP_200_OK)
