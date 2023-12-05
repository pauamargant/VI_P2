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

    return df


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
    hex_map = hex_map.to_crs("ESRI:102003")
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
    return ny_df, hex_buroughs


def calculate_spatial_data(df, hex_map):
    """
    Calculate spatial data based on a dataframe and a hex map.

    Args:
        df (pandas.DataFrame): The input dataframe containing latitude and longitude information.
        hex_map (geopandas.GeoDataFrame): The hex map used for spatial analysis.

    Returns:
        geopandas.GeoDataFrame: The hex map with additional spatial data.

    """
    df_coord = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    gdf = gpd.GeoDataFrame(
        df_coord, geometry=gpd.points_from_xy(df_coord.LONGITUDE, df_coord.LATITUDE)
    )[["geometry"]]
    gdf = gdf.set_crs(epsg=4326, inplace=True).to_crs("ESRI:102003")

    gdf = gpd.sjoin(gdf, hex_map, how="right", op="intersects")
    print(gdf.columns)
    gdf_count = (
        gdf.groupby(["geometry", "h3_polyfill"]).size().reset_index(name="counts")
    )
    gdf_count["counts"] = gdf_count.apply(lambda row: row["counts"], axis=1)
    df_geo = pd.DataFrame(gdf_count[["h3_polyfill", "counts"]])

    hex = hex_map.merge(
        df_geo, left_on="h3_polyfill", right_on="h3_polyfill", how="left"
    )

    # to 0 counts we sum 1
    hex["counts"] = hex["counts"].apply(lambda x: 1 if x == 0 else x)
    return hex[["h3_polyfill", "counts", "BoroName"]]


def plot_map(hex_data, mapa, ny_df, hex_buroughs, w=400, h=400):
    """
    Plots a map with hexagons representing the number of accidents,
    labels indicating the borough names, and borders for the boroughs.

    Parameters:
    - hex (alt.Chart): Altair chart object representing the hexagons.
    - ny_df (alt.Chart): Altair chart object representing the New York data.
    - hex_buroughs (alt.Chart): Altair chart object representing the hexagon boroughs.

    Returns:
    - alt.Chart: Altair chart object representing the map.
    """
    selection = alt.selection_multi(on="click", empty="all", fields=["BoroName"])
    mapa = mapa.reset_index()
    hexagons = (
        alt.Chart(mapa)
        .mark_geoshape()
        .encode(
            color=alt.Color(
                "counts:Q",
                title="Number of accidents",
                scale=alt.Scale(scheme="greenblue"),
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.5)),
            tooltip=["h3_polyfill:N", "counts:Q"],
        )
        .transform_lookup(
            lookup="h3_polyfill",
            from_=alt.LookupData(hex_data, "h3_polyfill", ["counts"]),
        )
        .project(type="identity", reflectY=True)
        .properties(width=w, height=300)
        .add_selection(selection)
    )

    labels = (
        alt.Chart(ny_df)
        .mark_text(fontWeight="bold")
        .encode(longitude="x:Q", latitude="y:Q", text="BoroName:N")
    )

    borders = (
        alt.Chart(hex_buroughs)
        .mark_geoshape(stroke="darkgray", strokeWidth=1.25, opacity=1, fillOpacity=0)
        .project(type="identity", reflectY=True)
        .encode(
            # opacity=alt.condition(selection, alt.value(1), alt.value(0.5)),
            # color=alt.condition(selection, alt.value(colors["col2"]), alt.value(colors["col1"])),
            tooltip=["BoroName:N"],
        )
        .properties(width=w, height=300)
        .add_selection(selection)
    )
    burough_chart = (
        alt.Chart(hex_data)
        .mark_bar(orient="horizontal", height=20, color=colors["col1"])
        .encode(
            x=alt.X("count()").title("Number of accidents"),
            y=alt.Y("BoroName:N", sort="-x", title=None),
            color=alt.condition(
                selection, alt.value(colors["col2"]), alt.value(colors["col1"])
            ),
            tooltip=["BoroName:N"],
        )
        .properties(width=w, height=h)
        .add_selection(selection)
    )
    return alt.layer(hexagons,borders), burough_chart
    # map_chart = alt.layer(hexagons, borders, labels)
    # return map_chart, burough_chart
    # return hexagons + labels + borders, burough_chart


def borough_chart(df, w=500, h=300):
    mapa = get_map()
    ny_df, bur = get_buroughs(mapa)
    hex_data = calculate_spatial_data(df, mapa)

    bar_chart = (
        alt.Chart(hex_data)
        .mark_bar(orient="horizontal", height=20, color=colors["col1"])
        .encode(
            x=alt.X("count()").title("Number of accidents"),
            y=alt.Y("BoroName:N", sort="-x", title=None),
        )
        .properties(width=200, height=300)
    )

    return bar_chart


def q2_preprocessing(df):
    """
    Preprocesses the given DataFrame by performing the following steps:
    1. Counts the occurrences of each vehicle type code.
    2. Selects the top 10 most frequent vehicle type codes.
    3. Replaces all other vehicle type codes with "Others".
    4. Groups the data by vehicle type code and sums the counts.
    5. Sorts the data by count in descending order.
    6. Separates the data into two parts: one with the top 10 vehicle type codes and one with "Others".
    7. Concatenates the two parts.
    8. Calculates the percentage of each vehicle type code count.

    Parameters:
    - df (pandas.DataFrame): The input DataFrame containing the vehicle type codes.

    Returns:
    - sorted_df (pandas.DataFrame): The preprocessed DataFrame with vehicle type codes and their counts and percentages.
    """
    count_df = df["VEHICLE TYPE CODE 1"].value_counts().reset_index()
    count_df.columns = ["VEHICLE TYPE CODE 1", "count"]
    top_10 = count_df.nlargest(9, "count")

    count_df["VEHICLE TYPE CODE 1"] = np.where(
        count_df["VEHICLE TYPE CODE 1"].isin(top_10["VEHICLE TYPE CODE 1"]),
        count_df["VEHICLE TYPE CODE 1"],
        "Others",
    )
    count_df = count_df.groupby("VEHICLE TYPE CODE 1").sum().reset_index()

    sorted_df = count_df.sort_values(by="count", ascending=False)

    df_part1 = sorted_df[sorted_df["VEHICLE TYPE CODE 1"] != "Others"]
    df_part2 = sorted_df[sorted_df["VEHICLE TYPE CODE 1"] == "Others"]

    sorted_df = pd.concat([df_part1, df_part2])

    sorted_df["percentage"] = (sorted_df["count"] / sorted_df["count"].sum()) * 100

    return sorted_df


def create_chart2(df, width=500, height=300):
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
        .mark_bar()
        .encode(
            y=alt.Y(
                "VEHICLE TYPE CODE 1:N",
                title=None,
                sort=df["VEHICLE TYPE CODE 1"].tolist(),
            ),
            x=alt.X(
                "percentage:Q",
                title="Percentage of accidents",
                scale=alt.Scale(domain=(0, 50)),
            ),
            color=alt.Color(
                "VEHICLE TYPE CODE 1:N",
                scale=alt.Scale(
                    domain=df["VEHICLE TYPE CODE 1"].tolist() + ["Others"],
                    range=[colors["col1"]] * (len(df["VEHICLE TYPE CODE 1"]) - 1)
                    + ["gray"],
                ),
                legend=None,
            ),
            tooltip=["VEHICLE TYPE CODE 1", "percentage"],
        )
    )

    text_labels = bar_chart.mark_text(
        align="left",
        baseline="middle",
        fontSize=12,
        dx=3,  # Adjust the horizontal position of the labels
    ).encode(
        text=alt.Text(
            "percentage:Q", format=".1f"
        ),  # Format the percentage with one decimal place
        color=alt.condition(
            alt.datum["VEHICLE TYPE CODE 1"] == "Others",
            alt.value("gray"),  # Set the text color to gray for the 'Others' category
            alt.value("black"),  # Set the text color to black for other categories
        ),
    )

    layered_chart = (
        alt.layer(bar_chart, text_labels)
        .configure_axisX(grid=True)
        .properties(width=width, height=height)
    )
    return layered_chart


def get_weather_data(
    df,
    fnames=[
        "new york city 2018-06-01 to 2018-08-31.csv",
        "new york city 2020-06-01 to 2020-08-31",
    ],
):
    """
    Retrieves weather data for a given DataFrame of accidents.

    Args:
        df (pandas.DataFrame): DataFrame containing accident data.
        fnames (list, optional): List of file names for weather data CSV files. Defaults to ["new york city 2018-06-01 to 2018-08-31.csv", "new york city 2020-06-01 to 2020-08-31"].

    Returns:
        pandas.DataFrame: DataFrame containing merged accident and weather data.
    """
    df_weather_1 = pd.read_csv("new york city 2018-06-01 to 2018-08-31.csv")
    df_weather_2 = pd.read_csv("new york city 2020-06-01 to 2020-08-31.csv")
    df_weather = pd.concat([df_weather_1, df_weather_2], axis=0)

    weather_cond = df_weather[["datetime", "conditions"]].copy()
    weather_cond["datetime"] = pd.to_datetime(
        weather_cond["datetime"], format="%Y-%m-%d"
    )

    # We  Convert 'date' column in df to the same timezone as 'datetime' column in weather_cond
    df["date"] = pd.to_datetime(pd.to_datetime(df["CRASH DATE"]).dt.date)

    # We Merge weather conditions with accidents using pd.concat
    data = df.merge(weather_cond, left_on="date", right_on="datetime", how="inner")
    return data


def weather_chart(data, w=500, h=300):
    """
    Generate a weather chart based on the given data.

    Parameters:
    - data: pandas DataFrame containing the necessary columns (date, conditions, CRASH TIME)
    - w: width of the chart (default: 500)
    - h: height of the chart (default: 300)

    Returns:
    - altair Chart object representing the weather chart
    """

    colors = {"bg": "#eff0f3", "col1": "#d8b365", "col2": "#5ab4ac"}

    per_day = (
        data[["date", "conditions", "CRASH TIME"]]
        .groupby(["date"])
        .count()
        .reset_index()
    )
    mean = per_day["CRASH TIME"].mean()

    # mean per conditions
    per_day_cond = (
        data[["date", "conditions", "CRASH TIME"]]
        .groupby(["date", "conditions"])
        .count()
        .reset_index()
    )
    mean_cond = (
        per_day_cond[["conditions", "CRASH TIME"]]
        .groupby(["conditions"])
        .mean()
        .reset_index()
    )
    mean_cond.columns = ["conditions", "mean_cond"]

    mean_cond["diff"] = mean_cond["mean_cond"].apply(lambda x: x - mean)
    bars = (
        alt.Chart(mean_cond)
        .mark_bar(height=3, orient="horizontal")
        .encode(
            y=alt.Y("conditions:N").sort("x"),
            x="diff:Q",
            color=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
        )
        .properties(width=w, height=h)
    )
    min_diff = mean_cond["diff"].min() - 0.1
    max_diff = mean_cond["diff"].max() + 0.1
    domain = [min_diff, max_diff]
    points = (
        alt.Chart(mean_cond)
        .mark_point(orient="horizontal", size=100, opacity=1, fillOpacity=1)
        .encode(
            y=alt.Y(
                "conditions:N",
                title="Conditions",
                sort="x",
                axis=alt.Axis(titleFontSize=14),
            ),
            x=alt.X("diff:Q", scale=alt.Scale(domain=domain)).title(
                "Difference in percentage"
            ),
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
        )
        .properties(width=w, height=h)
    )
    return bars + points


def q3_preprocessing(df):
    """
    Preprocesses the given DataFrame by converting the 'CRASH TIME' column to an integer representation.

    Args:
        df (pandas.DataFrame): The DataFrame to be preprocessed.

    Returns:
        pandas.DataFrame: The preprocessed DataFrame.
    """
    df = df[["CRASH TIME", "covid", "weekday"]]
    df["CRASH TIME INT"] = (
        pd.to_datetime(df["CRASH TIME"], format="%H:%M").dt.hour * 60
        + pd.to_datetime(df["CRASH TIME"], format="%H:%M").dt.minute
    )
    df["CRASH TIME INT"] = (df["CRASH TIME INT"] // 30) * 30
    df["CRASH TIME INT"] = df["CRASH TIME INT"].apply(
        lambda x: f"{x // 60:02d}:{x % 60:02d}"
    )
    return df


def create_chart3(df, color_palette, width=500, height=300):
    """
    Create a chart with morning and afternoon windows, and a before-after area plot.

    Parameters:
    - df: pandas DataFrame, the data to be plotted.
    - color_palette: dict, a dictionary containing color values for the chart.
    - width: int, optional, the width of the chart in pixels. Default is 500.
    - height: int, optional, the height of the chart in pixels. Default is 300.

    Returns:
    - chart: altair Chart object, the created chart.
    """
    morning_rh = {}
    morning_rh["x1"] = "08:00"
    morning_rh["x2"] = "09:00"
    morning_rh = pd.DataFrame([morning_rh])

    afternoon_rh = {}
    afternoon_rh["x1"] = "15:00"
    afternoon_rh["x2"] = "19:00"
    afternoon_rh = pd.DataFrame([afternoon_rh])

    morning_rh["x1"] = pd.to_datetime(morning_rh["x1"])
    morning_rh["x2"] = pd.to_datetime(morning_rh["x2"])

    afternoon_rh["x1"] = pd.to_datetime(afternoon_rh["x1"])
    afternoon_rh["x2"] = pd.to_datetime(afternoon_rh["x2"])

    morning_window = (
        alt.Chart(morning_rh)
        .mark_rect(opacity=0.1)
        .encode(x="hours(x1):T", x2="hours(x2):T", color=alt.value("gray"))
    )

    afternoon_window = (
        alt.Chart(afternoon_rh)
        .mark_rect(opacity=0.1)
        .encode(x="hours(x1):T", x2="hours(x2):T", color=alt.value("gray"))
    )

    before_after = (
        alt.Chart(width=width, height=height)
        .mark_area(size=3, opacity=0.4, interpolate="basis")
        .encode(
            x=alt.X("hours(HOUR):T"),
            y=alt.Y("count()").stack(None, title=None),
            color=alt.Color(
                "covid:N", scale=alt.Scale(range=[colors["col1"], colors["col2"]])
            ),
        )
    )
    df["HOUR"] = pd.to_datetime(df["CRASH TIME"])

    chart = (
        alt.layer(before_after, morning_window, afternoon_window, data=df)
        .facet(row=alt.Row("weekday", title=None, header=alt.Header(labelFontSize=16)))
        .configure_axis(title=None)
    )
    return chart


def get_palette():
    """
    Returns the palette of colors used for graphs.

    Returns:
        list: A list of colors.
    """
    return colors
