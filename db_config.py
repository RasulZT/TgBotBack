import json
import logging
import psycopg2

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname="new2",
    user="postgres",
    password="Aruka2004",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Чтение данных из JSON-файла
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

processed_count = 0  # Счетчик обработанных строк

# Вставка данных в базу данных
for feature in data['features']:
    properties = feature['properties']
    geometry = feature['geometry']
    coordinates = geometry['coordinates'][0]  # Все координаты полигона

    # Преобразование координат в формат JSON
    coordinates_json = json.dumps(coordinates)

    # Формирование SQL-запроса для вставки данных
    sql = "INSERT INTO map (id, housenumber, street, building, levels, roof_shape, coordinates) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(sql, (
            properties['@id'],
            properties.get('addr:housenumber', None),
            properties.get('addr:street', None),
            properties.get('building', None),
            properties.get('building:levels', None),
            properties.get('roof:shape', None),
            coordinates_json  # Вставка координат в виде JSON строки
        ))
        processed_count += 1
    except Exception as e:
        logger.error(f"Error while processing data: {e}")

# Применение изменений и закрытие соединения
conn.commit()
cur.close()
conn.close()

# Вывод информации о количестве обработанных строк
logger.info(f"Processed {processed_count} rows.")
