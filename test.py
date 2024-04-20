import json
from math import radians, sin, cos, sqrt, atan2

def distance(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c  # Radius of Earth in kilometers
    return distance

def find_nearest_coordinate(coordinates, lat, long):
    min_distance = float('inf')
    nearest_coordinate = None
    for coord in coordinates:
        dist = distance(lat, long, coord[1], coord[0])
        if dist < min_distance:
            min_distance = dist
            nearest_coordinate = coord
    return nearest_coordinate

# Пример использования
request_body = {
    "lat": 76.8433318,
    "long": 43.2319822
}
lat = request_body['lat']
long = request_body['long']

# Предполагаем, что coordinates это список координат из запроса
coordinates = [[[76.944544, 43.2649913], [76.9444003, 43.2649812], [76.9444435, 43.2646561], [76.9445871, 43.2646662], [76.944544, 43.2649913]]]

nearest_coordinate = find_nearest_coordinate(coordinates[0], lat, long)
print(nearest_coordinate)  # Выведет координату ближайшую к заданным lat и long
