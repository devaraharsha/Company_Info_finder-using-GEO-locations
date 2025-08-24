Operations Manager Finder
A Flask web app that lets you enter latitude and longitude, finds the nearest company using the Google Places API, and fetches the Operations Manager’s contact details (name, LinkedIn, email, phone) using the RocketReach API.

Features
Search by Latitude/Longitude:
Input a location to get the nearest company's details and live contacts.

Automatic Company Identification:
Uses Google Places to auto-identify offices/businesses near any coordinates.

Contact Lookup:
Uses RocketReach to find Operations Manager (or similar) for the detected company.

Clean Results:
See manager’s name, title, LinkedIn profile, email(s), and phone(s) (when available).

CSV Export:
Download your result history for analysis.

Modern UI:
Responsive, mobile-friendly, and easy to use.

Screenshots
(Insert screenshots of your app showing input form and result. Example:)

Install & Run
Clone this repo:

bash
git clone https://github.com/YOUR_USERNAME/operations-manager-finder.git
cd operations-manager-finder
Install Python dependencies:

bash
pip install flask requests rocketreach
Update API keys
Open your main .py file and set:

python
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
ROCKETREACH_API_KEY = "YOUR_ROCKETREACH_API_KEY"
Run the server:

bash
python app.py
In your browser:
Go to http://127.0.0.1:5000, input lat/lon, and click Search.


Usage Notes
Only public info available in RocketReach will be returned for Operations Managers.

If you see N/A for some fields, try searching for another company or branch.

Export your results easily with the CSV download button.

Tech
Flask

Google Places API

RocketReach API
