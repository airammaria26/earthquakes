# The Python standard library includes some functionality for communicating
# over the Internet.
# However, we will use a more powerful and simpler library called requests.
# This is external library that you may need to install first.
import requests
import json


def get_data():
    # With requests, we can ask the web service for the data.
    # Can you understand the parameters we are passing here?
    response = requests.get(
        "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson",
        params={
            'starttime': "2000-01-01",
            "maxlatitude": "58.723",
            "minlatitude": "50.008",
            "maxlongitude": "1.67",
            "minlongitude": "-9.756",
            "minmagnitude": "1",
            "endtime": "2018-10-11",
            "orderby": "time-asc"}
    )

    # Convert the JSON text to a Python dictionary
    data = json.loads(response.text)
    return data

def count_earthquakes(data):
    """Get the total number of earthquakes in the response."""
    return len(data["features"])


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]


def get_location(earthquake):
    """Retrieve the latitude and longitude of an earthquake item."""
    coords = earthquake["geometry"]["coordinates"]
    longitude = coords[0]
    latitude = coords[1]
    return (latitude, longitude)


def get_place(earthquake):
    """Retrieve the human-readable place name, if available."""
    return earthquake["properties"].get("place", "Unknown location")


def get_maximum(data):
    """
    Get the magnitude and all locations of the strongest earthquakes in the data.
    Returns:
        max_mag (float): the maximum magnitude found
        strongest_quakes (list): list of tuples (location, place_name)
    """
    features = data["features"]
    if not features:
        return None, []

    # Find the maximum magnitude
    magnitudes = [get_magnitude(q) for q in features if get_magnitude(q) is not None]
    max_mag = max(magnitudes)

    # Find all earthquakes with this magnitude
    strongest_quakes = []
    for quake in features:
        mag = get_magnitude(quake)
        if mag == max_mag:
            strongest_quakes.append((get_location(quake), get_place(quake)))

    return max_mag, strongest_quakes


# Main execution
if __name__ == "__main__":
    data = get_data()
    total = count_earthquakes(data)
    print(f"Loaded {total} earthquakes from the dataset.")
    max_magnitude, strongest = get_maximum(data)

    if not strongest:
        print("No earthquakes found in the dataset.")
    else:
        print(f"\nThe strongest earthquakes had magnitude {max_magnitude}:\n")
        for i, (location, place) in enumerate(strongest, 1):
            print(f"{i}. Location: {location}, Place: {place}")