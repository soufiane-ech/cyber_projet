from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector
import hashlib
import os
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'forum_db')
}


def db():
    return mysql.connector.connect(**DB_CONFIG)


# ============================================
# VULNERABILITE INTENTIONNELLE -- NE PAS MODIFIER
# Token d authentification previsible
# ============================================
def make_token(user_id, username):
    now = datetime.now()
    slot = (now.hour // 6) * 6
    time_part = now.strftime(f"%Y-%m-%d-{slot:02d}")
    uid_hex = format(user_id, 'x')
    raw = f"{uid_hex}|{username}|{time_part}"
    return hashlib.sha256(raw.encode()).hexdigest()


def check_token(token):
    if not token:
        return None
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    for u in users:
        if make_token(u['id'], u['username']) == token:
            return u
    return None


def current_user():
    return check_token(request.cookies.get('auth_token'))
# ============================================
# FIN DE LA ZONE VULNERABLE
# ============================================


@app.route('/')
def index():
    if current_user():
        return redirect(url_for('forum'))
    return redirect(url_for('login'))


# --------------------------------------------------
# AUTH : Login / Register / Logout
# --------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return render_template('login.html', error="Identifiants invalides")

        token = make_token(user['id'], user['username'])
        resp = make_response(redirect(url_for('forum')))
        resp.set_cookie('auth_token', token)
        return resp

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        bio = request.form.get('bio', '').strip()

        if not username or not password:
            return render_template('register.html', error="Le pseudo et le mot de passe sont obligatoires.")

        conn = db()
        cur = conn.cursor(dictionary=True)

        # Verifier si le username existe deja
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return render_template('register.html', error="Ce pseudo est deja pris.")

        cur.execute(
            "INSERT INTO users (username, password, email, bio) VALUES (%s, %s, %s, %s)",
            (username, password, email, bio)
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()

        # Connecter automatiquement apres inscription
        token = make_token(new_id, username)
        resp = make_response(redirect(url_for('forum')))
        resp.set_cookie('auth_token', token)
        return resp

    return render_template('register.html')


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('auth_token')
    return resp


# --------------------------------------------------
# FORUM : Liste des posts
# --------------------------------------------------

@app.route('/forum')
def forum():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    category_filter = request.args.get('category', '')
    search_query = request.args.get('q', '').strip()

    conn = db()
    cur = conn.cursor(dictionary=True)

    # Recuperer les posts avec comptage de commentaires
    query = """
        SELECT p.id, p.title, p.content, p.category, p.created_at, u.username,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
    """
    params = []
    conditions = []

    if category_filter:
        conditions.append("p.category = %s")
        params.append(category_filter)

    if search_query:
        conditions.append("(p.title LIKE %s OR p.content LIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY p.created_at DESC"

    cur.execute(query, params)
    posts = cur.fetchall()

    # Recuperer les categories disponibles
    cur.execute("SELECT DISTINCT category FROM posts ORDER BY category")
    categories = [row['category'] for row in cur.fetchall()]

    # Stats du forum
    if category_filter:
        # Utilisateurs actifs (auteurs de posts ou commentaires) dans cette categorie
        cur.execute("""
            SELECT COUNT(DISTINCT u_id) AS count FROM (
                SELECT user_id AS u_id FROM posts WHERE category = %s
                UNION
                SELECT c.user_id AS u_id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.category = %s
            ) as tmp
        """, (category_filter, category_filter))
        user_count = cur.fetchone()['count']

        cur.execute("SELECT COUNT(*) AS count FROM posts WHERE category = %s", (category_filter,))
        post_count = cur.fetchone()['count']

        cur.execute("SELECT COUNT(c.id) AS count FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.category = %s", (category_filter,))
        comment_count = cur.fetchone()['count']
    else:
        cur.execute("SELECT COUNT(*) AS count FROM users")
        user_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) AS count FROM posts")
        post_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) AS count FROM comments")
        comment_count = cur.fetchone()['count']

    cur.close()
    conn.close()

    return render_template('forum.html',
                           user=user,
                           posts=posts,
                           categories=categories,
                           current_category=category_filter,
                           search_query=search_query,
                           stats={'users': user_count, 'posts': post_count, 'comments': comment_count})


# --------------------------------------------------
# POSTS : Detail + Creation + Commentaires
# --------------------------------------------------

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.id, p.title, p.content, p.category, p.created_at, u.username, p.user_id
        FROM posts p JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()

    if not post:
        cur.close()
        conn.close()
        return "Post introuvable", 404

    cur.execute("""
        SELECT c.id, c.content, c.created_at, u.username
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s ORDER BY c.created_at ASC
    """, (post_id,))
    comments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('post.html', user=user, post=post, comments=comments)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    content = request.form.get('content', '').strip()
    if not content:
        return redirect(url_for('post_detail', post_id=post_id))

    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)",
        (post_id, user['id'], content)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General').strip()

        if not title or not content:
            return render_template('new_post.html', user=user,
                                   error="Le titre et le contenu sont obligatoires.")

        conn = db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (user_id, title, content, category) VALUES (%s, %s, %s, %s)",
            (user['id'], title, content, category)
        )
        conn.commit()
        post_id = cur.lastrowid
        cur.close()
        conn.close()

        return redirect(url_for('post_detail', post_id=post_id))

    return render_template('new_post.html', user=user)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()

    if post and (post['user_id'] == user['id'] or user['role'] == 'admin'):
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for('forum'))


# --------------------------------------------------
# PROFIL : Voir + Modifier (avec changement de username)
# --------------------------------------------------

@app.route('/profile/<username>')
def profile(username):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, email, bio, role, created_at FROM users WHERE username = %s",
        (username,)
    )
    target = cur.fetchone()

    if not target:
        cur.close()
        conn.close()
        return "Utilisateur introuvable", 404

    # Recuperer les posts de cet utilisateur
    cur.execute("""
        SELECT p.id, p.title, p.category, p.created_at,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p WHERE p.user_id = %s
        ORDER BY p.created_at DESC
    """, (target['id'],))
    user_posts = cur.fetchall()

    # Compter les commentaires de l utilisateur
    cur.execute("SELECT COUNT(*) AS count FROM comments WHERE user_id = %s", (target['id'],))
    comment_count = cur.fetchone()['count']

    cur.close()
    conn.close()

    return render_template('profile.html', user=user, target=target,
                           user_posts=user_posts, comment_count=comment_count)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        bio = request.form.get('bio', '').strip()

        if not new_username:
            cur.execute("SELECT id, username, email, bio FROM users WHERE id = %s", (user['id'],))
            profile_data = cur.fetchone()
            cur.close()
            conn.close()
            return render_template('edit_profile.html', user=user, profile=profile_data,
                                   error="Le pseudo ne peut pas etre vide.")

        # Verifier si le nouveau username est deja pris par un autre utilisateur
        if new_username != user['username']:
            cur.execute("SELECT id FROM users WHERE username = %s AND id != %s", (new_username, user['id']))
            if cur.fetchone():
                cur.execute("SELECT id, username, email, bio FROM users WHERE id = %s", (user['id'],))
                profile_data = cur.fetchone()
                cur.close()
                conn.close()
                return render_template('edit_profile.html', user=user, profile=profile_data,
                                       error="Ce pseudo est deja pris par un autre utilisateur.")

        cur.execute(
            "UPDATE users SET username = %s, email = %s, bio = %s WHERE id = %s",
            (new_username, email, bio, user['id'])
        )
        conn.commit()
        cur.close()
        conn.close()

        # Regenerer le token avec le nouveau username
        token = make_token(user['id'], new_username)
        resp = make_response(redirect(url_for('profile', username=new_username)))
        resp.set_cookie('auth_token', token)
        return resp

    # GET -- pre-remplir le formulaire
    cur.execute("SELECT id, username, email, bio FROM users WHERE id = %s", (user['id'],))
    profile_data = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_profile.html', user=user, profile=profile_data)


# --------------------------------------------------
# ADMIN : Dashboard
# --------------------------------------------------

@app.route('/admin')
def admin():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if user['role'] != 'admin':
        return render_template('forbidden.html', user=user), 403

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id, username, email, role, created_at FROM users ORDER BY id")
    all_users = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS count FROM users")
    user_count = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) AS count FROM posts")
    post_count = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) AS count FROM comments")
    comment_count = cur.fetchone()['count']

    cur.close()
    conn.close()

    return render_template('admin.html', user=user, all_users=all_users,
                           stats={'users': user_count, 'posts': post_count, 'comments': comment_count})


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    if user_id == user['id']:
        return redirect(url_for('admin'))  # Ne pas se supprimer soi-meme

    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)