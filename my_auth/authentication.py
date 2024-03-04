from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserToken


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is not None:
            token = str(token[7:])  # Обрезаем "Bearer " перед токеном
            # Проверяем наличие токена в базе данных
            try:
                user_token = UserToken.objects.get(access_token=token)
                return (user_token.telegram_id, None)  # Возвращаем telegram_id, связанный с токеном
            except UserToken.DoesNotExist:
                raise AuthenticationFailed('Invalid token')  # Если токен не найден, возбуждаем исключение аутентификации
        else:
            return None
