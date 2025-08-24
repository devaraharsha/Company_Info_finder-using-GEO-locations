import requests
import csv
import os
from flask import Flask, request, send_file, render_template_string

GOOGLE_API_KEY = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"
APOLLO_API_KEY = "3mRThrbwH4klaUQkpMOdnw"
ROCKETREACH_API_KEY = "19bbbb1k5978103faaf65b0a7f25b80b8ea9aa6f"
CSV_FILE = "company_info.csv"

app = Flask(__name__)

def get_place(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "rankby": "distance", "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    return results[0] if results else None

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id, 
        "fields": "formatted_phone_number,website",
        "key": GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("result", {})

def get_manager_info(company_name):
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {"Authorization": f"Bearer {APOLLO_API_KEY}"}
    payload = {
        "q_keywords": f"Manager {company_name}", 
        "page": 1, 
        "person_titles": ["Manager"]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        people = data.get("people", [])
        if people:
            person = people[0]
            name = f"{person.get('first_name','')} {person.get('last_name','')}".strip()
            email = person.get("email", "N/A")
            phone = person.get("phone_numbers", ["N/A"]) if person.get("phone_numbers") else "N/A"
            return name, email, phone
    except:
        pass
    return get_manager_info_rocketreach(company_name)

def get_manager_info_rocketreach(company_name):
    url = "https://api.rocketreach.co/v1/api/people_search"
    headers = {"Authorization": f"Bearer {ROCKETREACH_API_KEY}"}
    payload = {"query": f"Manager {company_name}", "page_size": 1}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        profiles = data.get("profiles", [])
        if not profiles:
            return None, None, None
        profile = profiles[0]
        name = profile.get("name", "N/A")
        emails = profile.get("emails", [])
        phones = profile.get("phones", [])
        email = emails.get("email", "N/A") if emails else "N/A"
        phone = phones.get("number", "N/A") if phones else "N/A"
        return name, email, phone
    except:
        return None, None, None

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow([
                "Company Name","Google Maps Link","Address","Phone Number",
                "Website","Manager","Manager Email","Manager Phone"
            ])
        writer.writerow(data)

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <title>Company Info Finder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" />
    <style>
        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #e0ecfc 0%, #d9f8c4 70%, #4f9a94 100%);
            background-attachment: fixed;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            margin:0;
        }
        .main-card {
            max-width: 430px;
            background: rgba(255,255,255,0.96);
            border-radius: 1.6rem;
            margin: 3rem auto;
            box-shadow: 0 6px 32px 0 rgba(31, 64, 55, 0.25);
            padding: 2.5rem 2rem 1.5rem 2rem;
            position: relative;
            top: 2vh;
        }
        h2 {
            text-align: center;
            color: #088167;
            font-weight: 800;
            margin-bottom: 2.1rem;
            letter-spacing:1px;
        }
        .form-label {font-weight:700;}
        .btn-primary {
            background: linear-gradient(90deg, #088167 30%, #4f9a94 100%);
            border: none;
            font-weight: 600;
            font-size: 1.18rem;
            padding: 0.6rem 0;
            border-radius: 0.7rem;
            box-shadow: 0 4px 24px rgba(60, 72, 88, 0.12);
            transition: background 0.3s;
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #4f9a94 10%, #088167 100%);
        }
        .result-card {
            background: #e6fbfc;
            border-radius: 1rem;
            margin-top: 1.4rem;
            padding: 1.2rem 1.1rem 1.1rem 1.1rem;
            box-shadow: 0 2px 13px rgba(31, 64, 55, 0.08);
        }
        .result-card h6 {
            color:#0367a6;
            margin:0 0 1rem 0;
            font-weight:700;
            letter-spacing: 1px;
        }
        .result-card b { color:#044262;}
        .btn-outline-success {
            margin-top: 1.6rem;
            border-radius: 999px;
            padding: 0.5rem 2.3rem;
            font-weight:600;
            font-size:1.07rem;
        }
        @media (max-width: 500px) {
            .main-card {
                max-width: 97vw;
                border-radius: 1.1rem;
                margin-top: 0.7rem;
                padding: 1.2rem 0.3rem 1.2rem 0.3rem;
            }
        }
    </style>
</head>
<body>
    <div class="main-card">
        <h2>Company Info Finder</h2>
        <form method="get" class="mb-3">
            <div class="mb-3">
                <label class="form-label">Latitude</label>
                <input name="lat" type="text" value="{{lat or ''}}" required placeholder="Enter Latitude" class="form-control shadow-sm">
            </div>
            <div class="mb-4">
                <label class="form-label">Longitude</label>
                <input name="lng" type="text" value="{{lng or ''}}" required placeholder="Enter Longitude" class="form-control shadow-sm">
            </div>
            <div class="d-grid">
                <button class="btn btn-primary btn-lg" type="submit">Search</button>
            </div>
        </form>
        {% if result %}
        <div class="result-card">
            <h6>Result</h6>
            <div class="mb-1"><b>Company:</b> {{result.company_name}}</div>
            <div class="mb-1"><b>Google Maps:</b> <a href="{{result.maps_link}}" target="_blank">View</a></div>
            <div class="mb-1"><b>Address:</b> {{result.address}}</div>
            <div class="mb-1"><b>Phone:</b> 
              {% if result.phone_number != "N/A" %}
                <a href="tel:{{result.phone_number}}">{{result.phone_number}}</a>
              {% else %}N/A{% endif %}
            </div>
            <div class="mb-1"><b>Website:</b> 
              {% if result.website != "N/A" %}
                <a href="{{result.website}}" target="_blank">{{result.website}}</a>
              {% else %}N/A{% endif %}
            </div>
            <div class="mb-1"><b>Manager Name:</b> {{result.manager_name}}</div>
            <div class="mb-1"><b>Manager Email:</b> 
              {% if result.email != "N/A" %}
                <a href="mailto:{{result.email}}">{{result.email}}</a>
              {% else %}N/A{% endif %}
            </div>
            <div class="mb-1"><b>Manager Phone:</b>
              {% if result.manager_phone != "N/A" %}
                <a href="tel:{{result.manager_phone}}">{{result.manager_phone}}</a>
              {% else %}N/A{% endif %}
            </div>
            <div class="text-center">
                <a href="/download" class="btn btn-outline-success">Download CSV</a>
            </div>
        </div>
        {% elif error %}
        <div class="alert alert-danger mt-2">{{error}}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    result = None
    error = None
    if lat and lng:
        try:
            place = get_place(lat, lng)
            if not place:
                error = "No companies located nearby."
            else:
                company_name = place.get("name", "N/A")
                maps_link = f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}"
                address = place.get("vicinity", "N/A")
                details = get_place_details(place["place_id"])
                phone_number = details.get("formatted_phone_number", "N/A")
                website = details.get("website", "N/A")

                manager_name, email, manager_phone = get_manager_info(company_name)
                manager_name = manager_name or "N/A"
                email = email or "N/A"
                manager_phone = manager_phone or "N/A"

                save_to_csv([company_name, maps_link, address, phone_number, website, manager_name, email, manager_phone])
                result = {
                    "company_name": company_name,
                    "maps_link": maps_link,
                    "address": address,
                    "phone_number": phone_number,
                    "website": website,
                    "manager_name": manager_name,
                    "email": email,
                    "manager_phone": manager_phone,
                }
        except Exception as ex:
            error = f"Error: {ex}"

    return render_template_string(TEMPLATE, result=result, error=error, lat=lat, lng=lng)

@app.route("/download")
def download_csv():
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True)
    return "No CSV file generated yet."

if __name__ == "__main__":
    app.run(debug=True)
