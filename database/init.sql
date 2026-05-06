-- 1. Créer la base de données
CREATE DATABASE IF NOT EXISTS forum_db;
USE forum_db;

-- 2. Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table des posts (messages du forum)
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. Table des commentaires
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. Insérer 3 utilisateurs de base
INSERT INTO users (username, password, role) VALUES
    ('marie', 'mariepwd', 'user'),
    ('paul', 'paulpwd', 'user'),
    ('admin', 'adminpwd', 'admin');

-- 6. Insérer quelques posts pour avoir du contenu
INSERT INTO posts (user_id, title, content) VALUES
    (1, 'Bienvenue sur TalkZone', 'Salut tout le monde, premier post !'),
    (2, 'Question technique', 'Quelqu un connait Docker ?'),
    (3, 'Annonce admin', 'Merci de respecter les règles du forum.');