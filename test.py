from graphs import *

accident_data = get_accident_data("dataset_v1.csv")
ny = "https://raw.githubusercontent.com/pauamargant/VI_P1/main/resources/new-york-city-boroughs.geojson"
data_geojson_remote = alt.Data(
    url=ny, format=alt.DataFormat(property="features", type="json")
)

# make month dropdown
month_dropdown = alt.binding_select(
    options=[[6, 7, 8, 9], 6, 7, 8, 9],
    name="month",
    labels=["All", "June", "July", "August", "September"],
)
selection_month_dropdown = alt.selection_single(
    fields=["month"], bind=month_dropdown, name="month"
)

base = (
    alt.Chart(accident_data)
    .mark_geoshape()  # fill=colors["col3"]
    .properties(
        width=500,
        height=300,
    )
    # .transform_filter(selection_month_dropdown)
    .transform_lookup(
        lookup="name",
        from_=alt.LookupData(data_geojson_remote, "name"),
        as_="geom",
        default="Other",
    )
    .transform_calculate(geometry="datum.geom.geometry", type="datum.geom.type")
    .mark_geoshape()
    .project(type="albersUsa")
    .encode(
        # opacity=alt.condition(selection_buro, alt.value(0.6), alt.value(0.2)),
        color=alt.Color("name:N"),
        tooltip=["name:N"],
    )
    .interactive()
    # .add_params(selection_month_dropdown)
)
import streamlit as st

st.altair_chart(base)
