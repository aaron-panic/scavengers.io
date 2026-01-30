-- Users Table - not to be exposed!
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'user', 'social') DEFAULT 'social',
    status ENUM('active', 'requested', 'suspended', 'banned') NOT NULL DEFAULT 'requested',
    suspended_until TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
