import json
import os
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

from loyalty.serializers import ActionSerializer
from my_auth.models import CustomUser, CustomUserAction
from my_auth.permissions import IsLogined
from my_auth.serializers import CustomUserSerializer, CustomUserActionSerializer
from .models import DeliveryLayers, CompanySpots, Reminder, Integration, Payment
from .serializers import DeliveryLayersSerializer, CompanySpotsSerializer, ReminderSerializer, IntegrationSerializer, \
    PaymentSerializer
from rest_framework.permissions import AllowAny
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
class DeliveryLayersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        delivery_layers = DeliveryLayers.objects.all()
        serializer = DeliveryLayersSerializer(delivery_layers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeliveryLayersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanySpotsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        company_spots = CompanySpots.objects.all()
        serializer = CompanySpotsSerializer(company_spots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySpotsSerializer(data=request.data)
        if serializer.is_valid():
            company_spot = serializer.save()

            # Найти пользователя по telegram_id
            telegram_id = serializer.validated_data['manager'].telegram_id
            print(telegram_id)
            try:
                manager = CustomUser.objects.get(telegram_id=telegram_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with the provided telegram_id does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Обновить роль пользователя на Manager
            manager.role = 'Manager'
            manager.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryLayersDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return DeliveryLayers.objects.get(pk=pk)
        except DeliveryLayers.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        delivery_layers = self.get_object(pk)
        serializer = DeliveryLayersSerializer(delivery_layers)
        return Response(serializer.data)

    def put(self, request, pk):
        delivery_layers = self.get_object(pk)
        serializer = DeliveryLayersSerializer(delivery_layers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delivery_layers = self.get_object(pk)
        delivery_layers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanySpotsDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CompanySpots.objects.get(pk=pk)
        except CompanySpots.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        company_spot = self.get_object(pk)
        serializer = CompanySpotsSerializer(company_spot)
        return Response(serializer.data)

    def put(self, request, pk):
        company_spot = self.get_object(pk)
        serializer = CompanySpotsSerializer(company_spot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        company_spot = self.get_object(pk)
        company_spot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from django.db import connection
from django.http import JsonResponse
import re
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


def parse_search_string(search_string):
    search_string = search_string.lower().strip()

    # Шаблоны для поиска улиц и микрорайонов
    patterns = [
        r'(?P<street>[^\bмикрорайон\b|\bмкр\.?\b]+)(\bмикрорайон\b|\bмкр\.?\b)\s*(?P<number>\d+)(?:-?(?P<suffix>\D*))?',
        # микрорайон 1-й, мкр. 1-й и т.д.
        r'(?P<street>.*?)\s+(микрорайон|мкр\.?)\s+(?P<number>\d+)\s*(?P<suffix>\D*)?',
        r'(?P<street>(\bулица\b|\bпроспект\b|\bул\b)\s*(?P<number>\d+))',  # улица Прокофьева, проспект Райымбека и т.д.
        r'(?P<street>.*?)\s+(?P<number>\d+)\s*(?P<suffix>\D*)?',
        r'(?P<street>.*?)(\d+)(?:\s*(?P<suffix>\D+))?',  # Самал 1 3, Самал 2 и т.д.
    ]

    street = ""
    housenumber = None

    # Проверка для однословных запросов
    if len(search_string.split()) == 1:
        street = search_string  # Если строка состоит из одного слова, оно считается названием улицы или микрорайона
    elif len(search_string.split()) == 3 and search_string.split()[1].isdigit() and not search_string.split()[
        2].isdigit():
        # Если строка содержит 3 элемента и второй элемент является числом
        street = search_string.split()[0] + " " + search_string.split()[1] + " " + search_string.split()[2]
        return street, None
    elif len(search_string.split()) == 3 and search_string.split()[1].isdigit() and search_string.split()[2].isdigit():
        # Если строка содержит 3 элемента и второй элемент является числом
        street = search_string.split()[0] + " " + search_string.split()[1] + " " + "микрорайон"
        return street, search_string.split()[2]
    else:
        for pattern in patterns:
            match = re.search(pattern, search_string)
            if match:
                groups = match.groupdict()
                street = groups.get('street', '').strip()
                number = groups.get('number', '')
                suffix = groups.get('suffix')
                if suffix is not None:
                    suffix = suffix.strip()  # Проверка на None перед вызовом strip()
                if number:
                    housenumber = number + suffix
                break
        else:
            street = search_string

    return street.strip(), housenumber


@csrf_exempt
def get_addresses(request):
    request_data = json.loads(request.body.decode('utf-8'))
    if 'search_string' not in request_data:
        return JsonResponse({'error': 'Search string not provided'}, status=400)

    search_string = request_data['search_string'].lower()
    street, housenumber = parse_search_string(search_string)
    if housenumber:
        housenumber += "%"

    with connection.cursor() as cursor:
        if housenumber:
            cursor.execute("""
                   SELECT CONCAT(m.street, ' ', m.housenumber) AS address,
                          m.building,
                          m.levels,
                          m.roof_shape,
                          m.coordinates,
                           similarity(LOWER(m.street), %s) AS similarity_score
                   FROM map AS m
                   WHERE similarity(LOWER(m.street), %s) > 0.4 AND m.housenumber LIKE %s 
                   ORDER BY similarity_score DESC
               """, [street, street, housenumber])
        else:
            cursor.execute("""
                   SELECT CONCAT(m.street, ' ', m.housenumber) AS address,
                          m.building,
                          m.levels,
                          m.roof_shape,
                          m.coordinates,
                          similarity(LOWER(m.street), %s) AS similarity_score
                   FROM map AS m
                   WHERE similarity(LOWER(m.street), %s) > 0.4
                   ORDER BY similarity_score DESC
               """, [street, street])

        rows = cursor.fetchall()
        addresses = [{
            'address': row[0],
            'building': row[1],
            'levels': row[2],
            'roof_shape': row[3],
            'coordinates': row[4]
        } for row in rows]

    return JsonResponse(addresses, safe=False)


@csrf_exempt
@require_POST
def get_matching_coordinates(request):
    request_data = json.loads(request.body.decode('utf-8'))  # Assuming the data is sent via POST request
    lat = request_data.get('lat')
    long = request_data.get('long')

    if lat is None or long is None:
        return JsonResponse({'error': 'Latitude or longitude is missing'}, status=400)

    try:
        lat = float(lat)
        long = float(long)
    except ValueError:
        return JsonResponse({'error': 'Latitude or longitude is not a valid number'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM map WHERE coordinates::jsonb @> %s::jsonb",
            [f'[[{lat}, {long}]]']
        )
        matching_data = cursor.fetchall()

    matching_results = []
    for row in matching_data:
        matching_results.append({
            'id': row[0],
            'housenumber': row[1],
            'street': row[2],
            'building': row[3],
            'levels': row[4],
            'roof_shape': row[5],
            'coordinates': row[6],
        })

    return JsonResponse(matching_results, safe=False)


class AddressListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user_id = str(user_id)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT address FROM Addresses WHERE user_id = %s",
                [user_id]
            )
            addresses = cursor.fetchall()
        address_dicts = [json.loads(address[0]) for address in addresses]

        # Создаем список словарей с ключом 'address'
        addresses_list = [{'address': address} for address in address_dicts]

        # Возвращаем JSON-ответ
        return JsonResponse(addresses_list, safe=False)


@csrf_exempt
def create_reminder(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        scheduled_time = request.POST.get('scheduled_time')
        user = request.user
        reminder = Reminder.objects.create(user=user, message=message, scheduled_time=scheduled_time)
        return JsonResponse({'status': 'success', 'reminder_id': reminder.id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


class ReminderAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            reminder = get_object_or_404(Reminder, pk=pk)
            serializer = ReminderSerializer(reminder)
        else:
            reminders = Reminder.objects.all()
            serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReminderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        reminder = get_object_or_404(Reminder, pk=pk)
        serializer = ReminderSerializer(reminder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reminder = get_object_or_404(Reminder, pk=pk)
        reminder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_users_by_role_or_company(request):
    role = request.data.get('role')
    company_id = request.data.get('company_id')

    users = CustomUser.objects.all()

    if role:
        users = users.filter(role=role)

    if company_id:
        try:
            company = CompanySpots.objects.get(id=company_id)
            users = users.filter(companies=company)
        except CompanySpots.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserCompaniesAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            # Получение пользователя по telegram_id
            user = CustomUser.objects.get(telegram_id=user_id)
            # Получение связанных компаний (только их ID)
            company_ids = user.companies.values_list('id', flat=True)
            # Возвращаем в виде JSON
            return JsonResponse(list(company_ids), safe=False)
        except CustomUser.DoesNotExist:
            # Если пользователь не найден, возвращаем пустой список
            return JsonResponse([], safe=False)


class CheckUserIdAPIView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        if user_id is None:
            return Response({'error': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        if self.check_user_id_from_json(user_id):
            return Response({'exists': True})
        else:
            return Response({'exists': False})

    def check_user_id_from_json(self, user_id):
        # Откройте и загрузите JSON-файл
        with open('./service/users.json', 'r') as file:
            data = json.load(file)

        # Извлеките список user_ids
        user_ids = data.get('user_ids', [])

        if not isinstance(user_ids, list):
            return False

        return user_id in user_ids

@csrf_exempt  # Отключаем CSRF для упрощения. Используйте с осторожностью в продакшене.
def add_user_id_view(request):
    if request.method == 'POST':
        try:
            # Извлекаем данные из тела запроса
            data = json.loads(request.body)
            user_id = data.get('user_id')

            if not user_id:
                return JsonResponse({'error': 'User ID not provided'}, status=400)

            # Определяем путь к JSON-файлу
            file_path = './service/users.json'

            # Читаем или создаем файл JSON
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {'user_ids': []}  # Если файл поврежден или пустой
            else:
                data = {'user_ids': []}

            # Проверяем формат данных в файле
            if not isinstance(data.get('user_ids', []), list):
                return JsonResponse({'error': 'Invalid format in JSON file'}, status=400)

            # Добавляем новый user_id в список, если его там нет
            if user_id not in data['user_ids']:
                data['user_ids'].append(user_id)

                # Записываем обновленные данные обратно в файл
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Если метод запроса не POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)


class UserActionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        # Получаем пользователя по user_id
        user = get_object_or_404(CustomUser, telegram_id=user_id)

        # Получаем текущее время
        now = timezone.now()
        print(f"{now},\n"
              f"{CustomUserAction.objects.filter(date_start__lte=now,date_end__gte=now)}")
        # Получаем все действия (Action), связанные с пользователем через CustomUserAction
        user_actions = CustomUserAction.objects.filter(
            user=user,
            amount__gt=0,  # amount должно быть больше 0
            date_start__lte=now,  # текущая дата должна быть после date_start
            date_end__gte=now  # текущая дата должна быть до date_end
        )

        actions = [user_action.action for user_action in user_actions]  # Получаем список акций

        # Сериализуем акции
        serializer = ActionSerializer(actions, many=True)

        # Возвращаем ответ
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntegrationCreateView(APIView):
    permission_classes = [AllowAny]  # Защита представления

    def get(self, request):
        login = request.query_params.get('login')
        password = request.query_params.get('password')

        # Проверка наличия логина и пароля
        if not login or not password:
            return Response({"error": "Login and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Пытаемся найти интеграцию по логину
        try:
            integration = Integration.objects.get(login=login)

            # Проверяем правильность пароля
            if check_password(password, integration.password):  # Используйте метод проверки пароля
                # Сериализуем данные интеграции без логина и пароля
                serializer = IntegrationSerializer(integration)
                # Убираем логин и пароль из ответа
                integration_data = serializer.data
                integration_data.pop('login', None)
                integration_data.pop('password', None)

                return Response(integration_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Incorrect password."}, status=status.HTTP_403_FORBIDDEN)

        except Integration.DoesNotExist:
            return Response({"error": "Integration not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        api = request.data.get('api')

        if login and password:
            # Проверяем, существует ли временный пользователь с telegram_id = "-1"
            try:
                temp_user = CustomUser.objects.get(telegram_id="-1")

                # Генерация уникального токена
                token = get_random_string(length=40)  # Создаем случайный токен длиной 40 символов

                # Создаем новый объект интеграции с временным пользователем
                integration = Integration(
                    login=login,
                    password=password,  # Будет зашифровано в модели
                    user=temp_user,  # Используем существующего временного пользователя
                    token=token,  # Используем сгенерированный токен
                    api=api
                )
                integration.save()  # Сохраняем объект в базе данных
            except IntegrityError:
                return Response({"error": "Integration with this login already exists."},
                                status=status.HTTP_400_BAD_REQUEST)

            except CustomUser.DoesNotExist:
                # Если временный пользователь не найден, создаем его
                temp_user = CustomUser.objects.create(
                    telegram_id="-1",  # Используем -1 как временный идентификатор
                    telegram_fullname="Temporary User",  # Можно указать временное имя
                    blocked=True  # Заносим временного пользователя в блокированные
                )

                # Генерация уникального токена
                token = get_random_string(length=40)  # Создаем случайный токен длиной 40 символов

                # Создаем новый объект интеграции с временным пользователем
                integration = Integration(
                    login=login,
                    password=password,  # Будет зашифровано в модели
                    user=temp_user,  # Используем временного пользователя
                    token=token,  # Используем сгенерированный токен
                    api = api
                )
                integration.save()  # Сохраняем объект в базе данных


            # Сериализуем данные и возвращаем респонс
            serializer = IntegrationSerializer(integration)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
class IntegrationDetailView(APIView):
    def get(self, request, pk):
        integration = get_object_or_404(Integration, pk=pk)
        serializer = IntegrationSerializer(integration)
        return Response(serializer.data)

    def put(self, request, pk):
        integration = get_object_or_404(Integration, pk=pk)
        serializer = IntegrationSerializer(integration, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        integration = get_object_or_404(Integration, pk=pk)
        integration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentView(APIView):
    # Получение всех платежей
    permission_classes = [AllowAny]
    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Создание нового платежа
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(APIView):
    # Получение информации о конкретном платеже по order_id
    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    # Обновление данных о платеже
    def put(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Удаление платежа
    def delete(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)