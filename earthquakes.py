import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.animation as animation



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

def filter_by_year(data, year):
    filtered = {
        "type": "FeatureCollection",
        "features": []
    }
    for item in data["features"]:
        timestamp = item["properties"]["time"]
        date = datetime.utcfromtimestamp(timestamp / 1000)
        if date.year == year:
            filtered["features"].append(item)
    return filtered

def get_lat_lon_mag(data):
    lons, lats, mags = [], [], []
    for item in data["features"]:
        coords = item["geometry"]["coordinates"]
        mag = item["properties"]["mag"]
        if mag is not None:
            lons.append(coords[0])
            lats.append(coords[1])
            mags.append(mag)
    return np.array(lons), np.array(lats), np.array(mags)

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

def plot_earthquake_map(data, year=None, animate=False, bin_size=1.0, by_day=False):
    if year:
        data = filter_by_year(data, year)

    lons, lats, mags = get_lat_lon_mag(data)

    def make_plot(ax_map, ax_top, ax_right, current_lons, current_lats, current_mags, title):
        ax_map.clear()
        ax_top.clear()
        ax_right.clear()

        ax_map.set_title(title)
        ax_map.coastlines(resolution='10m')
        ax_map.set_extent([-10, 2, 49, 59], crs=ccrs.PlateCarree())

        sc = ax_map.scatter(current_lons, current_lats, s=np.array(current_mags) ** 2,
                            alpha=0.6, color='red', transform=ccrs.PlateCarree(), zorder=3)

        # Histograms
        bins_lon = np.arange(-10, 2 + bin_size, bin_size)
        bins_lat = np.arange(49, 59 + bin_size, bin_size)

        ax_top.hist(current_lons, bins=bins_lon, color='gray')
        ax_top.set_xlim([-10, 2])
        ax_top.set_xticks([])
        ax_top.set_yticks([])

        ax_right.hist(current_lats, bins=bins_lat, orientation='horizontal', color='gray')
        ax_right.set_ylim([49, 59])
        ax_right.set_xticks([])
        ax_right.set_yticks([])

    if animate:
        fig = plt.figure(figsize=(10, 8))
        gs = fig.add_gridspec(4, 4)
        ax_map = fig.add_subplot(gs[1:, :-1], projection=ccrs.PlateCarree())
        ax_top = fig.add_subplot(gs[0, :-1])
        ax_right = fig.add_subplot(gs[1:, -1])

        all_dates = []
        date_to_features = defaultdict(list)

        for item in data["features"]:
            timestamp = item["properties"]["time"]
            date = datetime.utcfromtimestamp(timestamp / 1000)
            key = date.date() if by_day else date.year
            date_to_features[key].append(item)

        all_dates = sorted(date_to_features.keys())

        def update(frame):
            frame_data = {
                "type": "FeatureCollection",
                "features": date_to_features[all_dates[frame]]
            }
            frame_lons, frame_lats, frame_mags = get_lat_lon_mag(frame_data)
            make_plot(ax_map, ax_top, ax_right, frame_lons, frame_lats, frame_mags, f"Earthquakes - {all_dates[frame]}")

        ani = animation.FuncAnimation(fig, update, frames=len(all_dates), interval=400, repeat=False)
        plt.tight_layout()
        plt.show()
    else:
        # Static plot
        fig = plt.figure(figsize=(10, 8))
        gs = fig.add_gridspec(4, 4)
        ax_map = fig.add_subplot(gs[1:, :-1], projection=ccrs.PlateCarree())
        ax_top = fig.add_subplot(gs[0, :-1])
        ax_right = fig.add_subplot(gs[1:, -1])

        title = f"Earthquake Map {'(' + str(year) + ')' if year else ''}"
        make_plot(ax_map, ax_top, ax_right, lons, lats, mags, title)

        plt.tight_layout()
        plt.savefig("earthquake_map.png")
        plt.show()
        print("Saved plot as 'earthquake_map.png'")


data = get_data()
freq_per_year, mag_sum_per_year, count_per_year = extract_year_and_magnitude(data)
plot_data(freq_per_year, mag_sum_per_year, count_per_year)
data = get_data()

# plot_earthquake_map(data)
# plot_earthquake_map(data, year=2010)
plot_earthquake_map(data, animate=True)
# plot_earthquake_map(data, animate=True, by_day=True)
