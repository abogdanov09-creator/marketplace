import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'marketplace.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Таблица товаров
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')

    # Таблица комментариев
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Таблица пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Тестовые товары (15 штук)
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            ("Ноутбук Apple MacBook Air M2", "электроника", 1199.99, "8GB RAM, 256GB SSD", 10),
            ("Ноутбук ASUS ROG Strix G16", "электроника", 1499.99, "16GB RAM, 512GB SSD, RTX 4060", 7),
            ("Наушники Sony WH-1000XM5", "электроника", 349.99, "Беспроводные, шумоподавление", 15),
            ("Наушники JBL Tune 510BT", "электроника", 49.99, "Беспроводные, 40 часов работы", 30),
            ("Смартфон Xiaomi Redmi Note 12", "электроника", 299.99, "6.67 дюймов, 128GB", 20),
            ("Смартфон Samsung Galaxy A54", "электроника", 399.99, "6.4 дюйма, 128GB", 12),
            ("Курс Python для начинающих", "образование", 49.99, "45 часов видео, 100+ заданий", 100),
            ("Курс Java с нуля", "образование", 59.99, "60 часов видео, проекты", 85),
            ("Курс JavaScript полный", "образование", 39.99, "30 часов, React, Node.js", 120),
            ("Курс Data Science", "образование", 99.99, "Pandas, NumPy, Matplotlib", 45),
            ("Фитнес-браслет Xiaomi Mi Band 8", "спорт", 39.99, "1.62 дюйма, пульсометр", 50),
            ("Смарт-часы Apple Watch SE", "спорт", 249.99, "GPS, фитнес-трекер", 8),
            ("Фитнес-браслет Huawei Band 7", "спорт", 59.99, "1.47 дюйма, 96 режимов", 25),
            ("Игровая мышь Logitech G502", "аксессуары", 79.99, "11 программируемых кнопок", 30),
            ("Механическая клавиатура Redragon", "аксессуары", 89.99, "Red switches, RGB", 20),
        ]
        for p in products:
            c.execute("INSERT INTO products (name, category, price, description, stock) VALUES (?, ?, ?, ?, ?)", p)

        # Тестовые комментарии
        c.execute("SELECT id FROM products LIMIT 1")
        first_product_id = c.fetchone()[0]
        comments = [
            (first_product_id, "Анна", "Отличный ноутбук! Рекомендую!"),
            (first_product_id, "Максим", "Хороший ноутбук для работы"),
            (first_product_id, "Елена", "Быстрая доставка, спасибо!"),
        ]
        for pid, author, text in comments:
            c.execute("INSERT INTO comments (product_id, author, text) VALUES (?, ?, ?)", (pid, author, text))

    # Создаём тестового админа
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        c.execute('''
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@marketplacer.com', admin_hash, 1))

    conn.commit()
    conn.close()


init_db()