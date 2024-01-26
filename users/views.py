from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client
from rest_framework.decorators import authentication_classes, permission_classes

from .serializers import ClientSerializer


@authentication_classes([])  # Отключаем аутентификацию
@permission_classes([])  # Отключаем проверку разрешений


class TelegramStartView(APIView):

    def get(self, request, *args, **kwargs):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Получаем данные из запроса
        telegram_id = request.data.get('telegram_id')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        client = Client.objects.filter(telegram_id=telegram_id).first()

        if client:
            # Если пользователь существует, возвращаем "ОК"
            return Response({"detail": "ОК"})

        # Определяем роль автоматически
        role = 'user'  # Ваша логика определения роли

        # Создаем словарь данных для сериализации
        data = {
            'telegram_id': telegram_id,
            'telegram_fullname': f"{first_name} {last_name}",
            'role': role,
            'bonus':1000,
            'blocked': {'status': False}
        }

        # Используем сериализатор для валидации и сохранения данных
        serializer = ClientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

