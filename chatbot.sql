-- Create database
CREATE DATABASE IF NOT EXISTS negotiate;
USE negotiate;
DROP TABLE IF EXISTS users;

-- Create users table matching your Flask app (username, password, emailid only)
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50),
    emailid VARCHAR(100)
);

-- Drop and recreate reviews table
DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews (
    username VARCHAR(50),
    review TEXT,
    sentiment VARCHAR(20)
);

-- Drop and recreate purchaseorder table
DROP TABLE IF EXISTS purchaseorder;

CREATE TABLE purchaseorder (
    username VARCHAR(50),
    product_id VARCHAR(20),
    product_name VARCHAR(100),
    amount DECIMAL(10,2),
    transaction_date DATETIME
);