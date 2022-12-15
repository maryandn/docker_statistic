from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class StatusStreamView(APIView):

    def post(self, request):
        print(request.data)
        return Response(status.HTTP_200_OK)
