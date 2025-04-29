from flask import Flask, render_template, request, redirect, session,url_for, make_response
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import certifi
from dotenv import load_dotenv
from flask_session import Session
from pymongo.errors import ConnectionFailure
from datetime import datetime ,timezone
import matplotlib.pyplot as plt
import io
import base64

load_dotenv()

try:
    client = MongoClient(os.getenv("MONGO_URI"))
    # Force connection on a request as the connect=True parameter of MongoClient may not trigger it
    client.admin.command("ping")
    print("✅ Connection successful!")
except ConnectionFailure as e:
    print("❌ Connection failed:", e)

# MongoDB setup
uri = os.getenv("MONGO_URI")
import certifi
from pymongo import MongoClient

client = MongoClient(
    os.environ["MONGO_URI"],
    tlsCAFile=certifi.where(),
    tls=True,
)

Mongo_DBNAME = os.getenv("MONGO_DBNAME")
db = client[Mongo_DBNAME]

# Flask setup
app = Flask(__name__, static_folder='assets/templates')
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
        email = request.form["email"]

        existing_user = db.users.find_one({"username": username})
        if existing_user:
            return "<h3>User already exists. Try logging in.</h3>"

        db.users.insert_one({
            "username": username,
            "password": password ,
            "email": email
        })
        return redirect("/login")

    return render_template("signup.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]


        user = db.users.find_one({"username": username})
        if not user:
            return "<h3>User not found.</h3>"
        if user.get("email")!= email:
            return "<h3>Incorrect email.</h3>"
        if user.get("password") != password:
            return "<h3>Incorrect password.</h3>"

        session["user_id"] = str(user["_id"])
        return redirect("/dashboard")

    return render_template("login.html")

#user info
@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    if "user_id" not in session:
        return redirect("/login")

    user_id = ObjectId(session["user_id"])

    if request.method == "POST":
            update_data = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "date_of_birth": request.form.get("date_of_birth"),
                "gender": request.form.get("gender"),
                "height": {
                    "value": float(request.form.get("height_value")),
                    "unit": request.form.get("height_unit")
                },
                "weight": {
                    "value": float(request.form.get("weight_value")),
                    "unit": request.form.get("weight_unit")
                }
            }

            db.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            user_data = db.users.find_one({"_id": user_id})
            return render_template("user_profile.html", user=user_data)

        

    # If GET, load current profile info to prefill form
    user_data = db.users.find_one({"_id": user_id})
    return render_template("user_profile.html", user=user_data)
   

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = db.users.find_one({"_id": ObjectId(session["user_id"])})
     # Fetch all sleep logs for the logged-in user
    #sleep_logs = list(db.sleep_logs.find({"user_id": user["_id"]}))
     # Sort sleep logs by date (latest first)
    #sleep_logs.sort(key=lambda x: x["date"], reverse=True)
    #latest_sleep = sleep_logs[0] if sleep_logs else None
    return render_template("results.html", user=user)

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
    user_id = ObjectId(session["user_id"])
    if request.method == "POST":
        hours_slept = float(request.form["hours_slept"])
        sleep_notes = request.form.get("sleep_notes", "")
        sleep_quality = request.form.get("sleep_quality", "")
        date = request.form["date"]

        db.sleep_logs.insert_one({
            "user_id": user_id,
            "hours_slept": hours_slept,
            "sleep_notes": sleep_notes,
            "sleep_quality": sleep_quality,
            "date": date,
            "timestamp": datetime.now(timezone.utc)
        })

        return redirect(url_for("log_sleep"))
    sleep_entries = list(db.sleep_logs.find({"user_id": user_id}))
    sleep_entries.sort(key=lambda e: e["date"], reverse=True)
    return render_template("log_sleep.html", sleep_entries=sleep_entries)



@app.route("/log/nutrition", methods=["GET", "POST"])
def log_nutrition():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = ObjectId(session["user_id"])
    if request.method == "POST":
        carbs = float(request.form["carbs"])
        fats = float(request.form["fats"])
        proteins = float(request.form["proteins"])
        date = request.form["date"]
        total = carbs + fats + proteins
        balanced = (
            total > 0 and
            0.4 <= carbs/total <= 0.6 and
            0.2 <= fats/total <= 0.4 and
            0.2 <= proteins/total <= 0.4
        )
        db.nutrition_logs.insert_one({
            "user_id": user_id,
            "date": date,
            "carbs": carbs,
            "fats": fats,
            "proteins": proteins,
            "balanced": balanced,
            "timestamp": datetime.now(timezone.utc)
        })
        return redirect(url_for("log_nutrition"))
    nutrition_entries = list(db.nutrition_logs.find({"user_id": user_id}))
    nutrition_entries.sort(key=lambda e: e["date"], reverse=True)
    return render_template("log_nutrition.html", nutrition_entries=nutrition_entries)

@app.route("/log/exercise", methods=["GET", "POST"])
def log_exercise():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = ObjectId(session["user_id"])
    if request.method == "POST":
        exercise_type = request.form["exercise_type"]
        duration = float(request.form["duration"])
        date = request.form["date"]
        db.exercise_logs.insert_one({
            "user_id": user_id,
            "date": date,
            "exercise_type": exercise_type,
            "duration": duration,
            "timestamp": datetime.now(timezone.utc)
        })
        return redirect(url_for("log_exercise"))
    exercise_entries = list(db.exercise_logs.find({"user_id": user_id}))
    exercise_entries.sort(key=lambda e: e["date"], reverse=True)
    return render_template("log_exercise.html", exercise_entries=exercise_entries)

#########
@app.route("/activity_feed")
def activity_feed():
    if "user_id" not in session:
        return redirect("/login")

    user_id = ObjectId(session["user_id"])

    # Fetch from  collections
    sleep_logs = list(db.sleep_logs.find({"user_id": user_id}))
    for sleep in sleep_logs:
        sleep["type"] = "Sleep"
        sleep["timestamp"] = sleep.get("timestamp", datetime.min)

    nutrition_logs = list(db.nutrition_logs.find({"user_id": user_id}))
    for nutrition in nutrition_logs:
        nutrition["type"] = "Nutrition"
        nutrition["timestamp"] = nutrition.get("timestamp", datetime.min)

    exercise_logs = list(db.exercise_logs.find({"user_id": user_id}))
    for exercise in exercise_logs:
        exercise["type"] = "Exercise"
        exercise["timestamp"] = exercise.get("timestamp", datetime.min)

    # Combine all logs
    all_entries = sleep_logs + nutrition_logs + exercise_logs
    all_entries.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("reports.html", entries=all_entries)

@app.route("/reports", methods=["GET", "POST"])
def reports():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    error = None
    
    from report_generator import ReportGenerator
    
    try:
        generator = ReportGenerator(user_id)
        
        report_id = request.args.get('report_id')
        if report_id:
            try:
                html_content, filename = generator.get_report_by_id(report_id)
                response = make_response(html_content)
                response.headers["Content-Type"] = "text/html"
                response.headers["Content-Disposition"] = f"attachment; filename={filename}"
                return response
            except Exception as e:
                error = f"Error loading report: {str(e)}"
        
        if request.method == "POST":
            report_type = request.form["report_type"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            metrics = request.form.getlist("metrics")
            
            if not metrics:
                error = "Please select at least one metric to include in your report."
            else:
                try:
                    html_content, filename = generator.generate_report(
                        report_type=report_type,
                        start_date=start_date,
                        end_date=end_date,
                        metrics=metrics
                    )
                    
                    response = make_response(html_content)
                    response.headers["Content-Type"] = "text/html"
                    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
                    return response
                except Exception as e:
                    error = f"Error generating report: {str(e)}"
        
        reports = generator.get_user_reports()
        
        show_form = request.args.get('generate') == 'True'
        
        return render_template("reports.html", 
                              reports=reports, 
                              show_form=show_form, 
                              error=error)
    
    except Exception as e:
        return render_template("reports.html", 
                              reports=[], 
                              show_form=False, 
                              error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
