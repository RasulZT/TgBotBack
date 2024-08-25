import secrets
from datetime import datetime

from django.shortcuts import render

# Create your views here.
# Create your views here.
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from loyalty.models import Promos, UsedPromos
from .authentication import CustomTokenAuthentication
from .models import CustomUser, UserToken, CustomUserAction
from .permissions import IsLogined
from .serializers import CustomUserSerializer

from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        telegram_id = request.data.get('telegram_id')
        promo_token = request.data.get('promo', None)  # Expecting a promo token in the request
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
            created = False
        except CustomUser.DoesNotExist:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                created = True
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if promo_token:
            try:
                promo = Promos.objects.get(token=promo_token)
            except Promos.DoesNotExist:
                return Response({"detail": "Invalid promo code."}, status=status.HTTP_400_BAD_REQUEST)

            if UsedPromos.objects.filter(user=user, promo=promo).exists():
                return Response(CustomUserSerializer(user).data,status=status.HTTP_400_BAD_REQUEST)

            if promo.replace_existing_promo or not user.promo:
                user.promo = promo
                user.save()

            if created or promo.auto_add_on_registration:
                try:
                    customuser_action = CustomUserAction.objects.get(action_id=promo.action.id,
                                                                     user_id=user.telegram_id)
                    # Если объект найден, проверяем его действие
                    if customuser_action.action_id != promo.action.id:
                        CustomUserAction.objects.create(
                            user=user,
                            action=promo.action,
                            amount=promo.amount,
                            date_start=promo.date_start,
                            date_end=promo.date_end,
                            is_active=promo.is_active
                        )
                except CustomUserAction.DoesNotExist:
                    # Если объект не найден, создаем новый
                    CustomUserAction.objects.create(
                        user=user,
                        action=promo.action,
                        amount=promo.amount,
                        date_start=promo.date_start,
                        date_end=promo.date_end,
                        is_active=promo.is_active
                    )
            UsedPromos.objects.create(user=user, promo=promo)
        elif created and not promo_token:
            user.bonus = 1000
            user.save()

        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token) if created else None
        jwt_create_time = refresh.current_time if created else None

        if created:
            user_token = UserToken.objects.create(telegram_id=telegram_id, access_token=jwt_token,
                                                  created_at=jwt_create_time)
            user_token.save()

        response_data = CustomUserSerializer(user).data
        response_data['jwt_token'] = jwt_token
        response_data['jwt_create_time'] = jwt_create_time

        return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)


class UserByTelegramIdAPIView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]

    def handle_error(self, message, status_code):
        return Response({"error": message}, status=status_code)

    def get(self, request, telegram_id, format=None):
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return self.handle_error("User not found", status.HTTP_404_NOT_FOUND)

    def put(self, request, telegram_id, format=None):
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return self.handle_error(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return self.handle_error("User not found", status.HTTP_404_NOT_FOUND)


class UpdateTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        telegram_id = request.data.get('telegram_id')
        if telegram_id is None:
            return Response({"error": "Telegram ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)
        jwt_create_time = refresh.current_time

        user_token = UserToken.objects.get(telegram_id=telegram_id)
        user_token.access_token = jwt_token
        user_token.created_at = jwt_create_time
        user_token.save()

        return Response({
            "jwt_token": jwt_token,
            "jwt_create_time": jwt_create_time
        })
