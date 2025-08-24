const axios = require("axios");
const readline = require("readline");

// Your Google Maps API key
const apiKey = "AIzaSyC6-BBP12wAkqUIsVbOo3qSBBVVYcM0H7U";

// Function to get nearest place
async function getPlaceName(lat, lng) {
  const url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json";
  const params = {
    location: `${lat},${lng}`,
    rankby: "distance",
    type: "establishment",
    key: apiKey,
  };

  try {
    const response = await axios.get(url, { params });
    const results = response.data.results;

    if (!results || results.length === 0) {
      return { name: null, link: null };
    }

    const place = results[0];
    const name = place.name || "Unknown";
    const placeId = place.place_id || "";
    const mapsLink = placeId
      ? `https://www.google.com/maps/place/?q=place_id:${placeId}`
      : "N/A";

    return { name, link: mapsLink };
  } catch (error) {
    console.error("Network/HTTP error:", error.message);
    return { name: null, link: null };
  }
}

// CLI input for latitude & longitude
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question("Enter latitude: ", (lat) => {
  rl.question("Enter longitude: ", async (lng) => {
    const { name, link } = await getPlaceName(lat.trim(), lng.trim());

    if (name) {
      console.log("Nearest Company Name:", name);
      console.log("Google Maps Link:", link);
    } else {
      console.log("No company found at this location.");
    }

    rl.close();
  });
});
