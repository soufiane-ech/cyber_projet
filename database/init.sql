-- ============================================
-- TalkZone Forum -- Base de donnees
-- ============================================

CREATE DATABASE IF NOT EXISTS forum_db;
USE forum_db;

-- 1. Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) DEFAULT '',
    bio TEXT DEFAULT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table des posts (messages du forum)
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Table des commentaires
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- Donnees de test
-- ============================================

-- Utilisateurs (memes credentials qu avant + nouveaux)
INSERT INTO users (username, password, email, bio, role) VALUES
    ('marie', 'mariepwd', 'marie@talkzone.com', 'Passionnee de cybersecurite et developpement web. Etudiante en 4eme annee.', 'user'),
    ('paul', 'paulpwd', 'paul@talkzone.com', 'Developpeur backend, fan de Docker et Linux.', 'user'),
    ('admin', 'adminpwd', 'admin@talkzone.com', 'Administrateur du forum TalkZone. Contactez-moi pour tout probleme.', 'admin'),
    ('sarah', 'sarahpwd', 'sarah@talkzone.com', 'Etudiante en securite des reseaux. J''adore le CTF !', 'user'),
    ('lucas', 'lucaspwd', 'lucas@talkzone.com', 'Pentester junior, curieux de tout.', 'user');

-- Posts varies couvrant plusieurs categories
INSERT INTO posts (user_id, title, content, category) VALUES
    (1, 'Bienvenue sur TalkZone !', 'Salut tout le monde ! Je suis ravie de rejoindre ce forum. N''hesitez pas a vous presenter ici et a partager vos centres d''interet. Ce forum est un espace d''echange pour tous les passionnes de tech et de cybersecurite. Bonne discussion a tous !', 'General'),
    (2, 'Docker : les commandes essentielles a connaitre', 'Voici un recap des commandes Docker que j''utilise au quotidien :\n\n- docker build -t monimage .\n- docker run -d -p 8080:80 monimage\n- docker-compose up --build\n- docker ps / docker logs\n\nN''hesitez pas a ajouter les votres en commentaire !', 'Technique'),
    (3, 'Regles du forum -- A lire obligatoirement', 'Bonjour a tous,\n\nVoici les regles a respecter sur TalkZone :\n\n1. Restez respectueux envers les autres membres\n2. Pas de spam ni de publicite\n3. Les contenus illegaux sont interdits\n4. Utilisez les bonnes categories pour vos posts\n5. Signalez tout comportement inapproprie\n\nMerci de votre cooperation !\n-- L''equipe TalkZone', 'General'),
    (3, 'Mise a jour de securite -- Mai 2026', 'Nous avons effectue une mise a jour de securite sur le serveur. Si vous rencontrez des problemes de connexion, veuillez vider votre cache et vous reconnecter.\n\nMerci de votre patience.', 'Annonces'),
    (4, 'Mon premier CTF -- Retour d''experience', 'J''ai participe a mon premier CTF (Capture The Flag) ce weekend ! C''etait incroyable. J''ai reussi 5 challenges sur 12, principalement en web et en cryptographie.\n\nConseils pour les debutants :\n- Commencez par les challenges web (XSS, SQLi)\n- Apprenez a utiliser Burp Suite\n- Pratiquez sur HackTheBox ou TryHackMe\n\nQui d''autre fait du CTF ici ?', 'Cybersecurite'),
    (5, 'Les meilleures ressources pour apprendre le pentesting', 'Salut la communaute !\n\nJe compile une liste de ressources gratuites pour apprendre le pentesting :\n\nLivres : "The Web Application Hacker''s Handbook"\nSites : OWASP, PortSwigger Academy, HackTheBox\nYouTube : IppSec, John Hammond, LiveOverflow\nOutils : Burp Suite, Nmap, Metasploit, Wireshark\n\nAjoutez vos recommandations !', 'Cybersecurite'),
    (1, 'Flask vs Django -- Quel framework choisir ?', 'Je travaille sur un projet web et j''hesite entre Flask et Django.\n\nFlask :\n+ Leger et flexible\n+ Facile a apprendre\n- Moins de fonctionnalites built-in\n\nDjango :\n+ Batteries included (ORM, admin, auth)\n+ Ideal pour les gros projets\n- Plus lourd et opinionne\n\nVous utilisez quoi pour vos projets ?', 'Technique'),
    (2, 'Securiser une API REST -- Bonnes pratiques', 'Voici les bonnes pratiques que j''applique pour securiser mes APIs :\n\n1. Toujours utiliser HTTPS\n2. Implementer un rate limiting\n3. Valider toutes les entrees cote serveur\n4. Utiliser des tokens JWT avec expiration courte\n5. Ne jamais exposer les erreurs internes\n6. Mettre en place du CORS correctement\n\nD''autres suggestions ?', 'Technique'),
    (4, 'Presentation -- Sarah', 'Hello ! Je suis Sarah, etudiante en cybersecurite. Je suis passionnee par le ethical hacking et les CTF. Ravie de rejoindre TalkZone pour echanger avec vous tous !', 'General'),
    (5, 'Veille techno -- Les tendances cybersecurite 2026', 'Les grandes tendances cybersecurite de cette annee :\n\n- IA et detection des menaces\n- Zero Trust Architecture\n- Securite du cloud multi-provider\n- Attaques supply chain en hausse\n- Reglementation renforcee (NIS2, DORA)\n\nQuel sujet vous interesse le plus ?', 'Cybersecurite');

-- Commentaires repartis sur les posts
INSERT INTO comments (post_id, user_id, content) VALUES
    (1, 2, 'Bienvenue Marie ! Content de te voir ici. Le forum a l''air super prometteur !'),
    (1, 4, 'Salut ! Moi c''est Sarah, j''espere qu''on va bien echanger ici.'),
    (1, 3, 'Bienvenue a tous ! N''hesitez pas a poser vos questions.'),
    (2, 1, 'Super recap Paul ! J''ajouterais docker exec -it container_name bash pour acceder au shell.'),
    (2, 5, 'Merci ! Et docker system prune pour nettoyer les images inutilisees.'),
    (2, 4, 'Je decouvre Docker, ce post tombe a pic !'),
    (3, 1, 'Bien note ! Merci pour ces regles claires.'),
    (3, 2, 'Parfait, je suis d''accord avec tout ca.'),
    (5, 1, 'Bravo Sarah ! 5/12 pour un premier CTF c''est excellent !'),
    (5, 2, 'Je recommande aussi PicoCTF pour debuter, les challenges sont tres bien faits.'),
    (5, 5, 'J''ai commence avec TryHackMe et c''est vraiment top pour les debutants.'),
    (6, 4, 'PortSwigger Academy est de loin la meilleure ressource gratuite pour le web hacking.'),
    (6, 1, 'J''ajouterais CyberChef pour le decodage et la manipulation de donnees.'),
    (7, 2, 'Flask pour les petits projets, Django pour les gros. Simple !'),
    (7, 5, 'J''utilise FastAPI maintenant, c''est un bon compromis entre les deux.'),
    (8, 4, 'Point 4 est crucial. Les JWT sans expiration c''est un desastre de securite.'),
    (10, 1, 'Le Zero Trust m''interesse beaucoup. Tu as des ressources a recommander ?'),
    (10, 3, 'L''IA pour la detection des menaces est fascinante. On en parlera dans un prochain post.');