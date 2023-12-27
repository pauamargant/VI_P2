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


data = get_data()


# @st.cache_data
def get_graph(data):
    vis = make_visualization(data)
    return vis


# data = get_data()
# vis = get_graph(data)
data = get_accident_data(fname="dataset_v1.csv")
accident_data = get_weather_data(data)
# vis = make_visualization(accident_data)
st.title("NYC Traffic Accidents")

# make count of VEHICLE TYPE CODE 1 altair chart
st.header("Count of Vehicle Type Code 1")
st.write(
    "This chart shows the count of the different types of vehicles involved in accidents in NYC in 2018. Hover over the bars to see the exact count of each vehicle type."
)
chart = (
    alt.Chart(accident_data)
    .mark_bar()
    .encode(
        x=alt.X("count()", title="Count"),
        y=alt.Y("VEHICLE TYPE CODE 1", title="Vehicle Type"),
        tooltip=["VEHICLE TYPE CODE 1", "count()"],
    )
)
# st.altair_chart(vis, use_container_width=True)
print("done")

# make sidebar with instructions
with st.sidebar:
    if st.button("Reset graph (FOR DEVELOPMENT ONLY))"):
        get_graph.clear_cache()
    if st.button("Clear Selection"):
        st.write("Clearing selection")
    st.title("Instructions")
    st.write(
        """This app allows you to explore the relationship between weather and traffic accidents in NYC.
         Throughout the visualization you can click on specific items in  order to select them, which will update the rest of the visualization to show only the data that matches your selection.
         You can also hover over the data to see more information about it.
         At the bottom of the graph, dropwdown menus are also included to further filter the data.
        """
    )
    st.write(
        "For further help, more detailed instructions on how to use it are available by going to the instructions page"
    )
