import os
PORT = int(os.environ.get("PORT", "8001"))
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DB_FILE = "database.json"

def load_db():
    with open(DB_FILE, "r") as f:
        db = json.load(f)

    db.setdefault("users", [])
    db.setdefault("posts", [])
    db.setdefault("messages", [])
    db.setdefault("notifications", [])
    db.setdefault("follows", [])

    return db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        db = load_db()

        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/users":
            self.send_json(db["users"])

        elif path == "/api/posts":
            self.send_json(db["posts"])

        elif path == "/api/follows":
            self.send_json(db["follows"])

        elif path == "/api/notifications":
            user = params.get("user", [None])[0]

            if not user:
                self.send_json(
                    {"error": "user ana bukata"},
                    400
                )
                return

            notifications = [
                n for n in db["notifications"]
                if n.get("user") == user
            ]

            self.send_json(notifications)

        elif path == "/api/messages":
            user1 = params.get("user1", [None])[0]
            user2 = params.get("user2", [None])[0]

            if not user1 or not user2:
                self.send_json(
                    {"error": "user1 da user2 ana bukata"},
                    400
                )
                return

            messages = [
                m for m in db["messages"]
                if (
                    m.get("sender") == user1 and
                    m.get("receiver") == user2
                ) or (
                    m.get("sender") == user2 and
                    m.get("receiver") == user1
                )
            ]

            self.send_json(messages)

        else:
            self.send_json(
                {"error": "Ba a sami wannan API ba"},
                404
            )

    def do_POST(self):
        db = load_db()

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            data = json.loads(raw.decode("utf-8"))
        except:
            self.send_json(
                {"error": "Data ba daidai ba"},
                400
            )
            return

        if self.path == "/api/register":

            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            if not name or not email or not password:
                self.send_json(
                    {"error": "Cike dukkan bayanai"},
                    400
                )
                return

            for user in db["users"]:
                if user["email"] == email:
                    self.send_json(
                        {"error": "Email ɗin ya riga ya yi register"},
                        400
                    )
                    return

            db["users"].append({
                "name": name,
                "email": email,
                "password": password
            })

            save_db(db)

            self.send_json({
                "message": "An yi register lafiya! 🎉"
            })

        elif self.path == "/api/login":

            email = data.get("email")
            password = data.get("password")

            for user in db["users"]:

                if (
                    user["email"] == email and
                    user["password"] == password
                ):

                    self.send_json({
                        "message": "Login yayi nasara!",
                        "user": {
                            "name": user["name"],
                            "email": user["email"]
                        }
                    })

                    return

            self.send_json(
                {"error": "Email ko password ba daidai ba"},
                401
            )

        elif self.path == "/api/post":

            name = data.get("name")
            text = data.get("text")

            if not name or not text:
                self.send_json(
                    {"error": "Name da text ana bukata"},
                    400
                )
                return

            db["posts"].append({
                "name": name,
                "text": text
            })

            save_db(db)

            self.send_json({
                "message": "An ajiye post! 📝"
            })

        elif self.path == "/api/follow":

            follower = data.get("follower")
            following = data.get("following")

            if not follower or not following:
                self.send_json(
                    {"error": "Follower da following ana bukata"},
                    400
                )
                return

            if follower == following:
                self.send_json(
                    {"error": "Ba za ka iya follow kanka ba"},
                    400
                )
                return

            exists = any(
                f["follower"] == follower and
                f["following"] == following
                for f in db["follows"]
            )

            if exists:

                db["follows"] = [
                    f for f in db["follows"]
                    if not (
                        f["follower"] == follower and
                        f["following"] == following
                    )
                ]

                save_db(db)

                self.send_json({
                    "message": "An daina follow"
                })

            else:

                db["follows"].append({
                    "follower": follower,
                    "following": following
                })

                db["notifications"].append({
                    "user": following,
                    "from": follower,
                    "type": "follow",
                    "text": "Wani ya yi maka follow 👥"
                })

                save_db(db)

                self.send_json({
                    "message": "An yi follow! 👥"
                })

        elif self.path == "/api/message":

            sender = data.get("sender")
            receiver = data.get("receiver")
            text = data.get("text")

            if not sender or not receiver or not text:
                self.send_json(
                    {"error": "Sender, receiver da text ana bukata"},
                    400
                )
                return

            message = {
                "sender": sender,
                "receiver": receiver,
                "text": text
            }

            db["messages"].append(message)

            save_db(db)

            self.send_json({
                "message": "An aika saƙon! 💬",
                "data": message
            })

        else:

            self.send_json(
                {"error": "Ba a sami wannan API ba"},
                404
            )

print(f"Sayyadi Backend yana aiki a port {PORT} 🚀")


server = HTTPServer(
    ("0.0.0.0", PORT),
    Handler
)

server.serve_forever()
