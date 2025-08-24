import requests
import csv

def get_company_by_coords(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 18,
        "addressdetails": 1
    }
    response = requests.get(url, params=params, headers={"User-Agent": "geo-project"})
    return response.json()

def save_to_csv(data, filename="companies_exact.csv"):
    keys = ["Place Name", "Latitude", "Longitude", "Full Address", "Place Type"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for place in data:
            writer.writerow(place)

locations = [
    {"lat":53.264420, "lon":-1.857810},
    {"lat": 52.950260, "lon": -2.180140},
    {"lat": 50.868060, "lon": -2.612710},
    {"lat": 51.430030, "lon": -0.983950},
    {"lat": 51.293070, "lon": -1.029240},
    {"lat": 51.293330, "lon": -1.029400}
]

all_companies = []

for loc in locations:
    place = get_company_by_coords(loc["lat"], loc["lon"])
    if "display_name" in place:
        all_companies.append({
            "Place Name": place.get("name", place["display_name"].split(",")[0]),
            "Latitude": loc["lat"],
            "Longitude": loc["lon"],
            "Full Address": place["display_name"],
            "Place Type": place.get("type", "N/A")
        })

save_to_csv(all_companies)
print("✅ Exact company data saved to companies_exact.csv")
