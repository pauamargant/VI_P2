from p1_graphs import *
import altair as alt
import streamlit as st


@st.cache_data
def get_data():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather.csv")
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
        "conditions",
        "VEHICLE TYPE CODE 1",
    ]

    # select only cols
    accident_data = accident_data[cols]
    return accident_data


@st.cache_data
def make_graph():
    accident_data = get_data()

    selection_cond = alt.selection_point(on="click", fields=["conditions"])
    selection_acc_map = alt.selection_interval()
    selection_buro = alt.selection_point(fields=["name"])
    selection_vehicle = alt.selection_multi(on="click", fields=["VEHICLE TYPE CODE 1"])
    time_brush = alt.selection_point(fields=["HOUR"])
    # day_brush = alt.selection_interval(encodings=['x'])

    # weekday_dropdown = alt.binding_select(options=[[0,1,2,3,4],[5,6]],name='weekday',labels=['weekday','weekend'])
    selection_weekday = alt.selection_point(fields=["weekday"])

    # make month dropdown
    month_dropdown = alt.binding_select(
        options=[[6, 7, 8, 9], 6, 7, 8, 9],
        name="month",
        labels=["All", "June", "July", "August", "September"],
    )
    selection_month = alt.selection_point(fields=["month"])

    # selection_day = alt.selection_point(fields=['weekday','month-week'], empty=True)
    # selection_day_aux = alt.selection_point(fields=['weekday','month','week'],empty=False)

    h = 400
    ratio = 0.2
    w = 1000
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
        h=399 + 4,
        w=w * 0.7,
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
        h=399,
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
        h=399 + 4,
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
        h=399,
    )

    plot = (
        (geo_view | vehicles)
        & (weather).resolve_scale(color="independent")
        & (calendar | time_of_day).resolve_scale(color="independent")
    ).configure_scale(bandPaddingInner=0)
    hash = "hash"
    return hash, plot


# .configure_scale(bandPaddingInner=0)
hash, plot = make_graph()
# make button to reset selection
st.button("Reset Selection")
st.altair_chart(plot)
