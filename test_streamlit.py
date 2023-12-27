from graphs import *
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="NYC Traffic Accidents")


# @st.cache_data
def get_data():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather2018.csv")
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
        "CONTRIBUTING FACTOR VEHICLE 1",
        "dayname",
        "monthname",
    ]

    # select only cols
    accident_data = accident_data[cols]
    return accident_data


# data = get_data()


# @st.cache_data
def get_graph(data):
    vis = make_visualization(data)
    return vis


# data = get_data()
# vis = get_graph(data)
data = get_accident_data(fname="dataset_v1.csv")
accident_data = get_weather_data(data)
print(accident_data.columns)
# vis = make_visualization(accident_data)
st.title("NYC Traffic Accidents")

colors = {"bg": "#eff0f3", "col1": "#d8b365", "col2": "#5ab4ac"}
w = 600
h = 400
ratio = 0.2

selection_cond = alt.selection_point(on="click", fields=["conditions"])
selection_acc_map = alt.selection_interval()
selection_buro = alt.selection_point(fields=["name"])
selection_vehicle = alt.selection_point(on="click", fields=["VEHICLE TYPE CODE 1"])

time_brush = alt.selection_point(fields=["HOUR"])

selection_weekday = alt.selection_point(fields=["dayname"])

# month_dropdown = alt.binding_select(
#     options=[
#         "June, July, August, September",
#         "June",
#         "July",
#         "August",
#         "September",
#     ],
#     name="month",
#     labels=["All", "June", "July", "August", "September"],
# )
selection_month = alt.selection_point(fields=["monthname"])
selection_acc_factor =  alt.selection_point(fields=["CONTRIBUTING FACTOR VEHICLE 1"])


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
]

accident_data = accident_data[cols]

w = 1000
geo_view, bur_chart = get_map_chart(
    accident_data,
    selection_cond,
    selection_buro,
    selection_acc_map,
    selection_month,
    selection_weekday,
    selection_vehicle,
    time_brush,
    selection_acc_factor,
    h1=600,
    h2=350,
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
    selection_acc_factor,
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
    selection_acc_factor,
    h=399,
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
    selection_acc_factor,
    h=399,
    w=w * 0.3,
)
# .configure_scale(
#     bandPaddingInner=.1).add_params(date_selector,month_selection, weekday_selection)

chart = geo_view & bur_chart & vehicles & weather & acc_factor & calendar & time_of_day
st.altair_chart(chart)
# st.altair_chart(vis, use_container_width=True)
print("done")

# make sidebar with instructions
# with st.sidebar:
#     if st.button("Reset graph (FOR DEVELOPMENT ONLY))"):
#         get_graph.clear_cache()
#     if st.button("Clear Selection"):
#         st.write("Clearing selection")
#     st.title("Instructions")
#     st.write(
#         """This app allows you to explore the relationship between weather and traffic accidents in NYC.
#          Throughout the visualization you can click on specific items in  order to select them, which will update the rest of the visualization to show only the data that matches your selection.
#          You can also hover over the data to see more information about it.
#          At the bottom of the graph, dropwdown menus are also included to further filter the data.
#         """
#     )
#     st.write(
#         "For further help, more detailed instructions on how to use it are available by going to the instructions page"
#     )
