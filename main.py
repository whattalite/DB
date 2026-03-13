import sqlite3

conn = sqlite3.connect('photo_supplies.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys = ON')

cursor.execute('''
CREATE TABLE IF NOT EXISTS device_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT,
    phone TEXT,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    address TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    type_id INTEGER,
    vendor_id INTEGER,
    base_price DECIMAL(10,2) CHECK(base_price >= 0),
    warranty_months INTEGER,
    service_life_months INTEGER,
    material TEXT,
    description TEXT,
    FOREIGN KEY (type_id) REFERENCES device_types(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS purchase_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_date DATE NOT NULL,
    partner_name TEXT NOT NULL,
    total_amount DECIMAL(12,2) DEFAULT 0 CHECK(total_amount >= 0),
    status TEXT DEFAULT 'new'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS request_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price_per_unit DECIMAL(10,2) NOT NULL CHECK(price_per_unit >= 0),
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (quantity * price_per_unit) STORED,
    FOREIGN KEY (request_id) REFERENCES purchase_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id)
)
''')

print("Таблицы успешно созданы!")

cursor.execute("DELETE FROM request_items")
cursor.execute("DELETE FROM purchase_requests")
cursor.execute("DELETE FROM equipment")
cursor.execute("DELETE FROM vendors")
cursor.execute("DELETE FROM device_types")

cursor.execute("DELETE FROM sqlite_sequence")

device_types_data = [
    ('Серверы', 'Серверное оборудование для ЦОД'),
    ('Рабочие станции', 'Высокопроизводительные ПК'),
    ('МФУ', 'Многофункциональные устройства'),
    ('Фотобумага', 'Расходные материалы для печати'),
    ('Пленка', 'Фотопленка различных форматов'),
    ('Химикаты', 'Реагенты для проявки')
]

cursor.executemany(
    "INSERT INTO device_types (name, description) VALUES (?, ?)",
    device_types_data
)

vendors_data = [
    ('Fujifilm', 'Япония', '+81-3-1234-5678', 5, 'Токио, Япония'),
    ('Kodak', 'США', '+1-585-724-4000', 4, 'Рочестер, Нью-Йорк'),
    ('Ilford', 'Великобритания', '+44-20-1234-5678', 5, 'Лондон, UK'),
    ('HP', 'США', '+1-650-857-1501', 4, 'Пало-Альто, Калифорния'),
    ('Canon', 'Япония', '+81-3-3758-2111', 5, 'Токио, Япония'),
    ('Epson', 'Япония', '+81-3-1234-9876', 4, 'Нагано, Япония')
]

cursor.executemany(
    "INSERT INTO vendors (name, country, phone, rating, address) VALUES (?, ?, ?, ?, ?)",
    vendors_data
)

equipment_data = [
    ('Фотобумага Glossy', 4, 1, 2500.00, 0, 12, 'Целлюлоза', 'Глянцевая фотобумага A4'),
    ('Пленка 35мм', 5, 2, 1200.00, 6, 24, 'Полиэстер', 'Цветная негативная пленка'),
    ('Химикаты (Концентрат)', 6, 1, 4500.00, 3, 6, 'Галогенид серебра', 'Проявитель концентрат'),
    ('Матовая фотобумага', 4, 3, 2300.00, 0, 12, 'Целлюлоза', 'Матовая бумага A3'),
    ('Профессиональная пленка', 5, 1, 1800.00, 6, 24, 'Полиэстер', 'Пленка для студий'),
    ('Фиксаж', 6, 2, 1200.00, 3, 12, 'Галогенид серебра', 'Фиксирующий раствор'),
    ('Сервер DL380', 1, 4, 350000.00, 36, 60, 'Металл/пластик', 'Сервер для ЦОД'),
    ('МФУ LaserJet', 3, 4, 45000.00, 12, 36, 'Пластик/металл', 'Офисное МФУ')
]

cursor.executemany(
    """INSERT INTO equipment 
       (model, type_id, vendor_id, base_price, warranty_months, service_life_months, material, description) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    equipment_data
)

import datetime

today = datetime.date.today()
requests_data = [
    (today.isoformat(), 'Фотолаборатория №1', 0, 'completed'),
    ((today - datetime.timedelta(days=5)).isoformat(), 'Студия Свет', 0, 'processing'),
    ((today - datetime.timedelta(days=10)).isoformat(), 'Профи-Фото', 0, 'new')
]

cursor.executemany(
    "INSERT INTO purchase_requests (request_date, partner_name, total_amount, status) VALUES (?, ?, ?, ?)",
    requests_data
)

cursor.execute("SELECT id FROM purchase_requests ORDER BY id")
request_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id, model, base_price FROM equipment WHERE model IN ('Фотобумага Glossy', 'Пленка 35мм', 'Химикаты (Концентрат)')")
equipment_map = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}

request_items_data = [
    (request_ids[0], equipment_map['Фотобумага Glossy'][0], 20, equipment_map['Фотобумага Glossy'][1]),
    (request_ids[0], equipment_map['Пленка 35мм'][0], 50, equipment_map['Пленка 35мм'][1]),
    (request_ids[0], equipment_map['Химикаты (Концентрат)'][0], 10, equipment_map['Химикаты (Концентрат)'][1]),
]

cursor.executemany(
    "INSERT INTO request_items (request_id, equipment_id, quantity, price_per_unit) VALUES (?, ?, ?, ?)",
    request_items_data
)

for request_id in request_ids:
    cursor.execute('''
        UPDATE purchase_requests 
        SET total_amount = (
            SELECT COALESCE(SUM(subtotal), 0)
            FROM request_items
            WHERE request_id = ?
        )
        WHERE id = ?
    ''', (request_id, request_id))

conn.commit()

print("Тестовые данные успешно загружены!")

print("\n--- Содержимое таблицы vendors ---")
for row in cursor.execute("SELECT * FROM vendors"):
    print(row)

print("\n--- Содержимое таблицы equipment ---")
for row in cursor.execute("SELECT e.id, e.model, dt.name, v.name, e.base_price FROM equipment e JOIN device_types dt ON e.type_id = dt.id JOIN vendors v ON e.vendor_id = v.id"):
    print(row)

print("\n--- Детали заявки №1 ---")
cursor.execute('''
    SELECT e.model, ri.quantity, ri.price_per_unit, ri.subtotal
    FROM request_items ri
    JOIN equipment e ON ri.equipment_id = e.id
    WHERE ri.request_id = ?
''', (request_ids[0],))

total = 0
for row in cursor.fetchall():
    model, qty, price, subtotal = row
    print(f"{model:<20} {qty:>5} {price:>10,.2f} {subtotal:>12,.2f}")
    total += subtotal

print(f"{'ИТОГО:':<39} {total:>12,.2f}")

conn.close()


print("\nГотово! База данных сохранена в файле 'photo_supplies.db'")
