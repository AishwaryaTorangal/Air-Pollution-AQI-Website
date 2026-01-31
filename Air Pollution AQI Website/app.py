import sqlite3
from datetime import datetime, timedelta
from functools import wraps

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# OpenWeather API KEY
API_KEY = "3b913597bc092a98af0e436054e443cf"

# ---------------------- DB ----------------------
def get_db():
    conn = sqlite3.connect("aqi.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password_hash TEXT
        );
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS aqi_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT,
            aqi INTEGER,
            checked_at TEXT
        );
    """)

    conn.commit()
    conn.close()


# ---------------------- Login Decorator ----------------------
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            flash("Login first!", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap


# ---------------------- AQI Helpers ----------------------
def get_tip(aqi):
    if aqi is None:
        return (
            "⚠️ No AQI data available.\n"
            "• If the air smells smoky or looks hazy, reduce outdoor activity.\n"
            "• Keep windows closed and run indoor ventilation if available.\n"
            "• Children, elderly, and people with asthma should stay extra cautious."
        )

    if aqi <= 50:
        return (
            "🌿 GOOD AIR QUALITY\n"
            "• Safe for all age groups and health conditions.\n"
            "• Great time for outdoor exercise, jogging, and play.\n"
            "• Air out your home to bring in fresh air.\n"
            "• Sensitive individuals will also feel comfortable.\n"
            "• Pets can enjoy normal outdoor walks."
        )

    if aqi <= 100:
        return (
            "🙂 MODERATE AIR QUALITY\n"
            "• Safe for most people, but mild irritation is possible.\n"
            "• Asthma/allergy patients should avoid long outdoor workouts.\n"
            "• Children & elderly should avoid heavy outdoor exertion.\n"
            "• Pregnant women should stay away from traffic-heavy areas.\n"
            "• Athletes: Prefer morning/evening workouts.\n"
            "• Keep pets’ outdoor time moderate."
        )

    if aqi <= 150:
        return (
            "⚠️ UNHEALTHY FOR SENSITIVE GROUPS\n"
            "• Asthma, heart or lung disease: Limit outdoor activities & carry medication.\n"
            "• Children & elderly: Prefer staying indoors; monitor for coughing or fatigue.\n"
            "• Pregnant women: Avoid long outdoor exposure; stay hydrated.\n"
            "• Outdoor workers: Use PM2.5/N95 masks & take frequent indoor breaks.\n"
            "• Athletes: Move workouts indoors.\n"
            "• General public: Keep windows closed; run air purifiers.\n"
            "• Pets: Reduce walk duration; avoid dusty areas."
        )

    if aqi <= 200:
        return (
            "🚫 UNHEALTHY AIR\n"
            "• Everyone may experience irritation or breathing issues.\n"
            "• Sensitive groups should stay indoors as much as possible.\n"
            "• Use PM2.5/N95 masks outdoors.\n"
            "• Children, elderly & pregnant women: Strongly avoid outdoor exertion.\n"
            "• Outdoor workers: Take breaks in clean indoor spaces.\n"
            "• Avoid jogging or heavy exercise outside.\n"
            "• Keep indoor air clean—close windows, use air purifiers.\n"
            "• Pets: Keep walks short and controlled."
        )

    if aqi <= 300:
        return (
            "⚠️🌡️ VERY UNHEALTHY AIR\n"
            "• High health risk for all groups.\n"
            "• Stay indoors unless absolutely necessary.\n"
            "• Always wear a certified N95/KN95 mask outdoors.\n"
            "• Children, elderly, pregnant women: Avoid going outside completely.\n"
            "• Avoid cooking methods that create indoor smoke.\n"
            "• Use air purifiers or DIY filters if available.\n"
            "• Outdoor workers: Minimize exposure & rotate duties.\n"
            "• Pets: Very limited outdoor time only."
        )

    return (
        "☣️ HAZARDOUS AIR QUALITY\n"
        "• Serious health impact for everyone; avoid going outdoors entirely.\n"
        "• Stay in a sealed indoor environment with purified air.\n"
        "• Sensitive groups must strictly avoid exposure.\n"
        "• Keep medications handy if you have respiratory or heart conditions.\n"
        "• Avoid all outdoor exercise and physical work.\n"
        "• Follow government emergency alerts and health advisories.\n"
        "• Keep pets indoors and avoid walks until air improves."
    )

# ---------------------- FREE Past 7 Days AQI (Open-Meteo) ----------------------
from datetime import datetime

def format_time_list(time_list):
    formatted = []
    for t in time_list:
        dt = datetime.strptime(t, "%Y-%m-%dT%H:%M")
        formatted.append(dt.strftime("%b %d, %I:%M %p"))
    return formatted


def get_past_7_days_aqi(city): 
    try:
        # Step 1: get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo = requests.get(geo_url, timeout=10).json()

        if "results" not in geo:
            return None

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        # Step 2: fetch historical AQI data
        aqi_url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
            "&past_days=7"
        )

        hist = requests.get(aqi_url, timeout=10).json()

        if "hourly" not in hist:
            return None

        # Extract arrays
        time = hist["hourly"]["time"]
        pm25 = hist["hourly"]["pm2_5"]
        pm10 = hist["hourly"]["pm10"]
        co   = hist["hourly"]["carbon_monoxide"]
        no2  = hist["hourly"]["nitrogen_dioxide"]
        so2  = hist["hourly"]["sulphur_dioxide"]
        o3   = hist["hourly"]["ozone"]

        # Slice last 7 days (168 hours)
        time  = time[-168:]
        pm25  = pm25[-168:]
        pm10  = pm10[-168:]
        co    = co[-168:]
        no2   = no2[-168:]
        so2   = so2[-168:]
        o3    = o3[-168:]

        # ⭐ Format timestamps
        time = format_time_list(time)

        return {
            "time": time,
            "pm25": pm25,
            "pm10": pm10,
            "co": co,
            "no2": no2,
            "so2": so2,
            "o3": o3
        }

    except Exception as e:
        print("History error:", e)
        return None

# ---------------------- Current AQI + Forecast ----------------------
def get_aqi(city):
    try:
        # Get coordinates
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo = requests.get(geo_url).json()

        if not geo:
            return None

        lat = geo[0]["lat"]
        lon = geo[0]["lon"]

        # REAL-TIME AQI
        aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_data = requests.get(aqi_url).json()

        if "list" not in aqi_data:
            return None

        pollution = aqi_data["list"][0]
        aqi_index = pollution["main"]["aqi"]

        aqi_map = {
            1: ("Good", 50),
            2: ("Fair", 100),
            3: ("Moderate", 150),
            4: ("Poor", 200),
            5: ("Very Poor", 300),
        }

        category, aqi_value = aqi_map.get(aqi_index, ("Unknown", None))

        # WEATHER
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}"
            f"&appid={API_KEY}&units=metric"
        )
        weather = requests.get(weather_url).json()
        temp = weather.get("main", {}).get("temp")
        humidity = weather.get("main", {}).get("humidity")

        # FORECAST AQI (5 days)
        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/air_pollution/forecast?"
            f"lat={lat}&lon={lon}&appid={API_KEY}"
        )
        fc = requests.get(forecast_url).json()

        labels, values = [], []
        if "list" in fc:
            for f in fc["list"]:
                ts = datetime.utcfromtimestamp(f["dt"]).strftime("%d-%b %H:%M")
                idx = f["main"]["aqi"]
                val = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}.get(idx)
                labels.append(ts)
                values.append(val)

        return {
            "city": city.title(),
            "aqi": aqi_value,
            "category": category,
            "pm25": pollution["components"]["pm2_5"],
            "pm10": pollution["components"]["pm10"],
            "co": pollution["components"]["co"],
            "no2": pollution["components"]["no2"],
            "o3": pollution["components"]["o3"],
            "so2": pollution["components"]["so2"],
            "temp": temp,
            "humidity": humidity,
            "forecast_labels": labels,
            "forecast_values": values,
            "lat": lat,
            "lon": lon
        }

    except Exception as e:
        print("API error:", e)
        return None



# ---------------------- ROUTES ----------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"].strip()
        e = request.form["email"].strip().lower()
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE email=?", (e,))
        if c.fetchone():
            flash("Email already registered!", "danger")
            conn.close()
            return redirect(url_for("register"))

        c.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (u, e, generate_password_hash(p)),
        )
        conn.commit()
        conn.close()

        flash("Registered successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        e = request.form["email"].strip().lower()
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (e,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], p):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
@login_required
def search():
    city = request.form["city"].strip()
    if not city:
        flash("Enter a city name", "warning")
        return redirect(url_for("index"))

    # Current AQI
    data = get_aqi(city)
    if not data:
        flash("City not found or API error.", "danger")
        return redirect(url_for("index"))

    # Past 7 days AQI (FREE)
    history = get_past_7_days_aqi(city)

    # Save log
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO aqi_logs (user_id, city, aqi, checked_at) VALUES (?, ?, ?, ?)",
              (session["user_id"], city, data["aqi"], datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        city=city,
        data=data,
        history=history,
        tip=get_tip(data["aqi"]),
        labels=data["forecast_labels"],
        values=data["forecast_values"]
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/predict")
def predict():
    return render_template("predict.html")


@app.route("/awarness")
def awarness():
    return render_template("awarness.html")

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)