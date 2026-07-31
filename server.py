from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os


class HealthAIHandler(SimpleHTTPRequestHandler):

    def do_POST(self):

        if self.path == "/signup":

            length = int(self.headers["Content-Length"])

            data = self.rfile.read(length)

            user = json.loads(data)



            file_path = "data/users.json"


            if os.path.exists(file_path):

                with open(file_path, "r") as f:
                    users = json.load(f)

            else:

                users = []



            # Check duplicate email

            for u in users:

                if u["email"] == user["email"]:

                    self.send_response(400)

                    self.end_headers()

                    self.wfile.write(
                        b"Account already exists"
                    )

                    return




            users.append(user)



            with open(file_path, "w") as f:

                json.dump(
                    users,
                    f,
                    indent=4
                )



            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"Account Created"
            )




        elif self.path == "/login":


            length = int(self.headers["Content-Length"])

            data = self.rfile.read(length)

            login = json.loads(data)



            with open("data/users.json","r") as f:

                users=json.load(f)




            for user in users:

                if (
                    user["email"] == login["email"]
                    and
                    user["password"] == login["password"]
                ):


                    self.send_response(200)

                    self.end_headers()

                    self.wfile.write(
                        json.dumps(user).encode()
                    )

                    return




            self.send_response(401)

            self.end_headers()

            self.wfile.write(
                b"Invalid Login"
            )



        elif self.path == "/forgot":
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
            reset = json.loads(data)

            with open("data/users.json", "r") as f:
                users = json.load(f)

            found = False

            for user in users:
                if user["email"] == reset["email"]:
                    user["password"] = reset["password"]
                    found = True

            if found:
                with open("data/users.json", "w") as f:
                    json.dump(users, f, indent=4)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Password Changed")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Email not found")

server = HTTPServer(
    ("127.0.0.1", 8000),
    HealthAIHandler
)

print("HealthAI Server Running...")
print("Open: http://127.0.0.1:8000")

try:
    server.serve_forever()

except KeyboardInterrupt:
    print("Server stopped")

finally:
    server.server_close()