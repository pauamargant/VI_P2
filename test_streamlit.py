import streamlit as st
from p1_graphs import *
import altair as alt

data = get_accident_data(fname="dataset_v1.csv", sample=True)
accident_data = get_weather_data(data, fname="weather.csv")
mapa = get_map()
accident_data.head()
# create properties.name column equal to BoroName
accident_data["properties.name"] = accident_data["BoroName"]

colors = {"bg": "#eff0f3", "col1": "#d8b365", "col2": "#5ab4ac"}
w = 600
h = 400
ratio = 0.2
# accident_data = get_weather_data(data,fname = "weather.csv")
print(accident_data.columns)
selection_cond = alt.selection_multi(on="click", empty="all", fields=["conditions"])
# choropleth, _ = plot_map(hex_data, mapa, ny_df, bur,selection_buro,selection_cond)


ny = "https://raw.githubusercontent.com/pauamargant/VI_P1/main/resources/new-york-city-boroughs.geojson"
data_geojson_remote = alt.Data(
    url=ny, format=alt.DataFormat(property="features", type="json")
)
selection_buro = alt.selection_point(fields=["properties.name"], empty="all")
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
)
points = (
    alt.Chart(accident_data)
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
    .transform_filter(selection_cond)
    .encode(
        x=alt.X("count()"),
        y=alt.Y("properties\\.name"),
        opacity=alt.condition(selection_buro, alt.value(1), alt.value(0.4)),
    )
)
geo_view = (base + points) | bar_chart


bars = (
    alt.Chart(accident_data)
    .transform_filter(selection_buro)
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
    .properties(width=w * (1 - ratio), height=h)
    .add_params(selection_cond)
)
dots = (
    alt.Chart(accident_data)
    .transform_filter(selection_buro)
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
    .properties(width=w * (1 - ratio), height=h)
    .add_params(selection_cond)
)
bar_legend = (
    alt.Chart(accident_data)
    .mark_rect()
    .transform_filter(selection_buro)
    .transform_joinaggregate(day_count="count()", groupby=["date"])
    .transform_joinaggregate(per_day_cond="mean(day_count)", groupby=["conditions"])
    .transform_joinaggregate(per_day_mean="mean(day_count)", groupby=[])
    .transform_calculate(diff="datum.per_day_cond - datum.per_day_mean")
    .encode(
        y=alt.Y("conditions:N", sort=alt.EncodingSortField(field="diff")),
        color="count()",
        opacity=alt.condition(selection_cond, alt.value(1), alt.value(0.2)),
    )
    .properties(width=w * ratio, height=h)
    .add_params(selection_cond)
)

plot = geo_view & (bars + dots | bar_legend)
st.altair_chart(plot)
