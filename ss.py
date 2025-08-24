import requests
import csv
import os
from flask import Flask, render_template_string, request, send_file

# Replace these with your actual keys
GOOGLE_API_KEY = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"
APOLLO_API_KEY = "3mRThrbwH4klaUQkpMOdnw"  # <-- Replace with your Apollo API key

app = Flask(__name__)

def get_place_name(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "rankby": "distance",
        "type": "establishment",
        "key": GOOGLE_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        # Return exactly four values here
        return None, None, None, None  
    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None, None, None, None
    place = results[0]
    name = place.get("name", "Unknown")
    place_id = place.get("place_id", "")
    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "N/A"
    phone, address = get_place_details(place_id) if place_id else (None, None)
    return name, maps_link, phone, address


def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,formatted_address",
        "key": GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    result = data.get("result", {})
    phone = result.get("formatted_phone_number", "N/A")
    address = result.get("formatted_address", "N/A")
    return phone, address

def get_manager_info(company_name):
    url = "https://api.apollo.io/v1/people/search"
    headers = {"Authorization": f"Bearer {APOLLO_API_KEY}"}
    payload = {
        "q_keywords": f"Operations Manager {company_name}",
        "page": 1,
        "person_titles": ["Operations Manager"]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, None, None
    data = resp.json()
    people = data.get("people", [])
    if not people:
        return None, None, None
    person = people[0]
    name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
    email = person.get("email", "N/A")
    phone = person.get("phone_numbers", ["N/A"]) if person.get("phone_numbers") else "N/A"
    return name, email, phone

def write_to_csv(data, output_file="company_info.csv"):
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow([
                "Company Name", "Maps Link", "Address", "Phone Number",
                "Manager Name", "Manager Email", "Manager Phone"
            ])
        writer.writerow(data)

TEMPLATE = '''
<!doctype html>
<title>Company Info Finder</title>
<h2>Find Company & Manager from Location</h2>
<form method=post>
    Latitude: <input type=text name=latitude required>
    Longitude: <input type=text name=longitude required>
    <input type=submit value=Find>
</form>
{% if result %}
    <h3>Result:</h3>
    <ul>
        <li><b>Company Name:</b> {{result.name}}</li>
        <li><b>Google Maps Link:</b> <a href="{{result.link}}" target="_blank">{{result.link}}</a></li>
        <li><b>Address:</b> {{result.address}}</li>
        <li><b>Phone Number:</b> {{result.phone}}</li>
        <li><b>Operational Manager:</b> {{result.manager}}</li>
        <li><b>Email:</b> {{result.email}}</li>
        <li><b>Manager Phone:</b> {{result.mgr_phone}}</li>
    </ul>
    <a href="/download">Download CSV</a>
{% elif error %}
    <p style="color:red;">{{error}}</p>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lng = float(request.form['longitude'])
        except ValueError:
            error = "Invalid latitude or longitude input."
            return render_template_string(TEMPLATE, result=None, error=error)
        name, link, phone, address = get_place_name(lat, lng)
        if name and link:
            manager, email, mgr_phone = get_manager_info(name)
            result = {
                'name': name,
                'link': link,
                'address': address,
                'phone': phone,
                'manager': manager or "N/A",
                'email': email or "N/A",
                'mgr_phone': mgr_phone or "N/A"
            }
            write_to_csv([
                name, link, address, phone, 
                manager or "N/A", email or "N/A", mgr_phone or "N/A"
            ])
        else:
            error = "No company found at this location, or API/network error."
    return render_template_string(TEMPLATE, result=result, error=error)

@app.route('/download')
def download():
    return send_file("company_info.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
