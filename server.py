from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

DB_FILE = "database.json"

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

class Handler(SimpleHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        db = load_db()

        if self.path == "/api/users":
            self.send_json(db["users"])
        elif self.path == "/api/posts":
            self.send_json(db["posts"])
        elif self.path == "/api/messages":
            self.send_json(db["messages"])
        elif self.path == "/api/notifications":
            self.send_json(db["notifications"])
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body or b"{}")
        db = load_db()

        if self.path == "/api/register":
            user = {
                "name": data.get("name", ""),
                "email": data.get("email", ""),
                "password": data.get("password", "")
            }
            db["users"].append(user)
            save_db(db)
            self.send_json({"message": "An ƙirƙiri account"}, 201)

        elif self.path == "/api/message":
            db["messages"].append(data)
            save_db(db)
            self.send_json({"message": "An aika saƙo"}, 201)

        else:
            self.send_json({"error": "API ba a samu ba"}, 404)

server = HTTPServer(("localhost", 8000), Handler)
print("Sayyadi Server yana aiki...")
server.serve_forever()
