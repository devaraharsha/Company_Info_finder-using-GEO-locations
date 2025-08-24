import requests
import sys
import csv
import os
GOOGLE_API_KEY = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"
APOLLO_API_KEY = "nVgE-yI0YIDu8MDI7E0KgQ"

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
        print(f"Network/HTTP error: {e}")
        sys.exit(1)
    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None, None, None, None, None
    place = results[0]
    name = place.get("name", "Unknown")
    place_id = place.get("place_id", "")
    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "N/A"
    phone, website, address = get_place_details(place_id) if place_id else (None, None, None)
    return name, maps_link, phone, website, address

def get_place_details(place_id):
    """Fetch phone number, website, and address using Place Details API"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,formatted_address",
        "key": GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    result = data.get("result", {})
    phone = result.get("formatted_phone_number", "N/A")
    website = result.get("website", "N/A")
    address = result.get("formatted_address", "N/A")
    return phone, website, address

def get_manager_info(company_name, domain=None):
    """Fetch Operational Manager details using Apollo API"""
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
        print(f"Apollo API error: {e}")
        return None, None, None
    data = resp.json()
    people = data.get("people", [])
    if not people:
        return None, None, None
    # Pick the first Operations Manager found
    person = people[0]
    name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
    email = person.get("email", "N/A")
    phone = person.get("phone_numbers", ["N/A"]) if person.get("phone_numbers") else "N/A"
    return name, email, phone

def write_to_csv(data, output_file="company_info.csv"):
    # Write data to CSV, add header if file does not exist
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow([
                "Company Name", "Maps Link", "Address", "Phone Number", "Website",
                "Manager Name", "Manager Email", "Manager Phone"
            ])
        writer.writerow(data)

def main():
    try:
        latitude = float(input("Enter latitude: ").strip())
        longitude = float(input("Enter longitude: ").strip())
    except ValueError:
        print("Invalid latitude/longitude.")
        sys.exit(1)
    name, link, phone, website, address = get_place_name(latitude, longitude)
    if name:
        print("Nearest Company Name:", name)
        print("Google Maps Link:", link)
        print("Address:", address)
        print("Phone Number:", phone)
        print("Website:", website)
        manager, email, mgr_phone = get_manager_info(name, website)
        if manager:
            print("Operational Manager:", manager)
            print("Email:", email)
            print("Phone:", mgr_phone)
        else:
            print("No Operations Manager found in Apollo API.")
        # Save everything to CSV
        write_to_csv([
            name, link, address, phone, website, 
            manager or "N/A", email or "N/A", mgr_phone or "N/A"
        ])
        print("Result saved to company_info.csv")
    else:
        print("No company found at this location.")

if __name__ == "__main__":
    main()
