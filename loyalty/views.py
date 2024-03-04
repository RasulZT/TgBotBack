from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from my_auth.authentication import CustomTokenAuthentication
from my_auth.permissions import IsLogined
from .models import Action, Trigger, Payload, Promos
from .serializers import ActionSerializer, TriggerSerializer, PayloadSerializer, PromosSerializer

from django.http import Http404
class ActionListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]
    def get(self, request, format=None):
        actions = Action.objects.all()
        serializer = ActionSerializer(actions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TriggerListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]
    def get(self, request, format=None):
        triggers = Trigger.objects.all()
        serializer = TriggerSerializer(triggers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TriggerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayloadListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]
    def get(self, request, format=None):
        payloads = Payload.objects.all()
        serializer = PayloadSerializer(payloads, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PayloadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActionDetailView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]
    def get_object(self, pk):
        try:
            return Action.objects.get(pk=pk)
        except Action.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        action = self.get_object(pk)
        serializer = ActionSerializer(action)
        return Response(serializer.data)

    def put(self, request, pk):
        action = self.get_object(pk)
        serializer = ActionSerializer(action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        action = self.get_object(pk)
        action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PromosAPIView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]
    def get(self, request, format=None):
        promos = Promos.objects.all()
        serializer = PromosSerializer(promos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PromosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)