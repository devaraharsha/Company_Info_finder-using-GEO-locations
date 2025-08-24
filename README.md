📍 Operations Manager Finder

A Flask web application that lets you enter latitude and longitude, finds the nearest company using the Google Places API, and fetches the Operations Manager’s contact details (name, LinkedIn, email, phone) using the RocketReach API.

✨ Features

🔎 Search by Latitude/Longitude
Enter coordinates to get the nearest company’s details and live contacts.

🏢 Automatic Company Identification
Uses Google Places to auto-detect businesses/offices near any location.

👤 Contact Lookup
Finds Operations Manager (or similar roles) for the detected company using RocketReach.

📑 Clean Results
Displays manager’s name, title, LinkedIn profile, email(s), and phone(s) (if available).

📂 CSV Export
Download your search history for further analysis.

💻 Modern UI
Responsive, mobile-friendly, and easy to use.

📸 Screenshots

(Add screenshots of your app here. Example:)

Input Form


Results Page


🚀 Installation & Run
1. Clone the repository
git clone https://github.com/devaraharsha/Company_Info_finder-using-GEO-locations.git
cd Company_Info_finder-using-GEO-locations

2. Install dependencies
pip install flask requests rocketreach

3. Update API Keys

Open your app.py file and replace with your keys:

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
ROCKETREACH_API_KEY = "YOUR_ROCKETREACH_API_KEY"

4. Run the server
python app.py

5. Open in browser

Visit:
👉 http://127.0.0.1:5000

Enter latitude and longitude, then click Search.

📘 Usage Notes

Only public info available in RocketReach will be returned.

If you see N/A for some fields, try another company or location.

Use the CSV Export button to save your results.

🛠️ Tech Stack

Flask
 – Web Framework

Google Places API
 – Company lookup

RocketReach API
 – Contact details
