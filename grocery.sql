CREATE DATABASE IF NOT EXISTS grocery_db;
USE grocery_db;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    product_name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    image VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    order_status VARCHAR(30) DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE delivery (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    delivery_address TEXT,
    delivery_status VARCHAR(30) DEFAULT 'Preparing',
    expected_date DATE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

INSERT INTO categories (category_name)
VALUES
('Fruits'),
('Vegetables'),
('Dairy'),
('Beverages'),
('Bakery');

INSERT INTO products (category_id, product_name, description, price, stock, image)
VALUES
(1,'Apple','Fresh Red Apples',120.00,100,'apple.jpg'),
(1,'Banana','Organic Bananas',60.00,120,'banana.jpg'),
(2,'Tomato','Fresh Tomatoes',45.00,150,'tomato.jpg'),
(2,'Potato','Farm Fresh Potatoes',35.00,200,'potato.jpg'),
(3,'Milk','Amul Full Cream Milk',65.00,80,'milk.jpg'),
(3,'Cheese','Cheddar Cheese',180.00,50,'cheese.jpg'),
(4,'Orange Juice','Fresh Juice',150.00,40,'juice.jpg'),
(5,'Bread','Whole Wheat Bread',40.00,75,'bread.jpg');
