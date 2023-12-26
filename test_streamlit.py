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


data = get_data()
vis = get_graph(data)
st.title("NYC Traffic Accidents")
st.write(vis)
print("done")

# make sidebar with instructions
with st.sidebar:
    if st.button("Reset graph (FOR DEVELOPMENT ONLY))"):
        get_graph.clear()
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
