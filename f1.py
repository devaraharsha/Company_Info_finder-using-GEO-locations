import requests
import csv
import os
from flask import Flask, request, send_file

GOOGLE_API_KEY = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"
APOLLO_API_KEY = "3mRThrbwH4klaUQkpMOdnw"
ROCKETREACH_API_KEY = "19bbbb1k2801d26c4f07faf6eb3056de5eb36da7"

app = Flask(__name__)
CSV_FILE = "company_info.csv"

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
    params = {"place_id": place_id, "fields": "formatted_phone_number,website", "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("result", {})

def get_manager_info(company_name):
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {"Authorization": f"Bearer {APOLLO_API_KEY}"}
    payload = {"q_keywords": f"Operations Manager {company_name}", "page": 1, "person_titles": ["Operations Manager"]}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        people = data.get("people", [])
        if people:
            person = people[0]
            name = f"{person.get('first_name','')} {person.get('last_name','')}".strip()
            email = person.get("email", "N/A")
            phone = person.get("phone_numbers", ["N/A"])[0] if person.get("phone_numbers") else "N/A"
            return name, email, phone
    except:
        pass
    return get_manager_info_rocketreach(company_name)

def get_manager_info_rocketreach(company_name):
    url = "https://api.rocketreach.co/v1/api/search"
    headers = {"Authorization": f"Bearer {ROCKETREACH_API_KEY}"}
    payload = {"query": f"Operations Manager {company_name}", "page_size": 1}
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
        email = emails[0].get("email", "N/A") if emails else "N/A"
        phone = phones[0].get("number", "N/A") if phones else "N/A"
        return name, email, phone
    except:
        return None, None, None

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Company Name","Google Maps Link","Address","Phone Number","Website","Operations Manager","Email","Manager Phone"])
        writer.writerow(data)

@app.route("/", methods=["GET"])
def index():
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return """
        <h2>Enter Latitude & Longitude</h2>
        <form method="get">
            Latitude: <input name="lat" type="text"><br>
            Longitude: <input name="lng" type="text"><br>
            <button type="submit">Search</button>
        </form>
        """

    place = get_place(lat, lng)
    if not place:
        return "No companies located nearby."

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

    return f"""
    <h2>Result</h2>
    <form method="get">
        Latitude: <input name="lat" type="text" value="{lat}"><br>
        Longitude: <input name="lng" type="text" value="{lng}"><br>
        <button type="submit">Search</button>
    </form>
    <b>Company:</b> {company_name}<br>
    <b>Google Maps:</b> <a href="{maps_link}" target="_blank">View</a><br>
    <b>Address:</b> {address}<br>
    <b>Phone:</b> <a href="tel:{phone_number}">{phone_number}</a><br>
    <b>Website:</b> <a href="{website}" target="_blank">{website}</a><br>
    <b>Manager Name:</b> {manager_name}<br>
    <b>Email:</b> <a href="mailto:{email}">{email}</a><br>
    <b>Manager Phone:</b> <a href="tel:{manager_phone}">{manager_phone}</a><br>
    <br>
    <a href="/download">Download CSV</a>
    """

@app.route("/download")
def download_csv():
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True)
    return "No CSV file generated yet."

if __name__ == "__main__":
    app.run(debug=True)
