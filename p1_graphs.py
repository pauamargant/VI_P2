import altair as alt
import pandas as pd
import os

#!pip install geopandas
import geopandas as gpd

#!pip install geoplot
import geoplot as gplt

#!pip install geodatasets
import geodatasets

#!pip install h3pandas
import h3pandas

# import streamlit as st
import base64
import textwrap

import numpy as np

# we disable max_rows in altair
alt.data_transformers.disable_max_rows()

colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0"}
seq = [
    "#4f8c9d",
    "#5f9aa9",
    "#6fa8b4",
    "#7fb6c0",
    "#8fc4cc",
    "#9fd3d9",
    "#b0e1e5",
    "#c1f0f2",
    "#d2ffff",
]


def get_chart_1(df, w=300, h=500):
    """
    Generate a boxplot chart based on the provided dataframe.

    Parameters:
    - df: pandas.DataFrame
        The dataframe containing the data for the chart.
    - w: int, optional
        The width of the chart in pixels. Default is 300.
    - h: int, optional
        The height of the chart in pixels. Default is 500.

    Returns:
    - alt.Chart
        The generated boxplot chart.
    """
    return (
        alt.Chart(df)
        .mark_boxplot(size=30)
        .transform_aggregate(accidents="count()", groupby=["weekday", "date", "covid"])
        .encode(
            x=alt.X(
                "covid:N",
                title=None,
                axis=alt.Axis(labelFontSize=16, labelAngle=0),
                sort=["before", "after"],
            ),
            y=alt.Y("average(accidents):Q", axis=alt.Axis(labelFontSize=14)),
            color=alt.Color(
                "covid:N",
                legend=None,
                scale=alt.Scale(range=[colors["col1"], colors["col2"]]),
            ),
            column=alt.Column(
                "weekday:N",
                header=alt.Header(labelFontSize=16),
                title=None,
                sort=alt.SortField(
                    field="weekday:N", order="ascending"
                ),  # Order by weekday in descending order
            ),
        )
        .properties(width=w, height=h)
        .configure_axis(titleFontSize=16)
    )


def get_map():
    """
    Retrieves a hexagonal map of New York City.

    Returns:
        GeoDataFrame: A hexagonal map of New York City.
    """
    path = geodatasets.get_path("nybb")
    ny = gpd.read_file(path).to_crs("EPSG:4326")
    resolution = 8
    hex_map = ny.h3.polyfill_resample(resolution)
    return hex_map


def get_buroughs(hex_map):
    """
    Get the boroughs from a hex map.

    Parameters:
    - hex_map: The hex map to extract boroughs from.

    Returns:
    - ny_df: DataFrame containing centroid x, y, and borough name.
    - hex_buroughs: Dissolved hex map by borough name.
    """
    hex_buroughs = hex_map.dissolve(by="BoroName")

    ny_df = pd.DataFrame()
    ny_df["x"] = hex_buroughs.centroid.x
    ny_df["y"] = hex_buroughs.centroid.y
    ny_df["BoroName"] = hex_buroughs.index
    return ny_df, hex_buroughs.reset_index()


def get_accident_data(fname, sample=False):
    """
    Reads accident data from a CSV file and performs data preprocessing.

    Parameters:
    fname (str): The path to the CSV file.
    sample (bool, optional): Whether to sample the data. Defaults to False.

    Returns:
    pandas.DataFrame: The preprocessed accident data.
    """
    df = pd.read_csv(fname)

    df = df[
        [
            "CRASH DATE",
            "CRASH TIME",
            "BOROUGH",
            "LATITUDE",
            "LONGITUDE",
            "VEHICLE TYPE CODE 1",
        ]
    ]

    # Parse the date column as a date
    df["date"] = pd.to_datetime(df["CRASH DATE"], format="%Y-%m-%d")
    # filter year 2018 only
    df = df[df["date"].dt.year == 2018]
    # filter june, july, august
    df = df[df["date"].dt.month.isin([6, 7, 8])]
    if sample:
        df = df.sample(1000)
    # Create a column for weekday/weekend
    df["weekday"] = df["date"].dt.dayofweek
    df["weekday"] = df["weekday"].replace(
        [0, 1, 2, 3, 4, 5, 6],
        ["weekday", "weekday", "weekday", "weekday", "weekday", "weekend", "weekend"],
    )

    # Create a column indicating before or after COVID
    df["covid"] = df["date"].dt.year
    df["covid"] = df["covid"].replace([2018, 2020], ["before", "after"])
    df["VEHICLE TYPE CODE 1"] = df["VEHICLE TYPE CODE 1"].str.title()

    _, burough_map = get_buroughs(get_map())
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE))
    gdf = gdf.set_crs(epsg=4326, inplace=False)

    gdf = gpd.sjoin(gdf, burough_map, how="right", op="intersects")
    # convert to dataframe
    gdf = pd.DataFrame(gdf)
    # drop geometry
    gdf = gdf.drop(columns=["geometry"])
    return gdf



def plot_map(
    accident_data,
    selection_cond,
    selection_buro,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    w=400,
    h=400,
    ratio=0.8,
):
    ny = "https://raw.githubusercontent.com/pauamargant/VI_P1/main/resources/new-york-city-boroughs.geojson"
    data_geojson_remote = alt.Data(
        url=ny, format=alt.DataFormat(property="features", type="json")
    )

    base = (
        alt.Chart(data_geojson_remote)
        .mark_geoshape()
        .properties(
            width=500,
            height=300,
        )
        .project(type="albersUsa")
        .add_params(selection_buro)
        .encode(opacity=alt.condition(selection_buro, alt.value(0.8), alt.value(0.2)))
        .properties(width=w * ratio, height=h)
    )
    points = (
        alt.Chart(accident_data)
        .transform_filter(selection_cond & selection_month & selection_weekday & selection_vehicle & time_brush)
        .mark_circle()
        .encode(
            longitude="LONGITUDE:Q",
            latitude="LATITUDE:Q",
            size=alt.value(2),
            color=alt.value("red"),
            opacity=alt.condition(selection_buro, alt.value(1), alt.value(0)),
        )
        .add_params(selection_buro)
    )

    bar_chart = (
        alt.Chart(accident_data)
        .mark_bar()
        .transform_filter(selection_cond & selection_month & selection_weekday & selection_vehicle & time_brush)
        .encode(
            x=alt.X("count()"),
            y=alt.Y("properties\\.name:N"),
            opacity=alt.condition(selection_buro, alt.value(1), alt.value(0.4)),
        )
        .properties(width=w * (1 - ratio), height=h)
    )
    return (base + points) | bar_chart


def get_burough_chart(df, selection=None, w=500, h=300):
    bar_chart = (
        alt.Chart(df)
        .mark_bar(orient="horizontal", height=20, color=colors["col1"])
        .transform_filter(selection)
        .encode(
            x=alt.X("count()").title("Number of accidents"),
            y=alt.Y("BoroName:N", sort="-x", title=None),
        )
        .properties(width=200, height=300)
    )

    return bar_chart


def vehicle_chart(df, selection_buro, selection_cond, selection_month, selection_weekday, selection_vehicle, time_brush, width=500, height=300):
    """
    Creates a layered bar chart showing the percentage of accidents by vehicle type.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - width: int - The width of the chart (default: 500).
    - height: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    bar_chart = (
        alt.Chart(df)
        .transform_filter(selection_buro & selection_month & selection_weekday & selection_cond & time_brush)
        .transform_joinaggregate(day_count="count()", groupby=["date"])
        .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
        .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
        .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
        .mark_bar()
        .encode(
            y=alt.Y(
                "VEHICLE TYPE CODE 1:N",
                title=None,
                sort=alt.EncodingSortField(field="count", order="descending"),
            ),
            x=alt.X(
                "count()",
                title="Number of accidents"
                #scale=alt.Scale(domain=(0, 50)),
            ),
            color=alt.Color(
                "VEHICLE TYPE CODE 1:N", legend=None
            ),
            tooltip=["VEHICLE TYPE CODE 1", "count()"],
            opacity=alt.condition(selection_vehicle, alt.value(1), alt.value(0.2)),
        )
        .add_params(selection_vehicle).properties(width=width, height=height)
    )

    text_labels = bar_chart.mark_text(
        align="left",
        baseline="middle",
        fontSize=12,
        dx=3,  # Adjust the horizontal position of the labels
    ).encode(
        text=alt.Text(
            "count()"
        ),  # Format the percentage with one decimal place
        color=alt.value("black"),  # Set the text color to black for other categories,
    )

    """layered_chart = (
        alt.layer(bar_chart, text_labels)
        .configure_axisX(grid=True)
        .properties(width=width, height=height)
    )"""
    return bar_chart + text_labels


def get_weather_data(
    df,
    fname="weather.csv",
):
    """
    Retrieves weather data for a given DataFrame of accidents.

    Args:
        df (pandas.DataFrame): DataFrame containing accident data.
        fnames (list, optional): List of file names for weather data CSV files. Defaults to ["new york city 2018-06-01 to 2018-08-31.csv", "new york city 2020-06-01 to 2020-08-31"].

    Returns:
        pandas.DataFrame: DataFrame containing merged accident and weather data.
    """
    df_weather = pd.read_csv(fname)

    weather_cond = df_weather[["datetime", "conditions"]].copy()
    weather_cond["datetime"] = pd.to_datetime(
        weather_cond["datetime"], format="%Y-%m-%d"
    )

    # We  Convert 'date' column in df to the same timezone as 'datetime' column in weather_cond
    df["date"] = pd.to_datetime(pd.to_datetime(df["CRASH DATE"]).dt.date)

    # We Merge weather conditions with accidents using pd.concat
    data = df.merge(weather_cond, left_on="date", right_on="datetime", how="inner")
    return data


def weather_chart(accident_data,selection_buro,selection_cond, selection_month, selection_weekday, selection_vehicle, time_brush, w=500, h=300, ratio = 0.8):
    """
    """

        
    bars = (
        alt.Chart(accident_data)
        .transform_filter(selection_buro & selection_month & selection_weekday & selection_vehicle & time_brush)
        .transform_joinaggregate(day_count="count()", groupby=["date"])
        .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
        .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
        .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
        .mark_bar(height=3, orient="horizontal")
        .encode(
            y=alt.Y("conditions:N").sort("x"),
            x="min(diff):Q",
            color=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
            fill=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
            opacity=alt.condition(selection_cond, alt.value(1), alt.value(0.2)),
        )
        .properties(width=w * ratio, height=h)
        .add_params(selection_cond)
    )
    dots = (
        alt.Chart(accident_data)
        .transform_filter(selection_buro  & selection_month & selection_weekday & selection_vehicle & time_brush)
        .transform_joinaggregate(day_count="count()", groupby=["date"])
        .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
        .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
        .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
        .mark_point(height=3, orient="horizontal", size=100)
        .encode(
            y=alt.Y("conditions:N").sort("x"),
            x="min(diff):Q",
            color=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
            fill=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
            opacity=alt.condition(selection_cond, alt.value(1), alt.value(0.2)),
        )
        .properties(width=w * ratio, height=h)
        .add_params(selection_cond)
    )
    bar_legend = (
        alt.Chart(accident_data)
        .mark_rect()
        .transform_filter(selection_buro  & selection_month & selection_weekday )
        .transform_joinaggregate(day_count="count()", groupby=["date"])
        .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
        .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
        .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
        .encode(
            y=alt.Y("conditions:N", sort=alt.EncodingSortField(field="diff")),
            color="count()",
            opacity=alt.condition(selection_cond, alt.value(1), alt.value(0.2)),
        )
        .properties(width=w * (1-ratio), height=h)
        .add_params(selection_cond)
    )
    return (bars + dots) | bar_legend


def calendar_chart(accident_data, selection_buro, selection_cond, selection_month, selection_weekday, selection_vehicle, time_brush, w=200,h=300):
    
    return alt.Chart(accident_data).mark_rect().transform_filter(selection_cond & selection_buro & selection_vehicle & time_brush).encode(
        x = alt.X('weekday'),
        y = alt.Y('week:O',scale=alt.Scale(domain=[5,4,3,2,1])),
        row = alt.Column('month:O'),
        color = alt.Color('count()'),
        opacity=alt.condition(selection_month & selection_weekday, alt.value(1), alt.value(0.2))
    ).add_params(selection_month, selection_weekday).properties(width=w, height=h)


def time_of_day_chart(df, selection_buro,selection_cond, selection_month, selection_weekday, selection_vehicle, time_brush, width=600, height=300):

    base = (
        alt.Chart(df, width=width, height=height)
        .transform_filter(selection_buro & selection_month & selection_weekday & selection_cond & selection_vehicle)
        .transform_joinaggregate(day_count="count()", groupby=["date"])
        .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
        .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
        .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
        .mark_area(size=3, opacity = 0.3, interpolate="linear").encode(
        x=alt.X("HOUR:T"),
        y=alt.Y("count()").stack(None, title="Accidents per hour")
        )
    )

    background = base.add_selection(time_brush)
    selected = base.transform_filter(time_brush).mark_area(opacity=0.8)

    return background + selected

def get_palette():
    """
    Returns the palette of colors used for graphs.

    Returns:
        list: A list of colors.
    """
    return colors
