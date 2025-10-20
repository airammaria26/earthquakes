import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict


def get_data():
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
    return response.json()

def extract_year_and_magnitude(data):
    freq_per_year = defaultdict(int)
    mag_sum_per_year = defaultdict(float)
    count_per_year = defaultdict(int)

    for eq in data["features"]:
        timestamp_ms = eq["properties"]["time"]
        date = datetime.utcfromtimestamp(timestamp_ms / 1000)
        year = date.year
        magnitude = eq["properties"]["mag"]
        if magnitude is not None:
            freq_per_year[year] += 1
            mag_sum_per_year[year] += magnitude
            count_per_year[year] += 1

    return freq_per_year, mag_sum_per_year, count_per_year

def plot_data(freq_per_year, mag_sum_per_year, count_per_year):
    years = sorted(freq_per_year.keys())

    # Frequency plot
    frequencies = [freq_per_year[year] for year in years]

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.bar(years, frequencies, color='skyblue')
    plt.title("Earthquake Frequency per Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Earthquakes")

    # Average magnitude plot
    avg_magnitudes = [mag_sum_per_year[year] / count_per_year[year] for year in years]

    plt.subplot(1, 2, 2)
    plt.plot(years, avg_magnitudes, marker='o', linestyle='-', color='orange')
    plt.title("Average Earthquake Magnitude per Year")
    plt.xlabel("Year")
    plt.ylabel("Average Magnitude")

    plt.tight_layout()
    plt.savefig("earthquake_stats.png")
    print("Plot saved as 'earthquake_stats.png'")
    
def count_earthquakes(data):
    """Get the total number of earthquakes in the response."""
    return data["metadata"]["count"]

def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]


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
        if magnitude > current_max_magnitude:
            current_max_magnitude = magnitude
            current_max_location = get_location(item)
    return current_max_magnitude, current_max_location

data = get_data()
freq_per_year, mag_sum_per_year, count_per_year = extract_year_and_magnitude(data)
plot_data(freq_per_year, mag_sum_per_year, count_per_year)