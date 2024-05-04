from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from food.models import Product
from my_auth.authentication import CustomTokenAuthentication
from my_auth.permissions import IsLogined
from rest_framework.permissions import AllowAny
from .models import Action, Trigger, Payload, Promos
from .serializers import ActionSerializer, TriggerSerializer, PayloadSerializer, PromosSerializer

from django.http import Http404
class ActionListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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


class AnalyzeOrderView(APIView):
    permission_classes = [AllowAny]

    def check_free_pizza_three_action(self):
        free_pizza_action = Action.objects.filter(triggers__short_name="free_pizza_three").first()
        return free_pizza_action
    def post(self, request, *args, **kwargs):
        order_data = request.data
        category_count = {}

        # Итерация по продуктам заказа для подсчета количества продуктов в каждой категории
        for item in order_data['products']:
            product_id = item['product']
            product = Product.objects.get(id=product_id)
            category = product.category.name

            # Увеличение количества продуктов в категории
            category_count[category] = category_count.get(category, 0) + 1

        for category, count in category_count.items():
            if(category=="Пицца") and count==3:
                action = self.check_free_pizza_three_action()
                order_data['action'] = {
                    'id': action.id,
                }
                return Response(order_data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Акция не найдена'}, status=status.HTTP_404_NOT_FOUND)

        return Response(order_data, status=status.HTTP_200_OK)

