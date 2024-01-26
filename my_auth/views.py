import secrets

from django.shortcuts import render

# Create your views here.
# Create your views here.
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

from .models import User
from .serializers import UserSerializer


# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        # Получаем данные из запроса, не включая курсы
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({"Успешная регистрация"})

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.META['HTTP_AUTHORIZATION'].split()
        user = Token.objects.get(key=token[1]).user
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomToken
from .serializers import CustomTokenSerializer


class CustomTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Генерируем уникальный токен
        name = request.data.get('name')
        generated_token = secrets.token_urlsafe(8)
        print(name,generated_token)
        # Создаем объект CustomToken с сгенерированным токеном
        data = {
            'name': name,
            'key': generated_token,
        }
        serializer = CustomTokenSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'token': generated_token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        token_id = kwargs.get('pk')
        try:
            token = CustomToken.objects.get(id=token_id)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomToken.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
