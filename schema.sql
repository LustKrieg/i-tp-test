-- Создание таблиц

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INT REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    item_id INT REFERENCES items(id) ON DELETE CASCADE,
    quantity INT NOT NULL
);

-- Тестовые данные

-- Категории
INSERT INTO categories (name, parent_id) VALUES
('Бытовая техника', NULL),
('Стиралки', 1),
('Холодильники', 1),
('Однокамерные', 3),
('Двухкамерные', 3),
('Телевизоры', 1),
('Компьютеры', NULL),
('Ноутбуки', 7),
('17"', 8),
('19"', 8),
('Моноблоки', 7);

-- Товары
INSERT INTO items (name, quantity, price, category_id) VALUES
('Стиралка Samsung', 10, 35000, 2),
('Холодильник LG однокамерный', 5, 25000, 4),
('Холодильник LG двухкамерный', 3, 45000, 5),
('Телевизор Sony', 7, 55000, 6),
('Ноутбук HP 17"', 8, 60000, 9),
('Ноутбук Acer 19"', 6, 70000, 10),
('Моноблок Dell', 4, 80000, 11);

-- Клиенты
INSERT INTO clients (name, address) VALUES
('ООО Ромашка', 'Москва, ул. Ленина, 1'),
('ИП Иванов', 'Санкт-Петербург, Невский пр., 100');

-- Заказы
INSERT INTO orders (client_id) VALUES
(1),
(2);

-- Позиции заказов
INSERT INTO order_items (order_id, item_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 4, 1),
(2, 5, 3);