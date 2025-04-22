from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# data samples
sleep_data = [7, 6.5, 8, 7.2, 6, 7.8, 8.1]
exercise_data = [30, 45, 20, 60, 50, 0, 40]  # minutes per day
nutrition_data = ["Protein", "Carbs", "Fat"], [40, 45, 15]  # labels/percent distribution

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sleep")
def sleep():
    return render_template("sleep.html", data=sleep_data)

@app.route("/exercise")
def exercise():
    return render_template("exercise.html", data=exercise_data)

@app.route("/nutrition")
def nutrition():
    labels, values = nutrition_data
    return render_template("nutrition.html", labels=labels, values=values)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)