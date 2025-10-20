from datetime import date
import requests
import json
import matplotlib.pyplot as plt


def get_data():
    """Download earthquake data from the USGS API."""
    response = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson",
        params={
            'starttime': "2000-01-01",
            "maxlatitude": "58.723",
            "minlatitude": "50.008",
            "maxlongitude": "1.67",
            "minlongitude": "-9.756",
            "minmagnitude": "1",
            "endtime": "2018-10-11",
            "orderby": "time-asc"
        }
    )
    response.raise_for_status()
    return response.json()


def get_year(earthquake):
    """Extract the year in which an earthquake happened."""
    timestamp = earthquake['properties']['time']
    # The time is given in a strange-looking but commonly-used format.
    # To understand it, we can look at the documentation of the source data:
    # https://earthquake.usgs.gov/data/comcat/index.php#time
    # Fortunately, Python provides a way of interpreting this timestamp:
    # (Question for discussion: Why do we divide by 1000?)
    year = date.fromtimestamp(timestamp/1000).year
    return year


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    return earthquake["properties"]["mag"]


def get_magnitudes_per_year(earthquakes):
    """Group magnitudes by year."""
    magnitudes_by_year = {}
    for quake in earthquakes:
        year = get_year(quake)
        mag = get_magnitude(quake)
        if mag is not None:
            magnitudes_by_year.setdefault(year, []).append(mag)
    return magnitudes_by_year


def plot_average_magnitude_per_year(earthquakes):
    """Plot the average earthquake magnitude per year."""
    magnitudes_by_year = get_magnitudes_per_year(earthquakes)

    years = sorted(magnitudes_by_year.keys())
    avg_mags = [sum(magnitudes_by_year[y]) / len(magnitudes_by_year[y]) for y in years]

    plt.figure(figsize=(8, 5))
    plt.plot(years, avg_mags, marker='o', color='darkred')
    plt.title("Average Earthquake Magnitude per Year (2000–2018)")
    plt.xlabel("Year")
    plt.ylabel("Average Magnitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_number_per_year(earthquakes):
    """Plot the number of earthquakes per year."""
    magnitudes_by_year = get_magnitudes_per_year(earthquakes)

    years = sorted(magnitudes_by_year.keys())
    counts = [len(magnitudes_by_year[y]) for y in years]

    plt.figure(figsize=(8, 5))
    plt.bar(years, counts, color='steelblue')
    plt.title("Number of Earthquakes per Year (2000–2018)")
    plt.xlabel("Year")
    plt.ylabel("Number of Earthquakes")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


# --- Main execution ---
if __name__ == "__main__":
    quakes = get_data()['features']

    # Plot the results
    plot_number_per_year(quakes)
    plot_average_magnitude_per_year(quakes)