-- Announce Table
CREATE TABLE IF NOT EXISTS Announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    content TEXT NOT NULL,
    footnote TEXT,
    CONSTRAINT fk_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);