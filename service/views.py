import json

from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from my_auth.models import CustomUser
from my_auth.permissions import IsLogined
from .models import DeliveryLayers, CompanySpots, Reminder
from .serializers import DeliveryLayersSerializer, CompanySpotsSerializer, ReminderSerializer
from rest_framework.permissions import AllowAny
from django.http import Http404


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
    elif len(search_string.split()) == 3 and search_string.split()[1].isdigit() and not search_string.split()[2].isdigit() :
        # Если строка содержит 3 элемента и второй элемент является числом
        street = search_string.split()[0] +" "+search_string.split()[1]+" "+ search_string.split()[2]
        return street, None
    elif len(search_string.split()) == 3 and search_string.split()[1].isdigit() and search_string.split()[2].isdigit():
        # Если строка содержит 3 элемента и второй элемент является числом
        street = search_string.split()[0] +" "+search_string.split()[1]+" "+ "микрорайон"
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
        housenumber+="%"

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
               """, [street,street, housenumber])
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
    request_data = json.loads(request.body.decode('utf-8')) # Assuming the data is sent via POST request
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
        user_id=str(user_id)
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