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

TOKEN_SECRET = os.environ.get('TOKEN_SECRET', 'fallback_dev_key')


def db():
    return mysql.connector.connect(**DB_CONFIG)


def make_token(user_id, username):
    now = datetime.now()
    slot = (now.hour // 6) * 6
    time_part = now.strftime(f"%Y-%m-%d-{slot:02d}")
    uid_hex = format(user_id, 'x')
    raw = f"{TOKEN_SECRET}|{uid_hex}|{username}|{time_part}"
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


@app.route('/')
def index():
    if current_user():
        return redirect(url_for('forum'))
    return redirect(url_for('login'))


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


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('auth_token')
    return resp


@app.route('/forum')
def forum():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    conn.close()

    token = request.cookies.get('auth_token')
    return render_template('forum.html', user=user, posts=posts, token=token)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()

    if not post:
        cur.close()
        conn.close()
        return "Post introuvable", 404

    cur.execute("""
        SELECT c.content, c.created_at, u.username
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s ORDER BY c.created_at ASC
    """, (post_id,))
    comments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('post.html', user=user, post=post, comments=comments)


@app.route('/profile/<username>')
def profile(username):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, role, created_at FROM users WHERE username = %s",
        (username,)
    )
    target = cur.fetchone()
    cur.close()
    conn.close()

    if not target:
        return "Utilisateur introuvable", 404

    return render_template('profile.html', user=user, target=target)


@app.route('/admin')
def admin():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if user['role'] != 'admin':
        return render_template('forbidden.html', user=user), 403

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, password, role, created_at FROM users")
    all_users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin.html', user=user, all_users=all_users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)