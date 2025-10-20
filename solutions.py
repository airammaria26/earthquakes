import json
# The Python standard library includes some functionality for communicating
# over the Internet.
# However, we will use a more powerful and simpler library called requests.
# This is external library that you may need to install first.
import requests


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


    # The response we get back is an object with several fields.
    # The actual contents we care about are in its text field:
    text = response.text
    # To understand the structure of this text, you may want to save it
    # to a file and open it in VS Code or a browser.
    # See the README file for more information.

    # We need to interpret the text to get values that we can work with.
    # What format is the text in? How can we load the values?
    return json.loads(text)

def count_earthquakes(data):
    """Get the total number of earthquakes in the response."""
    return data["metadata"]["count"]


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]

def get_magnitudes_per_year(earthquakes):
    """Return a dict {year: [magnitudes]}."""
    magnitudes_per_year = {}
    for eq in earthquakes:
        year = get_year(eq)
        mag = get_magnitude(eq)
        if year not in magnitudes_per_year:
            magnitudes_per_year[year] = []
        magnitudes_per_year[year].append(mag)
    return magnitudes_per_year

def plot_average_magnitude_per_year(earthquakes):
    """Plot average magnitude of earthquakes per year."""
    magnitudes_per_year = get_magnitudes_per_year(earthquakes)

    years = sorted(magnitudes_per_year.keys())
    avg_magnitudes = [
        np.mean(magnitudes_per_year[year]) for year in years
    ]

    plt.figure(figsize=(8, 5))
    plt.plot(years, avg_magnitudes, marker="o")
    plt.xlabel("Year")
    plt.ylabel("Average Magnitude")
    plt.title("Average Earthquake Magnitude per Year")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.savefig("average_magnitude_per_year.png")
    plt.show()


def plot_number_per_year(earthquakes):
    """Plot frequency (number) of earthquakes per year."""
    years = [get_year(eq) for eq in earthquakes]
    unique_years, counts = np.unique(years, return_counts=True)

    plt.figure(figsize=(8, 5))
    plt.bar(unique_years, counts)
    plt.xlabel("Year")
    plt.ylabel("Number of Earthquakes")
    plt.title("Frequency of Earthquakes per Year")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.savefig("earthquakes_per_year.png")
    plt.show()

def get_location(earthquake):
    """Retrieve the latitude and longitude of an earthquake item."""
    coordinates = earthquake["geometry"]["coordinates"]
    # There are three coordinates, but we don't care about the third (altitude)
    return (coordinates[0], coordinates[1])


def get_maximum(data):
    """Get the magnitude and location of the strongest earthquake in the data."""
    current_max_magnitude = get_magnitude(data["features"][0])
    current_max_location = get_location(data["features"][0])
    for item in data["features"]:
        magnitude = get_magnitude(item)
        # Note: what happens if there are two earthquakes with the same magnitude?
        if magnitude > current_max_magnitude:
            current_max_magnitude = magnitude
            current_max_location = get_location(item)
    return current_max_magnitude, current_max_location
    # There are other ways of doing this too:
    # biggest_earthquake = sorted(data["features"], key=get_magnitude)[0]
    # return get_magnitude(biggest_earthquake), get_location(biggest_earthquake)
    # Or...
    # biggest_earthquake = max(
    #     ({"mag": get_magnitude(item), "location": get_location(item)}
    #     for item in data["features"]),
    #     key=lambda x: x["mag"]
    # )
    # return biggest_earthquake["mag"], biggest_earthquake["location"]

def get_year(earthquake):
    """Extract the year in which an earthquake happened."""
    timestamp = earthquake["properties"]["time"]
    year = date.fromtimestamp(timestamp / 1000).year
    return year


def get_magnitude(earthquake):
    """Retrieve the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]






# === MAIN SCRIPT ===
if __name__ == "__main__":
    quakes = get_data()["features"]
    plot_number_per_year(quakes)
    plt.clf()
    plot_average_magnitude_per_year(quakes)


# With all the above functions defined, we can now call them and get the result
data = get_data()
print(f"Loaded {count_earthquakes(data)}")
max_magnitude, max_location = get_maximum(data)
print(f"The strongest earthquake was at {max_location} with magnitude {max_magnitude}")