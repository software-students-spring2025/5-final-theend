from flask import Flask, render_template, request, redirect, session
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import certifi
from dotenv import load_dotenv
from flask_session import Session

# Load .env variables
load_dotenv()

# MongoDB setup
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
Mongo_DBNAME = os.getenv("MONGO_DBNAME")
db = client[Mongo_DBNAME]

# Flask setup
app = Flask(__name__, static_folder='assets')
app.secret_key = os.getenv("SECRET_KEY", "devkey")

# Session setup
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# =======================
# ROUTES
# =======================

@app.route("/")
def home():
    return render_template("signup.html")

# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = db.users.find_one({"username": username})
        if existing_user:
            return "<h3>User already exists. Try logging in.</h3>"

        db.users.insert_one({
            "username": username,
            "password": password
        })
        return redirect("/login")

    return render_template("signup.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.users.find_one({"username": username})
        if not user:
            return "<h3>User not found.</h3>"
        if user.get("password") != password:
            return "<h3>Incorrect password.</h3>"

        session["user_id"] = str(user["_id"])
        return redirect("/dashboard")

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = db.users.find_one({"_id": ObjectId(session["user_id"])})
     # Fetch all sleep logs for the logged-in user
    sleep_logs = list(db.sleep_logs.find({"user_id": user["_id"]}))
     # Sort sleep logs by date (latest first)
    sleep_logs.sort(key=lambda x: x["date"], reverse=True)
    latest_sleep = sleep_logs[0] if sleep_logs else None
    return render_template("results.html", user=user, latest_sleep=latest_sleep)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#sleep log
@app.route("/log/sleep", methods=["GET", "POST"])
def log_sleep():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        user_id = ObjectId(session["user_id"])
        hours_slept = float(request.form["hours_slept"])
        sleep_notes = request.form["sleep_notes"]
        sleep_quality = request.form["sleep_quality"]
        date = request.form["date"]

        db.sleep_logs.insert_one({
            "user_id": user_id,
            "hours_slept": hours_slept,
            "sleep_notes": sleep_notes,
            "sleep_quality": sleep_quality,
            "date": date
        })

        return redirect("/dashboard")

    return render_template("log_sleep.html")

if __name__ == "__main__":
    app.run(debug=True)