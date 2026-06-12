import os
from rfi_fileparser import util

import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from h3 import h3_to_geo_boundary, h3_to_geo
from shapely.geometry import Polygon

def aggregate_data(filepaths):
    outer_df = pd.DataFrame(columns=[
        'h3Index',
        'lowQualityCount',
        'totalAircraftCount'
    ])
    for filepath in filepaths:
        # Load the heatmap.json file
        with open(filepath) as f:
            data = json.load(f)
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Flatten the "data" dict column into its own columns
        data_expanded = pd.json_normalize(df['data'])
        df = pd.concat([df.drop(columns=['data']), data_expanded], axis=1)
        # Keep only the columns we need
        curr = df[['h3Index', 'lowQualityCount', 'totalAircraftCount']]

        # Append
        outer_df = pd.concat([outer_df, curr], ignore_index=True)

        # Aggregate rows with the same h3Index
        outer_df = (
            outer_df
            .groupby('h3Index', as_index=False)[
                ['lowQualityCount', 'totalAircraftCount']
            ]
            .sum()
        )

        outer_df["latitude"] = outer_df["h3Index"].apply(lambda h: h3_to_geo(h)[0])
        outer_df["longitude"] = outer_df["h3Index"].apply(lambda h: h3_to_geo(h)[1])

    return outer_df


def generate_aggregate_heatmap(df, title):
    # Filter out rows with totalAircraftCount = 0 to avoid divide-by-zero
    df = df[df['totalAircraftCount'] > 0].copy()
    # Compute ratio: lowQualityCount / totalAircraftCount
    df['low_quality_ratio'] = (
            df['lowQualityCount'] / df['totalAircraftCount']
    ).astype(float)

    # Convert H3 hexagons to polygons
    def h3_to_polygon(h3_index):
        boundary = h3_to_geo_boundary(h3_index, geo_json=True)
        return Polygon(boundary)

    # Create geometry column
    df['geometry'] = df['h3Index'].apply(h3_to_polygon)
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # Create full-screen figure and axis
    fig, ax = plt.subplots(figsize=(20, 12))
    gdf.plot(
        column='low_quality_ratio',
        cmap='viridis',
        edgecolor='none',
        ax=ax,
        legend=True,
        legend_kwds={
            'shrink': 0.4,  # Shrink the colorbar to 40% height
            'label': 'Low NIC Ratio',
            'orientation': 'vertical',
            'pad': 0.02
        }
    )
    # Customize title and layout
    ax.set_title(title, fontsize=16)
    ax.set_axis_off()  # Hide axes for cleaner map
    plt.tight_layout()
    plt.show()


def generate_heatmap(filepath, title):
    if os.path.isfile(filepath):
        # Load the heatmap.json file
        with open(filepath) as f:
            data = json.load(f)
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Flatten the "data" dict column into its own columns
        data_expanded = pd.json_normalize(df['data'])
        df = pd.concat([df.drop(columns=['data']), data_expanded], axis=1)

        # Filter out rows with totalAircraftCount = 0 to avoid divide-by-zero
        df = df[df['totalAircraftCount'] > 0].copy()
        # Compute ratio: lowQualityCount / totalAircraftCount
        df['low_quality_ratio'] = df['lowQualityCount'] / df['totalAircraftCount']

        # Convert H3 hexagons to polygons
        def h3_to_polygon(h3_index):
            boundary = h3_to_geo_boundary(h3_index, geo_json=True)
            return Polygon(boundary)

        # Create geometry column
        df['geometry'] = df['h3Index'].apply(h3_to_polygon)
        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        # Create full-screen figure and axis
        fig, ax = plt.subplots(figsize=(20, 12))
        gdf.plot(
            column='low_quality_ratio',
            cmap='viridis',
            edgecolor='none',
            ax=ax,
            legend=True,
            legend_kwds={
                'shrink': 0.4,  # Shrink the colorbar to 40% height
                'label': 'Low NIC Ratio',
                'orientation': 'vertical',
                'pad': 0.02
            }
        )
        # Customize title and layout
        ax.set_title(title, fontsize=16)
        ax.set_axis_off()  # Hide axes for cleaner map
        plt.tight_layout()
        plt.show()

    else:
        # print("Looking for:", os.path.abspath(fullpath))
        print(f"No such file or directory {filepath}.")


def plot_daily_heatmap(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        fullpath = os.path.join(filepath, "jamming", *subpath, 'heatmap.json')
        generate_heatmap(fullpath, 'Daily Low NIC Flight Percentage Heatmap')


def plot_hourly_heatmap(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        allhours = [f"{hour:02}00" for hour in range(24)]
        for hourpath in allhours:
            file = os.path.join(filepath, "jamming", *subpath, hourpath, "heatmap.json")
            title = f"Hourly Low NIC Flight Percentage Heatmap  {date}  {hourpath}"
            generate_heatmap(file, title)

def plot_aggregate_heatmap(filepath, startDate, endDate, lat_range=None, lon_range=None):
    if util.is_valid_date(startDate) and util.is_valid_date(endDate):
        allDates = util.dates_in_between(startDate, endDate)

        existing_dates = []
        fullpaths = []
        for subDate in allDates:
            fullpath = os.path.join(
                filepath,
                "jamming",
                *subDate.split("/"),
                "heatmap.json"
            )
            if os.path.isfile(fullpath):
                existing_dates.append(subDate)
                fullpaths.append(fullpath)
            else:
                print(f"No such file or directory: {fullpath}")

        if not fullpaths:
            print("No heatmap files found in the requested date range.")
            return


        df = aggregate_data(fullpaths)
        if lat_range is not None and lon_range is not None:
            lat_min, lat_max = lat_range
            lon_min, lon_max = lon_range

            df = df[
                (df["latitude"] >= lat_min) &
                (df["latitude"] <= lat_max) &
                (df["longitude"] >= lon_min) &
                (df["longitude"] <= lon_max)
                ].copy()

            region_text = (
                f"Lat {lat_min} to {lat_max}, "
                f"Lon {lon_min} to {lon_max}"
            )
        else:
            region_text = "Global"

        if df.empty:
            print("No data found after applying the selected date/range filters.")
            return

        title = (
            f"Cumulative Low-NIC Flight Percentage Heatmap "
            f"({existing_dates[0]}–{existing_dates[-1]}, {region_text})"
        )
        generate_aggregate_heatmap(df, title)
    else:
        print("Invalid startDate or endDate.")



if __name__ == '__main__':
    # plot_daily_heatmap("..\downloaded_json_files", "2025/04/24")
    # plot_hourly_heatmap("..\downloaded_json_files", "2025/04/24")
    # plot_aggregate_heatmap("..\downloaded_json_files", "2025/04/23", "2025/04/26")
    plot_aggregate_heatmap(
        "..\downloaded_json_files",
        "2025/03/23",
        "2025/04/26",
        lat_range=(24.5, 49.5),
        lon_range=(-125.0, -66.5)
    )