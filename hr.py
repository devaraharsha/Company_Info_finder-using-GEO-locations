import requests
import sys

def get_place_name(lat, lng):
    api_key = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U"  # <-- your API key here
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "rankby": "distance",       # gets the nearest place
        "type": "establishment",
        "key": api_key
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
        return None, None

    # only take the first nearest result
    place = results[0]
    name = place.get("name", "Unknown")
    place_id = place.get("place_id", "")
    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "N/A"

    return name, maps_link


def main():
    try:
        latitude = float(input("Enter latitude: ").strip())
        longitude = float(input("Enter longitude: ").strip())
    except ValueError:
        print("Invalid latitude/longitude.")
        sys.exit(1)

    name, link = get_place_name(latitude, longitude)

    if name:
        print("Nearest Company Name:", name)
        print("Google Maps Link:", link)
    else:
        print("No company found at this location.")

if __name__ == "__main__":
    main()
