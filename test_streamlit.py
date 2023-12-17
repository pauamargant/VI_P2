from p1_graphs import *
import altair as alt
import streamlit as st


@st.cache_data
def make_graph():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather.csv")
    colors = {"bg": "#eff0f3", "col1": "#d8b365", "col2": "#5ab4ac"}
    w = 600
    h = 400
    ratio = 0.2
    # accident_data = get_weather_data(data,fname = "weather.csv")
    print(accident_data.columns)
    selection_cond = alt.selection_point(on="click", fields=["conditions"])
    selection_acc_map = alt.selection_interval()
    selection_buro = alt.selection_point(fields=["properties.name"])
    selection_vehicle = alt.selection_multi(on="click", fields=["VEHICLE TYPE CODE 1"])
    time_brush = alt.selection_interval(fields=["HOUR"])
    # day_brush = alt.selection_interval(encodings=['x'])

    # weekday_dropdown = alt.binding_select(options=[[0,1,2,3,4],[5,6]],name='weekday',labels=['weekday','weekend'])
    selection_weekday = alt.selection_point(fields=["weekday"])
    selection_month = alt.selection_multi(fields=["month"])
    w = 1000
    geo_view = plot_map(
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
    weather = weather_chart(
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
    calendar = calendar_chart(
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
    vehicles = vehicle_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
    )
    time_of_day = time_of_day_chart(
        accident_data,
        selection_buro,
        selection_acc_map,
        selection_cond,
        selection_month,
        selection_weekday,
        selection_vehicle,
        time_brush,
    )

    plot = (
        geo_view
        & (weather | calendar).resolve_scale(color="independent")
        & (vehicles | time_of_day)
    )
    return plot


# .configure_scale(bandPaddingInner=0)
plot = make_graph()
# make button to reset selection
st.button("Reset Selection")
st.altair_chart(plot)
