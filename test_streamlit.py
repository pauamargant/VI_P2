from p1_graphs import *
import altair as alt
import streamlit as st


@st.cache_data
def get_data():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather.csv")
    return accident_data


@st.cache_data
def make_graph():
    accident_data = get_data()

    selection_cond = alt.selection_point(on="click", fields=["conditions"])
    selection_acc_map = alt.selection_interval()
    selection_buro = alt.selection_point(fields=["properties.name"])
    selection_vehicle = alt.selection_multi(on="click", fields=["VEHICLE TYPE CODE 1"])
    time_brush = alt.selection_interval(fields=["HOUR"])
    selection_weekday = alt.selection_point(fields=["weekday"])
    selection_month = alt.selection_multi(fields=["month"])

    h = 400
    ratio = 0.2
    w = 1000
    geo_view = get_map_chart(
        accident_data,
        selection_cond,
        selection_buro,
        selection_acc_map,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
        w=w,
        ratio=0.9,
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
        w=w * 0.2,
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
    )
    hash = "hash"
    return hash, (
        geo_view
        & (weather | calendar).resolve_scale(color="independent")
        & (vehicles | time_of_day)
    ).configure_scale(bandPaddingInner=0)


# .configure_scale(bandPaddingInner=0)
hash, plot = make_graph()
# make button to reset selection
st.button("Reset Selection")
st.altair_chart(plot)
