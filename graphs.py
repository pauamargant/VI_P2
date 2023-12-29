import altair as alt
import pandas as pd
import geopandas as gpd
from geodatasets import get_path
import numpy as np

# we disable max_rows in altair
alt.data_transformers.disable_max_rows()

# We define the color style palette
colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0", "col3": "#c3dee6"}
# Sequential palette
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


# Columns which must be in all datasets for all charts, because of the
# interactivity
filter_cols = [
    "name",
    "monthname",
    "VEHICLE TYPE CODE 1",
    "HOUR",
    "dayname",
    "CONTRIBUTING FACTOR VEHICLE 1",
    "conditions",
    "LATITUDE",
    "LONGITUDE",
    "week",
    "date",
    "fulldate",
    "INJURED",
    "num_days_in_month",
]


def get_map():
    """
    Retrieves a map of New York City.

    Returns:
        GeoDataFrame: A map of New York City, with buroughs divisions.
    """
    path = get_path("nybb")
    ny = gpd.read_file(path).to_crs("EPSG:4326")
    return ny


def get_buroughs():
    """
    Get the boroughs from ny map.

    Returns:
    - buroughs: Buroughs geodataframe.
    """
    path = get_path("nybb")
    buroughs = gpd.read_file(path).to_crs("EPSG:4326")

    return buroughs.reset_index()


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

    # Parse the date column as a date
    df["date"] = pd.to_datetime(df["CRASH DATE"])  # , format="%Y-%m-%d")
    # filter year 2018 only
    df = df[df["date"].dt.year == 2018]
    # filter june, july, august
    df = df[df["date"].dt.month.isin([6, 7, 8, 9])]
    if sample:
        df = df.sample(1000)

    df["VEHICLE TYPE CODE 1"] = df["VEHICLE TYPE CODE 1"].str.title()

    # filter types of vehicles
    df["VEHICLE TYPE CODE 1"] = df["VEHICLE TYPE CODE 1"].replace(
        ["Fire Truck"], "FIRE"
    )
    df["VEHICLE TYPE CODE 1"] = df["VEHICLE TYPE CODE 1"].replace(
        ["Ambulance"], "AMBULANCE"
    )
    df["VEHICLE TYPE CODE 1"] = df["VEHICLE TYPE CODE 1"].replace(["Taxi"], "TAXI")
    df = df[df["VEHICLE TYPE CODE 1"].isin(["FIRE", "AMBULANCE", "TAXI"])]

    # create HOUR column from CRASH TIME
    df["CRASH TIME"] = pd.to_datetime(df["CRASH TIME"])
    df["HOUR"] = df["CRASH TIME"].dt.hour

    df["weekday"] = df["date"].dt.weekday
    df["weekday_name"] = df["date"].dt.day
    # make weekend column
    df["weekend"] = df["weekday"].apply(lambda x: 1 if x > 4 else 0)

    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month

    # for each month we get the minimum week number, to get the
    # week number within the month
    #min_week = df.groupby(["month"])["week"].min().reset_index()

    #df = pd.merge(df, min_week, on="month", how="left")
    #df["week"] = df["week_x"] - df["week_y"] + 1

    replacement_dict = {
    'Passing Too Closely': 'Traffic Violation - Passing Too Closely',
    'Driver Inattention/Distraction': 'Driver Distraction',
    'Unspecified': 'Unclear Reason',
    'Following Too Closely': 'Tailgating',
    'Turning Improperly': 'Improper Turning',
    'Unsafe Lane Changing': 'Unsafe Lane Change',
    'Pedestrian/Bicyclist/Other Pedestrian Error/Confusion': 'Pedestrian/Bicyclist Error/Confusion',
    'Driver Inexperience': 'Inexperienced Driver',
    'Reaction to Uninvolved Vehicle': 'Reaction to Other Vehicle',
    'Aggressive Driving/Road Rage': 'Aggressive Driving/Road Rage',
    'Passing or Lane Usage Improper': 'Improper Passing/Lane Usage',
    'Other Vehicular': 'Other Vehicle Related',
    'Traffic Control Disregarded': 'Disregarded Traffic Control',
    'Failure to Yield Right-of-Way': 'Failure to Yield',
    'Unsafe Speed': 'Excessive Speed',
    'Fell Asleep': 'Drowsy Driving',
    'Passenger Distraction': 'Passenger Distraction',
    'Oversized Vehicle': 'Oversized Vehicle',
    'Backing Unsafely': 'Unsafe Backing',
    'Failure to Keep Right': 'Failure to Keep Right',
    'Outside Car Distraction': 'External Distraction',
    'Tire Failure/Inadequate': 'Tire Failure/Inadequate',
    'View Obstructed/Limited': 'Limited Visibility',
    'Glare': 'Glare Effect',
    'Alcohol Involvement': 'Alcohol Impairment',
    'Obstruction/Debris': 'Road Obstruction/Debris',
    'Pavement Slippery': 'Slippery Pavement',
    'Brakes Defective': 'Defective Brakes',
    'Cell Phone (hand-Held)': 'Cell Phone Usage',
    'Drugs (illegal)': 'Illegal Drug Usage',
    'Driverless/Runaway Vehicle': 'Runaway Vehicle',
    'Steering Failure': 'Steering Failure',
    'Accelerator Defective': 'Defective Accelerator',
    'Pavement Defective': 'Defective Pavement',
    'Fatigued/Drowsy': 'Driver Fatigue',
    'Other Lighting Defects': 'Lighting Defects',
    'Vehicle Vandalism': 'Malicious Damage'
}

    df['CONTRIBUTING FACTOR VEHICLE 1'] = df['CONTRIBUTING FACTOR VEHICLE 1'].replace(replacement_dict)


    df["dayname"] = df["date"].dt.day_name()
    df["monthname"] = df["date"].dt.month_name()
    df["num_days_in_month"] = df["monthname"].apply(
        lambda x: 30 if x in ["June", "September"] else 31
    )

    df["fulldate"] = (
        df["monthname"] + " " + df["date"].dt.day.astype(str) + ", " + df["dayname"]
    )

    df["INJURED"] = (
        df["NUMBER OF PEDESTRIANS INJURED"]
        + df["NUMBER OF CYCLIST INJURED"]
        + df["NUMBER OF MOTORIST INJURED"]
        + df["NUMBER OF PERSONS INJURED"]
    )
    # We assign 0 if = 0 and 1 if >0
    df["INJURED"] = df["INJURED"].apply(
        lambda x: "with injuries" if x > 0 else "without injuries"
    )

    # Given that a lot of null values are present in burough, we
    # use the coordinates to get the burough

    burough_map = get_buroughs()
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE))
    gdf = gdf.set_crs(epsg=4326, inplace=False)

    gdf = gpd.sjoin(gdf, burough_map, how="right", op="intersects")
    # convert to dataframe
    gdf = pd.DataFrame(gdf)
    gdf = gdf.rename(columns={"BoroName": "name"})

    # make column month_number- week_number
    gdf["month-week"] = gdf["month"].astype(str) + "-" + gdf["week"].astype(str)

    # drop geometry
    gdf = gdf.drop(columns=["geometry"])

    return gdf


def get_weather_data(
    df,
    fname="weather2018.csv",
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

    df["date"] = pd.to_datetime(pd.to_datetime(df["CRASH DATE"]).dt.date)

    data = df.merge(weather_cond, left_on="date", right_on="datetime", how="inner")
    return data


def get_map_chart(
    accident_data,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=400,
    h1=400,
    h2=200,
    ratio=0.8,
):
    """
    Creates an interactive map of New York City, showing the number of accidents per burough
    in a bar chart

    Parameters:
        -accident_data (DataFrame): The input DataFrame containing the data for the chart.
        - (Selectors for interactivity) ....
        - w (int): The width of the chart
        - h1 (int): the height of the map chart
        - h2 (int): the height of the bar chart
        - ratio (float): the ratio between the map chart and the bar chart in width

    """
    ny = "https://raw.githubusercontent.com/pauamargant/VI_P1/main/resources/new-york-city-boroughs.geojson"
    data_geojson_remote = alt.Data(
        url=ny, format=alt.DataFormat(property="features", type="json")
    )

    # We create the base map
    base = (
        alt.Chart(data_geojson_remote)
        .mark_geoshape(fill="lightgrey", stroke = "white")
        .properties(
            width=500,
            height=300,
        )
        .project(type="albersUsa")
        .encode(
            opacity=alt.condition(selection_buro, alt.value(0.6), alt.value(0.2)),
            tooltip=[alt.Tooltip("name:N", title="Borough")],
        )
        .properties(width=w * ratio, height=h1)
    )

    accident_data = accident_data[filter_cols]

    # We create the points corresponding to the accidents
    points = (
        alt.Chart(accident_data)
        .transform_filter(
            selection_cond
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_injured
            & selection_acc_factor
        )
        .mark_circle()
        .encode(
            longitude="LONGITUDE:Q",
            latitude="LATITUDE:Q",
            size=alt.value(2),
            color=alt.Color(
                "name:N",
                legend=alt.Legend(title="Borough", orient="top-left"),
            ).scale(
                # scheme="category20c"
                range=["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]
            ),
            opacity=alt.condition(
                selection_buro & selection_acc_map, alt.value(1), alt.value(0)
            ),
            tooltip=alt.value(None),
        )
        .add_params(selection_acc_map)
    )

    # We create the bar chart of the number of accidents per burough
    bar_chart = (
        alt.Chart(accident_data)
        .mark_bar()
        .transform_filter(
            selection_cond
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_injured
            & selection_acc_map
            & selection_acc_factor
        )
        .encode(
            x=alt.X("count()", axis=alt.Axis(title=None)),
            y=alt.Y("name:N", axis=alt.Axis(title="Boroughs")).sort("-x"),
            opacity=alt.condition(selection_buro, alt.value(1), alt.value(0.4)),
            color=alt.Color("name:N", legend=None).scale(
                range=["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]
            ),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("name:N", title="Borough"),
            ],
        )
        .properties(width=w * 0.3, height=h2, title="Accidents by Borough")
    )

    # We create the layered chart and return a tuple with the map and the bar chart
    return (base + points).add_params(selection_buro), bar_chart.add_params(
        selection_buro
    )


def get_vehicle_chart(
    df,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=500,
    h=300,
):
    """
    Creates a layered bar chart showing the percentage of accidents by vehicle type.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    df = df[filter_cols]
    bar_chart = (
        alt.Chart(df)
        .transform_filter(
            selection_buro
            & selection_month
            & selection_weekday
            & selection_cond
            & time_brush
            & selection_injured
            & selection_acc_map
            & selection_acc_factor
        )
        .mark_bar()
        .encode(
            y=alt.Y(
                "VEHICLE TYPE CODE 1:N",
                title=None,
            ).sort("x"),
            x=alt.X("count()", title="Number of accidents"),
            tooltip=[
                alt.Tooltip("VEHICLE TYPE CODE 1:N", title="Type of vehicle"),
                alt.Tooltip("count()", title="No. accidents"),
            ],
            opacity=alt.condition(selection_vehicle, alt.value(1), alt.value(0.2)),
        )
        .add_params(selection_vehicle)
        .properties(width=w, height=h)
    )

    text_labels = bar_chart.mark_text(
        align="left",
        baseline="middle",
        fontSize=12,
        dx=3,  # Adjust the horizontal position of the labels
    ).encode(
        text=alt.Text("count()"),
        color=alt.value("black"),
    )

    text_emoji = (
        bar_chart.mark_text(
            align="left",
            baseline="middle",
            fontSize=30,
            dx=0,
        )
        .encode(text=alt.Text("emoji:N"))
        .transform_calculate(
            emoji="{'AMBULANCE':'🚑','FIRE':'🚒','TAXI':'🚕'}[datum['VEHICLE TYPE CODE 1']]"
        )
    )

    return bar_chart + text_emoji


def get_weather_chart(
    accident_data,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=500,
    h=300,
    ratio=0.8,
):
    """
    Creates a layered bar chart showing the count of accidents per weather type.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    custom_sort = [
        "Clear",
        "Partially cloudy",
        "Overcast",
        "Rain",
        "Rain, Overcast",
        "Rain, Partially cloudy",
    ]
    accident_data = accident_data[filter_cols]
    bar_legend = (
        alt.Chart(accident_data)
        .transform_filter(
            selection_acc_map
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_injured
            & selection_acc_factor
            & selection_buro
        )
        .mark_rect()
        .encode(
            y=alt.Y("conditions:N", sort=custom_sort, axis=alt.Axis(title=None)),
            color=alt.Color(
                "count()",
                legend=alt.Legend(title="No. accidents"),
                scale=alt.Scale(scheme="blues"),
            ),
            opacity=alt.condition(selection_cond, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("conditions:N", title="Weather"),
            ],
        )
        .properties(width=w * (1 - ratio), height=h, title="Weather conditions")
        .add_params(selection_cond)
    )
    return bar_legend


def get_calendar_chart(
    accident_data,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=500,
    h=300,
    ratio=0.8,
):
    """
    Creates a layered bar chart showing the accident count in a calendar like chart.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    accident_data = accident_data[filter_cols]

    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    month_order = ["June", "July", "August", "September"]

    calendars = (
        alt.Chart(accident_data)
        .transform_filter(
            selection_acc_map
            & selection_cond
            & selection_month
            & selection_vehicle
            & time_brush
            & selection_injured
            & selection_acc_factor
            & selection_buro
        )
        .mark_rect()
        .encode(
            row=alt.Row("monthname:O", sort=month_order, spacing=0, title=None),
            x=alt.X("dayname:O", sort=order, axis=alt.Axis(title=None)),
            y=alt.Y("week:O", title=None, axis=alt.Axis(labels=False)),
            color=alt.Color(
                "count()",
                scale=alt.Scale(scheme="greens"),
                legend=alt.Legend(title="No. accidents", orient="top"),
            ),
            opacity=alt.condition(
                selection_weekday,
                alt.value(1),
                alt.value(0.2),
            ),
            tooltip=[
                alt.Tooltip("fulldate:N", title="Date"),
                alt.Tooltip("count()", title="No. accidents"),
            ],
        )
        .properties(width=int(w), height=int(h / 4)).resolve_scale(y="independent")
    )

    return calendars


def get_counts_chart(
    accident_data,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=100,
    h=70,
    ratio=0.8,
):
    """
    Creates a layered bar chart showing the total accident count, the currenlty selected count
    and the count of accidents with and without injuries.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    accident_data = accident_data[filter_cols]

    total_chart = (
        alt.Chart(accident_data)
        .mark_bar(cornerRadius=10)
        .encode(
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
            ],
        )
    )

    total_text = (
        total_chart.mark_text(
            align="center",
            baseline="middle",
            fontSize=25,
            dx=0,
            fontWeight="bold",
        )
        .encode(
            text=alt.Text("count()"),
            color=alt.value("white"),
            x=alt.X().axis(labels=False),
        )
        .properties(width=int(w), height=int(h), title="Total accidents")
    )
    selected_text = (
        total_chart.transform_filter(
            selection_acc_map
            & selection_buro
            & selection_cond
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_acc_factor
            & selection_injured
        )
        .mark_text(
            align="center",
            baseline="middle",
            fontSize=25,
            dx=0,
            fontWeight="bold",
        )
        .encode(
            text=alt.Text("count()"),
            color=alt.value("white"),
            x=alt.X().axis(labels=False),
        )
        .properties(width=int(w), height=int(h), title="Currently selected")
    )
    injured_chart = (
        alt.Chart(accident_data)
        .mark_bar(cornerRadius=10)
        .transform_filter(
            selection_acc_map
            & selection_buro
            & selection_cond
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_acc_factor
        )
        .encode(
            opacity=alt.condition(selection_injured, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
            ],
            #color=alt.value("blue"),
            x=alt.X("INJURED:N", title=None, axis=alt.Axis(ticks=False, labelAngle=0, orient="top")),
        )
    )
    injured_text = (
        injured_chart.mark_text(
            align="center",
            baseline="middle",
            fontSize=15,
            dx=0,
            fontWeight="bold",
        )
        .encode(
            text=alt.Text("count()"),
            color=alt.value("white"),
        )
        .properties(width=int(w*1.8), height=int(h * 0.8))
    )

    injured_chart = (injured_chart + injured_text).add_params(selection_injured)
    return (total_chart + total_text) | (total_chart + selected_text) | injured_chart


def get_month_chart(
    accident_data,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=500,
    h=300,
    ratio=0.8,
):
    """
    Creates a layered bar chart showing the total accident count per month.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data."""

    accident_data = accident_data[filter_cols]

    month_order = ["June", "July", "August", "September"]

    month_bar = (
        alt.Chart(accident_data)
        .mark_bar(cornerRadius=10)
        .transform_filter(
            selection_acc_map
            & selection_cond
            # & selection_month
            # & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_injured
            & selection_acc_factor
        )
        .transform_window(
            total_acc="count()",
            frame=[None, None],
            groupby=["monthname"],
        )
        .transform_calculate(
            mean_accidents=alt.datum.total_acc / alt.datum.num_days_in_month,
        )
        .encode(
            y=alt.Y(
                "monthname:N",
                sort=month_order,
                title=None,
                axis=alt.Axis(labels=False, ticks=False),
            ),
            color=alt.Color(
                "mean_accidents:Q", scale=alt.Scale(scheme="greens")
            ),
            opacity=alt.condition(selection_month, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("monthname:N", title="Month"),
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("mean_accidents:Q", format=",.2f", title="Mean accidents"),
            ],
        )
        .properties(width=int(h / 4), height=int(h))
        .add_params(selection_month)
    )

    text = month_bar.mark_text(
        align="center",
        baseline="middle",
        fontSize=15,
        dx=0,
        fontWeight="bold",
    ).encode(
        text=alt.Text("monthname:N"),
        color=alt.value("black"),
    )

    return month_bar + text


def get_time_of_day_chart(
    df,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=600,
    h=300,
):
    """
    Creates a layered bar chart showing the accidents per time of day and weekday. It includes a bar chart for the time of day
    and weekday axis.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 500).
    - w: int - The height of the chart (default: 300).

    Returns:
    - layered_chart: LayeredChart - The layered bar chart visualizing the data.
    """
    df = df[filter_cols]
    h1 = int(2 * h / 3)
    h2 = int(1 * h / 3)
    w1 = int(3 * w / 4)
    w2 = int(w / 8)

    custom_sort = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    base = (
        alt.Chart()
        .mark_rect()
        .encode(
            x=alt.X("HOUR:O", axis=alt.Axis(title="Hour of the day")),
            y=alt.Y("dayname:O", sort=custom_sort, axis=alt.Axis(title=None)),
        )
        .transform_filter(
            selection_cond
            & selection_buro
            & selection_vehicle
            & selection_acc_map
            & selection_acc_factor
            & selection_month
            & selection_injured
        )
    )

    times_of_day = (
        base.mark_rect(stroke="grey")
        .encode(
            color=alt.Color(
                "count()",
                scale=alt.Scale(scheme="tealblues"),
                legend=alt.Legend(title="Number of accidents"),
            ),
            opacity=alt.condition(
                time_brush & selection_weekday, alt.value(1), alt.value(0.2)
            ),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("HOUR:O", title="Hour"),
                alt.Tooltip("dayname:O", title="Day"),
            ],
        )
        .properties(width=w1, height=h1)
        .add_params(time_brush, selection_weekday)
    )

    hour_bar = (
        alt.Chart()
        .mark_bar()
        .transform_filter(
            selection_cond
            & selection_buro
            & selection_vehicle
            & selection_acc_map
            & selection_acc_factor
            & selection_month
            & selection_injured
        )
        .encode(
            y=alt.Y(
                "count()",
                scale=alt.Scale(reverse=False),
                axis=alt.Axis(title="No. accidents"),
            ),
            x=alt.X("HOUR:O", axis=None),
            opacity=alt.condition(time_brush, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("HOUR:O", title="Hour"),
            ],
        )
        .properties(width=int(w1), height=h2)
        .add_params(time_brush)
    )
    weekday_bar = (
        alt.Chart()
        .mark_bar()
        .transform_filter(
            selection_cond
            & selection_buro
            & selection_vehicle
            & selection_acc_map
            & selection_acc_factor
            & selection_month
            & selection_injured
        )
        .encode(
            x=alt.X("count()", axis=alt.Axis(title="No. accidents")),
            y=alt.Y("dayname:O", axis=None, sort=custom_sort),
            opacity=alt.condition(selection_weekday, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("count()", title="No. accidents"),
                alt.Tooltip("dayname:O", title="Day"),
            ],
        )
        .properties(width=w2, height=h1)
        .add_params(selection_weekday)
    )

    time_chart = alt.vconcat(
        hour_bar,
        alt.hconcat(times_of_day, weekday_bar).resolve_scale(y="shared"),
        data=df,
    ).resolve_scale(color="shared", x="shared")
    return time_chart


def get_factor_chart(
    df,
    selection_buro,
    selection_acc_map,
    selection_cond,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_injured,
    selection_acc_factor,
    w=600,
    h=300,
):
    """
    Makes a bar chart showing the number of accidents per contributing factor. It shows the top 10.

    Parameters:
    - df: DataFrame - The input DataFrame containing the data for the chart.
    - (Selectors for interactivity)
    - w: int - The width of the chart (default: 600).
    - w: int - The height of the chart (default: 300).

    Returns:
    - bar_chart: LayeredChart - The layered bar chart visualizing the data.

    """
    df = df[filter_cols]
    return (
        alt.Chart(df)
        .mark_bar()
        .transform_filter(
            selection_buro
            & selection_acc_map
            & selection_cond
            & selection_month
            & selection_weekday
            & selection_vehicle
            & time_brush
            & selection_injured
        )
        .encode(
            y=alt.Y(
                "CONTRIBUTING FACTOR VEHICLE 1:N",
                axis=alt.Axis(title=None, orient="right"),
            ).sort("-x"),
            x=alt.X("counter:Q", axis=alt.Axis(title="No. accidents per Contributing Factor", orient="bottom", labelLimit=2000), scale=alt.Scale(reverse=True)),
            opacity=alt.condition(selection_acc_factor, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("counter:Q", title="No. accidents"),
                alt.Tooltip("CONTRIBUTING FACTOR VEHICLE 1:N", title="Factor"),
            ],
        )
        .transform_aggregate(
            counter="count()", groupby=["CONTRIBUTING FACTOR VEHICLE 1"]
        )
        .transform_window(
            rank="rank(counter)", sort=[alt.SortField("counter", order="descending")]
        )
        .transform_filter((alt.datum.rank <= 10))
        .add_params(selection_acc_factor)
        #.properties(title="Top 10 Contributing Factors")
    )


def make_visualization(accident_data):
    """
    It creates the whole visualization, with all the charts and interactivity.

    Parameters:
    - accident_data: DataFrame - The input DataFrame containing the data for the chart.

    Returns:
    - chart: LayeredChart - The layered chart visualizing the data.
    """
    w = 600
    h = 400
    ratio = 0.2

    selection_cond = alt.selection_point(on="click", fields=["conditions"])
    selection_acc_map = alt.selection_interval(fields=["LATITUDE", "LONGITUDE"])
    selection_buro = alt.selection_point(fields=["name"])
    selection_vehicle = alt.selection_point(on="click", fields=["VEHICLE TYPE CODE 1"])
    time_brush = alt.selection_point(fields=["HOUR"])
    selection_injured = alt.selection_point(fields=["INJURED"])

    selection_weekday = alt.selection_point(fields=["dayname"])

    month_dropdown = alt.binding_select(
        options=[
            "June, July, August, September",
            "June",
            "July",
            "August",
            "September",
        ],
        name="month",
        labels=["All", "June", "July", "August", "September"],
    )
    selection_month = alt.selection_point(fields=["monthname"])
    selection_acc_factor = alt.selection_point(fields=["CONTRIBUTING FACTOR VEHICLE 1"])

    cols = [
        "CRASH DATE",
        "LATITUDE",
        "LONGITUDE",
        "date",
        "HOUR",
        "week",
        "weekday",
        "month",
        "name",
        "VEHICLE TYPE CODE 1",
        "CONTRIBUTING FACTOR VEHICLE 1",
        "dayname",
        "monthname",
        "conditions",
        "fulldate",
        "INJURED",
        "num_days_in_month",
    ]

    accident_data = accident_data[cols]
    w = 800
    geo_view, bur_chart = get_map_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h1=600,
        h2=200,
        w=w,
        ratio=0.7,
    )
    weather = get_weather_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=399,
        w=w * 0.8,
        ratio=0.8,
    )
    calendar = get_calendar_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=550,
        w=w * 0.3,
    )
    months = get_month_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=550,
        w=w * 0.3,
    )
    vehicles = get_vehicle_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=200,
        w=w * 0.3,
    )
    time_of_day = get_time_of_day_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=250,
        w = 600,
    )
    acc_factor = get_factor_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h = 200,
        w = 2000,
    )

    counts = get_counts_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        selection_injured,
        selection_acc_factor,
        h=70,
        w=100,
    )
    chart = ( 
        (geo_view | (counts & ((bur_chart & vehicles) | weather)))
        & ((months | calendar).resolve_scale(color="shared") | ((time_of_day & acc_factor).resolve_scale(color="independent")))    
    )

    return chart
