from flask import Flask, Response
from pymongo import MongoClient, errors
import os

app = Flask(__name__)

def check_mongo():
    uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        return True
    except errors.PyMongoError:
        return False

@app.get("/")
def index():
    connected = " (connected)" if check_mongo() else " (not connected)"
    HTML = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hello World – Flask</title>
<style>
  body{{
    margin:0; height:100vh; display:grid; place-items:center;
    background: linear-gradient(120deg,#0f2027,#203a43,#2c5364);
    background-size:180% 180%; animation:bg-move 12s ease-in-out infinite;
    color:#fff; font-family:system-ui,Segoe UI,Roboto,sans-serif;
  }}
  .hello{{
    font-size:clamp(32px,7vw,72px); white-space:nowrap; overflow:hidden;
    border-right:.12em solid rgba(255,255,255,.85); width:0;
    animation:typing 2.6s steps(20,end) forwards, caret 1s step-end infinite;
    text-shadow:0 6px 24px rgba(0,0,0,.35);
  }}
  @keyframes typing {{ from{{width:0}} to{{width:13ch}} }}
  @keyframes caret {{ 50% {{ border-color: transparent }} }}
  @keyframes bg-move {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
</style>
</head>
<body>
  <div class="hello">{connected}</div>
  <div class="hello">!!!!</div>
  <div></div>
</body>
</html>
"""
    return Response(HTML, mimetype="text/html")

@app.get("/db")
def db_health():
    if check_mongo():
        return "MongoDB OK (ping réussi)\n", 200
    else:
        return "MongoDB KO\n", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
