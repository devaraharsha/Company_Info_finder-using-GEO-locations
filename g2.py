import requests
import csv
import os
from flask import Flask, request, send_file, render_template_string
import rocketreach

GOOGLE_API_KEY = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"
ROCKETREACH_API_KEY = "19bbbb1k5978103faaf65b0a7f25b80b8ea9aa6f"
CSV_FILE = "company_info.csv"

app = Flask(__name__)
rr = rocketreach.Gateway(api_key=ROCKETREACH_API_KEY)

def get_place(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "rankby": "distance", "type": "establishment", "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    return results[0] if results else None

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "formatted_phone_number,website", "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("result", {})

def find_manager_via_linkedin(company_name):
    # You can dynamically set or remove the LinkedIn URL logic as needed
    try:
        # Only filter by company and title (practical for your use case)
        s = rr.person.search().filter(current_employer=company_name, current_title="OPERATIONS MANAGER")
        result = s.execute()
        for person in result.people:
            name = getattr(person, "name", "N/A")
            linkedin_url = getattr(person, "linkedin_url", "N/A")
            emails = getattr(person, "emails", [])
            emails_str = ", ".join(emails) if emails else "N/A"
            phones = getattr(person, "phones", [])
            phones_str = ", ".join(phones) if phones else "N/A"
            return name, linkedin_url, emails_str, phones_str
    except Exception as e:
        print("RocketReach search error:", e)
    return "N/A", "N/A", "N/A", "N/A"

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow([
                "Company Name", "Google Maps Link", "Address", "Phone Number",
                "Website", "Manager Name", "Manager LinkedIn URL", "Manager Email", "Manager Phone"
            ])
        writer.writerow(data)

TEMPLATE = '''
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
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
        }
        .main-card {
            max-width: 430px;
            background: rgba(255,255,255,0.95);
            border-radius: 1.6rem;
            padding: 2.5rem 2rem 1.5rem;
            margin: 3rem auto;
            box-shadow: 0 6px 32px rgba(31,64,55,0.25);
        }
        h2 {
            text-align: center;
            color: #088167;
            font-weight: 800;
            margin-bottom: 2rem;
            letter-spacing: 1px;
        }
        .btn-primary {
            background: linear-gradient(90deg, #088167 30%, #4f9a94 100%);
            border: none;
            font-weight: 600;
            font-size: 1.18rem;
            padding: 0.6rem 0;
            border-radius: 0.7rem;
            box-shadow: 0 4px 24px rgba(60,72,88,0.12);
            transition: background 0.3s;
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #4f9a94 10%, #088167 100%);
        }
        .result-card {
            background: #e6fbfc;
            border-radius: 1rem;
            padding: 1.2rem 1.1rem 1.1rem 1.1rem;
            margin-top: 1.4rem;
            box-shadow: 0 2px 13px rgba(31,64,55,0.08);
        }
        .result-card h6 {
            color: #0367a6;
            margin-bottom: 1rem;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .result-card b {
            color: #044262;
        }
        .btn-outline-success {
            margin-top: 1.6rem;
            border-radius: 999px;
            padding: 0.5rem 2.3rem;
            font-weight: 600;
            font-size: 1.07rem;
        }
        .alert {
            margin-top: 1.6rem;
        }
        @media (max-width: 500px) {
            .main-card {
                max-width: 97vw;
                padding: 1.2rem 0.3rem;
                margin-top: 0.7rem;
                border-radius: 1.1rem;
            }
        }
    </style>
</head>
<body>
<div class="main-card">
    <h2>Company Info Finder</h2>
    <form method="get" class="mb-3">
        <label class="form-label">Latitude</label>
        <input type="text" name="lat" class="form-control shadow-sm mb-3" placeholder="Enter Latitude" value="{{ lat or '' }}" required>
        <label class="form-label">Longitude</label>
        <input type="text" name="lng" class="form-control shadow-sm mb-3" placeholder="Enter Longitude" value="{{ lng or '' }}" required>
        <button class="btn btn-primary btn-lg w-100" type="submit">Search</button>
    </form>

    {% if result %}
    <div class="result-card">
        <h6>Result</h6>
        <div><b>Company:</b> {{ result.company_name }}</div>
        <div><b>Google Maps:</b> <a href="{{ result.maps_link }}" target="_blank">View</a></div>
        <div><b>Address:</b> {{ result.address }}</div>
        <div><b>Phone:</b> 
            {% if result.phone_number != 'N/A' %}
                <a href="tel:{{ result.phone_number }}">{{ result.phone_number }}</a>
            {% else %}N/A{% endif %}
        </div>
        <div><b>Website:</b> 
            {% if result.website != 'N/A' %}
                <a href="{{ result.website }}" target="_blank">{{ result.website }}</a>
            {% else %}N/A{% endif %}
        </div>
        <div><b>Manager Name:</b> {{ result.manager_name }}</div>
        <div><b>Manager LinkedIn:</b> 
            {% if result.manager_linkedin != 'N/A' %}
                <a href="{{ result.manager_linkedin }}" target="_blank">{{ result.manager_linkedin }}</a>
            {% else %}N/A{% endif %}
        </div>
        <div><b>Manager Email:</b> {{ result.email }}</div>
        <div><b>Manager Phone:</b> {{ result.manager_phone }}</div>
        <div class="text-center">
             <a href="/download" class="btn btn-outline-success">Download CSV</a>
        </div>
    </div>
    {% elif error %}
    <div class="alert alert-danger mt-3">{{ error }}</div>
    {% endif %}
</div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
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

                manager_name, linkedin_url, email, manager_phone = find_manager_via_linkedin(company_name)
                manager_name = manager_name or "N/A"
                linkedin_url = linkedin_url or "N/A"
                email = email or "N/A"
                manager_phone = manager_phone or "N/A"

                save_to_csv([company_name, maps_link, address, phone_number, website, manager_name, linkedin_url, email, manager_phone])

                result = {
                    "company_name": company_name,
                    "maps_link": maps_link,
                    "address": address,
                    "phone_number": phone_number,
                    "website": website,
                    "manager_name": manager_name,
                    "manager_linkedin": linkedin_url,
                    "email": email,
                    "manager_phone": manager_phone,
                }
        except Exception as ex:
            error = f"Error: {ex}"
    return render_template_string(TEMPLATE, result=result, error=error, lat=lat, lng=lng)

@app.route('/download')
def download_csv():
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True)
    return 'No CSV file generated yet.'

if __name__ == '__main__':
    app.run(debug=True)
